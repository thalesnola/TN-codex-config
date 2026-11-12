<!-- BEGIN CONFIDENTIALITY-POLICY -->
## SIGILO LOCAL PRIORITARIO - prevalece sobre o roteamento

Dados de caso somente podem ser processados e revisados por executor local (Ollama, Qwen Code, DSH ou OpenCode) ou pela propria sessao principal autorizada. Nenhum subagente ou modelo em nuvem pode receber dados de caso, inclusive nomes, caminhos ou trechos; nada disso entra em prompts de `codex exec`. Nao existe aprovacao que dispense esta regra. Dados de caso e artefatos derivados permanecem somente em pastas locais de caso. Instrucoes mais restritivas de projeto prevalecem.

O roteador CLI e consultivo e nao concede liberacao de sigilo. Overrides explicitos podem mudar modelo/esforco, mas nao afastam esta regra de sigilo. Estas instrucoes sao comportamentais e nao prometem bloqueio tecnico.
<!-- END CONFIDENTIALITY-POLICY -->

# Roteamento por metadados

O padrão inicial global é Luna `gpt-6-luna` com esforço `low`, responsável por tarefas simples e coordenação. Luna aciona Astra `gpt-6-astra` low para planejamento substancial e arquitetura, recebendo recomendações compactas. A execução cloud usa os agentes nativos standalone em `~/.codex/agents/`: Astra planejador, Sol executor, Sol revisor, Luna triagem e Terra visual, todos low. O padrão de subagente também é Luna low. A política completa está em `~/.codex/AGENTS.md`.

No JSON do roteiro, `agent=controller` significa que a Luna principal executa a tarefa sem abrir subagente. Isso cobre buscas, extrações, resumos, triagem e código pequeno delimitado. `luna-triage` fica disponível para trabalho paralelo quando houver benefício claro.

O roteador Python não despacha tarefas. Ele retorna JSON determinístico com agente, modelo, destino e motivo usando somente metadados. Não aceita prompts, não abre casos ou arquivos de entrada e não chama rede/modelos. `dispatched` é sempre `false`; disponibilidade e configuração dos modelos locais precisam ser verificadas pelo executor. A fila serial é uma exigência de execução, não um lock implementado aqui.

```powershell
python ~/.codex/local-router/route.py --task implementation --complexity complex
python ~/.codex/local-router/route.py --task visual --dry-run
python ~/.codex/local-router/route.py --task implementation --complexity small --scope local
python ~/.codex/local-router/route.py --task batch --items 5 --scope local
python ~/.codex/local-router/route.py --task planning --restricted
python -m unittest discover -s ~/.codex/local-router/tests -v
```

Tipos: `planning`, `architecture`, `implementation`, `testing`, `debug`, `review`, `triage`, `extraction`, `batch`, `visual`, `writing`, `computer-use`, `investigation`, `search`, `summarization`. Complexidade: `small`, `medium` (padrão), `complex`. `--items N` é positivo; `--files`, `--total-bytes` e `--largest-file-bytes` são inteiros não negativos, padrão zero (metadado não informado). Se total e maior arquivo forem ambos conhecidos e positivos, maior arquivo não pode exceder o total; entrada incoerente é rejeitada. `--input-kind text|binary` tem padrão `text`; o chamador deve marcar PDFs, scans e outros binários como `binary`. Destino: `--scope auto|local|cloud`.

Aplique SIGILO LOCAL PRIORITARIO antes de usar qualquer recomendacao. As selecoes cloud abaixo se aplicam somente ao contexto que essa regra permite receber; uma resposta do CLI nao autoriza acesso, processamento ou envio. Kimi continua fora. `--restricted` e `--acervo-authorized` permanecem aceitos por compatibilidade, são ignorados e aparecem em `compatibility_flags_ignored`; não classificam conteúdo, não bloqueiam nem forçam destino. `--acervo` indica que o usuário já forneceu/indicou a coleção para a tarefa e favorece OpenCode para investigação em auto. Não concede acesso a outras pastas nem autoriza varrer acervos. Nenhuma consulta do roteador lê fonte ou credencial.

