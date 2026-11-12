---
name: codex-token-router
description: Escolha de papéis Codex e preparação local por metadados para controlar volume, custo e contexto em tarefas que exigem delegação ou processamento em lotes.
---

<!-- BEGIN CONFIDENTIALITY-POLICY -->
## SIGILO LOCAL PRIORITARIO - prevalece sobre o roteamento

Dados de caso somente podem ser processados e revisados por executor local (Ollama, Qwen Code, DSH ou OpenCode) ou pela propria sessao principal autorizada. Nenhum subagente ou modelo em nuvem pode receber dados de caso, inclusive nomes, caminhos ou trechos; nada disso entra em prompts de `codex exec`. Nao existe aprovacao que dispense esta regra. Dados de caso e artefatos derivados permanecem somente em pastas locais de caso. Instrucoes mais restritivas de projeto prevalecem.

O roteador CLI e consultivo e nao concede liberacao de sigilo. Overrides explicitos podem mudar modelo/esforco, mas nao afastam esta regra de sigilo. Estas instrucoes sao comportamentais e nao prometem bloqueio tecnico.
<!-- END CONFIDENTIALITY-POLICY -->

# Roteamento Codex

Use a política global em `~/.codex/AGENTS.md`; os modelos e limiares ficam em `~/.codex/local-router/policy.json`.

| Trabalho | Papel | Modelo / esforço |
| --- | --- | --- |
| Sessão inicial e coordenação | Luna, despacha especialistas por necessidade | gpt-6-luna / low |
| Planejamento e arquitetura por demanda | astra-planner, devolve decisões à Luna | gpt-6-astra / low |
| Código, integração, testes e depuração complexa | sol-executor | gpt-6.1-sol / low |
| Revisão independente em contexto separado | sol-reviewer | gpt-6.1-sol / low |
| Busca focada, extração delimitada e triagem pequena | Luna principal ou luna-triage | gpt-6-luna / low |
| UI, computer use, visual, documentos e redação | terra-visual | gpt-6.1-terra / low |

Não eleve esforço automaticamente. Prefira `agent_type` quando disponível. Se o schema não expuser o papel, use `fork_turns="none"`, modelo explícito, esforço low e contexto compacto com as instruções do papel. Workers não delegam por padrão. O autor não aprova sua própria alteração.

O controlador Luna executa tarefas simples diretamente. No roteiro por metadados, `agent=controller` indica que não é necessário abrir subagente; use `luna-triage` somente quando uma triagem paralela delimitada ajudar.

Antes de conteúdo volumoso, meça somente metadados e consulte, por exemplo:

```powershell
python ~/.codex/local-router/route.py --task extraction --total-bytes 1048576 --files 5 --dry-run
```

O CLI é consultivo: não lê fontes, não verifica disponibilidade, não carrega modelos e nunca despacha (`dispatched=false`). Em auto, texto >=1 MiB, maior arquivo >=512 KiB ou >=5 itens mecânicos pede preparação local em chunks/lotes/índice e retorno compacto. PDF/binário pede extração/OCR local antes de selecionar modelo para o texto.

DSH/gpt-oss:20b atende código pequeno; Qwen3-Coder-Next:NOTPL atende código delimitado, buscas, extração, resumos e lotes; OpenCode/nemotron-3.5-lightning:30b-a3b atende investigação do acervo indicado. Kimi está fora. Confirme disponibilidade e adequação antes de executar. Local explícito sem executor adequado retorna unsupported, sem fallback silencioso.

Execute pesos locais em série, com contexto efetivo >=32768, flash attention e KV q8_0. Não baixe modelos automaticamente, não force num_gpu=0 nem carregue dois modelos grandes. Preserve originais documentais e mantenha artefatos no disco. Revise diff/coerência e valide o resultado antes de aceitar.

Aplique SIGILO LOCAL PRIORITARIO antes de qualquer despacho. A indicacao de dados pelo usuario nao afasta sigilo nem autoriza outros acervos, credenciais, apps externos ou publicacao. Não leia C:/ACERVO, Segundo_Cerebro ou Casos sem indicação para a tarefa.

Configuração e instruções são comportamentais, não barreiras técnicas. Overrides explícitos de sessão/projeto/UI podem prevalecer; os agentes compartilham os limites da conta. Estimativas não são medições de tokens.

## Despacho Local e Preflight Endurecido

Para tarefas locais (`dsh-local`, `qwen-local`, `opencode-local`), utilize o despachante com lock serial e pré-verificação endurecida:

```powershell
./local-preflight/scripts/Invoke-LocalFirstWorker.ps1 -TaskFile <manifesto.json> -WorkerAction {
    param($ready, $task)
    # Executa o comando local aprovado
}
```

O preflight em `local-preflight/scripts/Test-LocalFirstPreflight.ps1` valida boundaries do workspace, rejeita symlinks/reparse points, impede escape de diretório e verifica modelos residentes no Ollama (`NUM_PARALLEL=1`).

## Ponte opcional Codex -> AGY / Gemini

Para tarefas autorizadas no AGY, consulte a integração `thalesnola/codex-agy` (pública: `TN-codex-agy`) e sua skill correspondente. O AGY local chama modelos Gemini em nuvem: a regra SIGILO LOCAL PRIORITARIO também se aplica aos prompts, caminhos e snapshots dessa ponte. Não encaminhe dados de caso; ela não é um executor local de pesos.

O controlador conserva objetivo, escopo, critérios de aceite, acompanhamento, revisão e aceitação. Confirme `argon_status` e `argon_models`, escolha somente Gemini autorizado e envie tarefas compactas com `inputs`/`owns` delimitados. Nenhum fallback para Claude ou Anthropic. Leia resposta e patch, valide a base e os testes antes de integrar e aceitar o job. O roteiro por metadados continua consultivo e não despacha AGY. Consulte `docs/agy-gemini.md` no repositório canônico para instalação e sondas sintéticas.
