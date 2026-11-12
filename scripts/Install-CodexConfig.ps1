[CmdletBinding(SupportsShouldProcess)]
param([string]$Destination = (Join-Path $env:USERPROFILE '.codex'))
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path $PSScriptRoot -Parent
$destinationFull = [IO.Path]::GetFullPath($Destination)
function Get-LocalFileSha256([string]$LiteralPath) {
    $stream = [IO.File]::OpenRead($LiteralPath)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '')
    } finally {
        $stream.Dispose()
        $hasher.Dispose()
    }
}
# Validate every policy source before ShouldProcess or any filesystem mutation.
# This preflight is native PowerShell 5.1 and does not require Python.
$policyFile = Join-Path $sourceRoot 'policy/confidentiality.md'
$policyText = [IO.File]::ReadAllText($policyFile).Replace("`r`n", "`n").Trim()
$sha256 = [Security.Cryptography.SHA256]::Create()
try {
    $policyHash = [BitConverter]::ToString($sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($policyText))).Replace('-', '').ToLowerInvariant()
} finally { $sha256.Dispose() }
if ($policyHash -ne '92c666e3212afc1810201598846d4bd8c336382938c50f29ef3ad87d23564148') {
    throw 'Confidentiality policy integrity check failed.'
}
$agentNames = @('astra-planner', 'luna-triage', 'sol-executor', 'sol-reviewer', 'terra-visual')
$agentFiles = @(Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'agents') -Filter '*.toml' -File)
if ($agentFiles.Count -ne $agentNames.Count) { throw 'Expected exactly five policy-protected agents.' }
$policyConsumers = @('AGENTS.md', 'skills/codex-token-router/SKILL.md', 'local-router/README.md', 'profiles/acervo-conhecimento/AGENTS.md', 'profiles/redacao-forense/AGENTS.md')
$policyConsumers += $agentNames | ForEach-Object { 'agents/' + $_ + '.toml' }
$contradictions = @('dispon[i\u00ed]veis a qualquer modelo', 'podem ser processados por qualquer modelo', 'podem ser usados por modelos adequados', 'podem ser usados pelos modelos adequados', 'autorizados aos modelos adequados', 'sem bloqueio por categoria restrita', 'sem nova barreira por categoria')
foreach ($relative in $policyConsumers) {
    $content = [IO.File]::ReadAllText((Join-Path $sourceRoot $relative)).Replace("`r`n", "`n")
    if (-not $content.Contains($policyText)) { throw "Missing or altered confidentiality policy: $relative" }
    if ($relative.StartsWith('agents/')) {
        $instructions = [regex]::Match($content, '(?s)developer_instructions\s*=\s*"""(.*?)"""')
        if (-not $instructions.Success -or -not $instructions.Groups[1].Value.Contains($policyText)) {
            throw "Confidentiality policy must be inside developer_instructions: $relative"
        }
    }
    foreach ($pattern in $contradictions) {
        if ($content -match $pattern) { throw "Contradictory confidentiality permission: $relative" }
    }
}
if (Test-Path -LiteralPath (Join-Path $destinationFull 'AGENTS.override.md')) {
    throw 'Existing AGENTS.override.md would hide the installed AGENTS.md. Resolve it before installation.'
}
$backupRoot = Join-Path $destinationFull ('backups/codex-config-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [Guid]::NewGuid().ToString('N'))
$paths = @('AGENTS.md', 'agents', 'local-router', 'skills/codex-token-router', 'policy/confidentiality.md')
foreach ($relative in $paths) {
    $source = Join-Path $sourceRoot $relative
    if (Test-Path -LiteralPath $source -PathType Container) {
        $files = Get-ChildItem -LiteralPath $source -File -Recurse -Force | Where-Object {
            $_.Extension -ne '.pyc' -and $_.FullName -notmatch '[\\/]__pycache__([\\/]|$)'
        }
    } else {
        $files = @(Get-Item -LiteralPath $source)
    }
    foreach ($file in $files) {
        $fileRelative = $file.FullName.Substring($sourceRoot.Length).TrimStart([char[]]'\/')
        $target = Join-Path $destinationFull $fileRelative
        if ($PSCmdlet.ShouldProcess($target, 'Back up and install configuration file')) {
            if (Test-Path -LiteralPath $target) {
                if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Destination is not a file: $target" }
                $backup = Join-Path $backupRoot $fileRelative
                New-Item -ItemType Directory -Force -Path (Split-Path $backup -Parent) | Out-Null
                $originalHash = Get-LocalFileSha256 $target
                Copy-Item -LiteralPath $target -Destination $backup
                $backupHash = Get-LocalFileSha256 $backup
                if ($originalHash -ne $backupHash) { throw "Backup verification failed for: $target" }
            }
            New-Item -ItemType Directory -Force -Path (Split-Path $target -Parent) | Out-Null
            Copy-Item -LiteralPath $file.FullName -Destination $target -Force
        }
    }
}
Write-Output 'config.toml preserved. Review config/config.toml.example separately. Open a new session to reload instructions.'