Em `auto`, texto processável com total >=1 MiB, maior arquivo >=512 KiB ou >=5 arquivos/itens em tarefa mecânica (busca, extração, triagem, sumarização, lote) prefere local. Os limites inclusivos ficam em `policy.json/local_first`: são pontos de partida ajustáveis, não benchmarks. Bytes armazenados não equivalem a tokens, contexto ou garantia de capacidade. O executor divide texto em chunks/lotes, produz índices/resumos locais e retorna resultado compacto. Artefatos ficam no disco; não se deve injetar todo volume na cloud. `preparation=local_chunking_or_index` e `cloud_input=compact_summary_only` exigem a etapa local anterior e entrada cloud somente compacta. `compact_context_required` informa essa necessidade inclusive quando `--scope cloud` explícito prevalece sobre a preferência de volume.

Luna consulta Astra para planejamento/arquitetura em auto, mesmo com grande volume, recebendo somente contexto compacto. Revisão, visual, documentos e computer use também mantêm sua especialidade cloud para a etapa final, após preparação local do volume. Local explícito para essas tarefas retorna `unsupported`: não existe Astra local configurado. Revisão crítica local sem executor retorna `unsupported`, assim como UI/computer use sem executor adequado. Não há fallback cloud automático. `cloud_forbidden` representa somente a escolha explícita `--scope local` por economia; não é classificação de sensibilidade nem barreira técnica de rede. Uma nova escolha cloud continua subordinada a SIGILO LOCAL PRIORITARIO; nem flags nem justificativas dispensam a regra.

Código pequeno local seleciona DSH `gpt-oss:20b`; tarefas delimitadas de código, busca, extração, sumarização e lotes selecionam Qwen `hf.co/unsloth/Qwen3-Coder-Next-GGUF:NOTPL`. Qwen não recebe tudo em um prompt: exige chunks/índices locais. Investigação local seleciona OpenCode `nemotron-3.5-lightning:30b-a3b` no escopo indicado. Complexidade complex sem executor local configurado retorna `unsupported`. Para contexto permitido pela regra de sigilo, a revisao independente/integracao critica permanece com Sol conforme capacidade.

`--input-kind binary` retorna `needs_preprocessing`, destino local e modelo ausente, para preparar extração/OCR local em lotes quando necessário e reconsultar com metadados do texto extraído. Isso não confirma ferramenta instalada, não lê bytes e não delega binário bruto a modelo. Originais devem ser lidos sem alteração; transformações vão para cópias/área de trabalho, sem exigir duplicação integral só para leitura.

```powershell
python ~/.codex/local-router/route.py --task extraction --total-bytes 1048576
python ~/.codex/local-router/route.py --task summarization --largest-file-bytes 524288
python ~/.codex/local-router/route.py --task investigation --acervo
python ~/.codex/local-router/route.py --task extraction --input-kind binary --files 10
```

Antes de executar pesos locais, verificar disponibilidade, contexto efetivo >=32768, flash attention e KV q8_0; manter somente um modelo grande carregado, sem download automático nem num_gpu=0. Não reduzir modelo automaticamente por VRAM: relatar limite e reavaliar etapa. Revisar resultados/diff e validar proporcionalmente. A fila serial e essas verificações são exigências comportamentais, não funcionalidades do roteador. Nenhum peso é baixado ou carregado.

Para executar, o orquestrador usa o papel customizado nativo se `agent_type` estiver disponível. Se o schema não expuser o papel customizado, use `fork_turns="none"`, modelo explícito, `reasoning_effort="low"` e instruções/contexto do papel. Fork completo herda o modelo do pai; use contexto novo e modelo explícito para selecionar outro especialista. Workers não delegam por padrão. O revisor recebe contexto separado do autor.

As instruções são comportamentais: não são um bloqueio técnico de ferramentas, dados ou rede. A configuração não troca sessões abertas retroativamente; escolhas explícitas de UI/projeto/chamada podem prevalecer. Os agentes cloud compartilham os limites da conta. Não há subprocesso recursivo de Codex ou controlador local completo instalado.

Schema e referência: [subagentes oficiais](https://learn.chatgpt.com/docs/agent-configuration/subagents). A configuração foi validada com Codex Doctor `0.165.0-alpha.1.2`; os papéis standalone ficam em `~/.codex/agents/*.toml`. Não há registros duplicados de papéis em config.toml.
