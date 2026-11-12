$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$script = Join-Path $repo 'scripts\Test-LocalFirstPreflight.ps1'
$tmp = Join-Path ([IO.Path]::GetTempPath()) ('codex-preflight-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
Set-Content (Join-Path $tmp 'input.txt') 'synthetic'
$base = @{id='synthetic-test';classification='internal';operation='analyze';worker='qwen-ollama';model='synthetic:latest';workspace=$tmp;include=@('input.txt');exclude=@('secrets');objective='Synthetic tests';acceptance=@('No changes')}
function Invoke-RestMethod {
    param($Uri, $TimeoutSec)
    if ($Uri -like '*/tags') { return @{models=@(@{name='synthetic:latest'})} }
    return @{models=@(@{name=$global:codexTestResident})}
}
$global:codexTestResident = 'synthetic:latest'
function Check($name, $mutate, $expectFailure) {
    $t = $base | ConvertTo-Json -Depth 5 | ConvertFrom-Json
    & $mutate $t
    $file = Join-Path $tmp 'task.json'
    $t | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $file -Encoding UTF8
    $failed = $false
    try { & $script -TaskFile $file -ArtifactRoot (Join-Path $tmp 'art') | Out-Null }
    catch { if ($_.Exception.Message -notmatch 'PRECHECK FAILED') { throw }; $failed=$true }
    if ($failed -ne $expectFailure) { throw "Unexpected result: $name" }
    Write-Output "PASS: $name"
}
try {
    Check 'valid' {} $false
    Check 'missing include' {param($t) $t.include=$null} $true
    Check 'missing exclude' {param($t) $t.exclude=@()} $true
    Check 'unknown operation' {param($t) $t.operation='unknown'} $true
    Check 'ingestion requires opencode' {param($t) $t.operation='ingest'} $true
    Check 'escape' {param($t) $t.include=@('..\outside')} $true
    Check 'normalized overlap' {param($t) $t.exclude=@('.\INPUT.txt')} $true
    $global:codexTestResident='other:latest'
    Check 'other resident model' {} $true
} finally {
    Remove-Variable codexTestResident -Scope Global -ErrorAction SilentlyContinue
    $resolved = [IO.Path]::GetFullPath($tmp)
    if (-not $resolved.StartsWith([IO.Path]::GetTempPath(), [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolved -Leaf) -notlike 'codex-preflight-*') { throw 'Unsafe cleanup path' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
