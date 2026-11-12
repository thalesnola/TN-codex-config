$repo = Split-Path $PSScriptRoot -Parent
$task = Join-Path $repo 'examples\task.local-analysis.json'
$script = Join-Path $repo 'scripts\Test-LocalFirstPreflight.ps1'

$text = Get-Content -Raw -LiteralPath $script
if ($text -notmatch "evidence tasks must use worker=opencode") { throw 'Missing evidence routing gate' }
if ($text -notmatch "api/tags") { throw 'Missing Ollama model verification' }
if ($text -notmatch "ready-for-manual-local-dispatch") { throw 'Missing explicit non-executing status' }

try { Get-Content -Raw -LiteralPath $task | ConvertFrom-Json | Out-Null } catch { throw 'Example manifest is not valid JSON' }
Write-Output 'PASS: static preflight gates and example manifest validated'

# --- Comportamento (30/09/2026): casos que a auditoria mostrou aceitos indevidamente. Exige Ollama no ar.
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("preflight-test-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
$base = Get-Content -Raw -LiteralPath $task | ConvertFrom-Json
function Expect-Fail($name, $mutate) {
    $t = $base | ConvertTo-Json -Depth 6 | ConvertFrom-Json
    & $mutate $t
    $f = Join-Path $tmp "$name.json"; $t | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $f -Encoding utf8
    try { & $script -TaskFile $f -ArtifactRoot (Join-Path $tmp 'art') | Out-Null; throw "ACCEPTED: $name" }
    catch { if ($_.Exception.Message -notmatch 'PRECHECK FAILED') { throw } }
}
Expect-Fail 'classificacao-desconhecida' { param($t) $t.classification = 'evdience' }
Expect-Fail 'id-com-traversal'          { param($t) $t.id = '../escaped' }
Expect-Fail 'include-e-exclude'         { param($t) $t.include = @('C:\x'); $t.exclude = @('C:\x') }
if (Test-Path (Join-Path $tmp 'escaped-prompt.md')) { throw 'wrote outside ArtifactRoot' }
Remove-Item -Recurse -Force $tmp
Write-Output 'PASS: behavioral preflight gates (classification, id, include/exclude)'
