[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$TaskFile,
    [Parameter(Mandatory)] [scriptblock]$WorkerAction,
    [string]$ArtifactRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'artifacts')
)
$ErrorActionPreference = 'Stop'
# O lock precisa abranger a execucao, nao apenas a verificacao anterior.
$mutex = [Threading.Mutex]::new($false, 'Local\CodexLocalFirstWorker')
$owned = $false
try {
    try { $owned = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $owned = $true }
    if (-not $owned) { throw 'Local worker already running; dispatch refused.' }
    $preflight = & "$PSScriptRoot\Test-LocalFirstPreflight.ps1" -TaskFile $TaskFile -ArtifactRoot $ArtifactRoot
    $ready = $preflight | ConvertFrom-Json
    $task = Get-Content -LiteralPath $TaskFile -Raw | ConvertFrom-Json
    $global:LASTEXITCODE = 0
    & $WorkerAction $ready $task
    if ($LASTEXITCODE -ne 0) { throw "Local worker failed: exit $LASTEXITCODE" }
} finally {
    if ($owned) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
