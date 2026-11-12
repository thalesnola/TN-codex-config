[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$TaskFile,
    [string]$ArtifactRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'artifacts')
)

$ErrorActionPreference = 'Stop'

function Fail([string]$Message) { throw "PRECHECK FAILED: $Message" }

if (-not (Test-Path -LiteralPath $TaskFile -PathType Leaf)) { Fail "task file not found: $TaskFile" }
try { $task = Get-Content -Raw -LiteralPath $TaskFile | ConvertFrom-Json } catch { Fail "invalid JSON task manifest" }

$required = 'id','classification','operation','worker','model','workspace','objective','acceptance'
foreach ($field in $required) {
    if ([string]::IsNullOrWhiteSpace([string]$task.$field)) { Fail "missing required field: $field" }
}
# Vocabulário fechado: classificação desconhecida (ex.: typo de 'evidence') nunca cai no caminho permissivo.
if ($task.classification -notin @('public','internal','evidence')) { Fail "unknown classification: $($task.classification) (allowed: public, internal, evidence)" }
# id vira nome de arquivo: só nome simples, sem separador nem '..'.
if ([string]$task.id -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$' -or [string]$task.id -match '\.\.') { Fail "invalid task id (simple name only): $($task.id)" }
# O mesmo caminho em include e exclude é contradição: recusar em vez de deixar o prompt ambíguo.
$overlap = @($task.include | Where-Object { $_ -and ($task.exclude -contains $_) })
if ($overlap.Count) { Fail "path listed in both include and exclude: $($overlap -join ', ')" }
if ($task.classification -eq 'evidence' -and $task.worker -ne 'opencode') {
    Fail "evidence tasks must use worker=opencode"
}
if ($task.worker -notin @('qwen-ollama','opencode')) { Fail "unsupported local worker: $($task.worker)" }
if (-not (Test-Path -LiteralPath $task.workspace -PathType Container)) { Fail "workspace not found: $($task.workspace)" }

$runtime = if ($task.worker -eq 'opencode') { Get-Command opencode -ErrorAction SilentlyContinue } else { Get-Command qwen -ErrorAction SilentlyContinue }
if (-not $runtime) { Fail "required CLI is not on PATH for worker $($task.worker)" }

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) { Fail 'ollama is not on PATH' }
try { $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5 } catch { Fail 'Ollama API is offline at 127.0.0.1:11434' }
if ($tags.models.name -notcontains $task.model) { Fail "Ollama model is not installed: $($task.model)" }

$loaded = @()
try { $loaded = @((Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/ps' -TimeoutSec 5).models.name) } catch { Write-Warning 'Ollama /api/ps failed: resident models unknown; check `ollama ps` before dispatching.' }
$others = @($loaded | Where-Object { $_ -and $_ -ne $task.model })
if ($others.Count) {
    Write-Warning "Other Ollama model(s) resident ($($others -join ', ')); unload them (ollama stop) and do not dispatch local work in parallel."
}

New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
$promptPath = Join-Path $ArtifactRoot "$($task.id)-prompt.md"
# Contenção: o destino absoluto tem de ficar dentro do ArtifactRoot.
$rootFull = [IO.Path]::GetFullPath($ArtifactRoot).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
if (-not [IO.Path]::GetFullPath($promptPath).StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)) { Fail "prompt path escapes ArtifactRoot: $promptPath" }
$include = ($task.include | ForEach-Object { "- $_" }) -join "`n"
$exclude = ($task.exclude | ForEach-Object { "- $_" }) -join "`n"
$acceptance = ($task.acceptance | ForEach-Object { "- $_" }) -join "`n"
@"
# Local task: $($task.id)

Worker: $($task.worker)
Model: $($task.model)
Workspace: $($task.workspace)
Operation: $($task.operation)

## Objective
$($task.objective)

## Include
$include

## Exclude — never read or send
$exclude

## Acceptance
$acceptance

Return a compact artifact only: files examined/touched, path:line facts, verification commands/results, and unresolved gaps. Do not return raw dumps. Do not make architectural decisions.
"@ | Set-Content -LiteralPath $promptPath -Encoding utf8

[pscustomobject]@{
    status = 'ready-for-manual-local-dispatch'
    task = $task.id
    worker_cli = $runtime.Source
    model = $task.model
    prompt = $promptPath
    loaded_models = @($loaded)
} | ConvertTo-Json -Depth 4
