# Local-First Preflight & Worker Dispatcher

Motor endurecido de pré-verificação e despacho serial de tarefas locais no Codex.

## Componentes

- scripts/Invoke-LocalFirstWorker.ps1: Despacha tarefas para o worker local sob lock atômico de exclusão mútua (Local\\CodexLocalFirstWorker), garantindo que apenas um executor local rode por vez.
- scripts/Test-LocalFirstPreflight.ps1: Valida boundaries do workspace, rejeita symlinks/reparse points, impede escape de diretório e verifica modelos residentes no Ollama para evitar colisão de memória.
- 	ests/Test-HardenedPreflight.ps1: Suíte de validação com testes de conformidade para o preflight endurecido.
- examples/task.local-analysis.json: Exemplo de manifesto JSON de tarefa local.

## Uso

`powershell
.\local-preflight\scripts\Invoke-LocalFirstWorker.ps1 -TaskFile .\local-preflight\examples\task.local-analysis.json -WorkerAction {
    param(, )
    # Executa o comando local aprovado
}
`
