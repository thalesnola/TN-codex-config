<!-- BEGIN CONFIDENTIALITY-POLICY -->
## SIGILO LOCAL PRIORITARIO - prevalece sobre o roteamento

Dados de caso somente podem ser processados e revisados por executor local (Ollama, Qwen Code, DSH ou OpenCode) ou pela propria sessao principal autorizada. Nenhum subagente ou modelo em nuvem pode receber dados de caso, inclusive nomes, caminhos ou trechos; nada disso entra em prompts de `codex exec`. Nao existe aprovacao que dispense esta regra. Dados de caso e artefatos derivados permanecem somente em pastas locais de caso. Instrucoes mais restritivas de projeto prevalecem.

O roteador CLI e consultivo e nao concede liberacao de sigilo. Overrides explicitos podem mudar modelo/esforco, mas nao afastam esta regra de sigilo. Estas instrucoes sao comportamentais e nao prometem bloqueio tecnico.
<!-- END CONFIDENTIALITY-POLICY -->

# Instruções globais do usuário

<!-- BEGIN SETUP-CLAUDE-ADAPTADO -->
## Preferências globais adaptadas para Codex
- Responder em português brasileiro, salvo pedido diferente. No Windows, usar PowerShell compatível com 5.1; não usar && sem selecionar explicitamente PowerShell 7.
- Preferir os recursos nativos do Codex para navegador, arquivos, GitHub, revisão e memória do projeto; Context7 para documentação de bibliotecas. Não chamar comandos /plugin, /effort ou subagentes token-router:* do Claude como se existissem no Codex.
- Skills de uso diário podem estar em ~/.agents/skills ou no catálogo disponível: redacao-forense, consulta-juridica, graphify, archify, humanizer, find-skills, apple-hig-designer e redesign-existing-projects. Ler SKILL.md quando a tarefa se enquadrar. Resolver scripts e referências a partir da pasta da skill. Adaptar nomes de ferramentas Claude aos recursos disponíveis no Codex; não alegar equivalência quando faltar capacidade.
- Para consulta jurídica, usar a base pública C:/LegalRef quando disponível e conferir vigência e citações nas fontes oficiais antes de entregar peça. Não tratar o resultado local como validação de pertinência jurídica.
- Não acessar, indexar, clonar ou enviar C:/ACERVO ou Segundo_Cerebro quando não indicados pelo usuário para a tarefa; indicação na tarefa é a autorização, sem novo consentimento rotineiro. A instalação das skills não autoriza leitura do acervo. Não executar hooks do Segundo Cérebro automaticamente.
- Nunca expor tokens, senhas, chaves privadas, .env ou .credentials.json. Antes de commit, revisar o diff staged e os nomes de arquivos para impedir inclusão de credenciais; isso é instrução de comportamento, não substitui hook técnico de bloqueio.
- Trabalho de modelos locais exige revisão do diff, coerência e validação apropriada antes de ser considerado concluído. Só usar executores locais quando disponíveis e adequados à tarefa. Aplicar a regra SIGILO LOCAL PRIORITARIO acima; indicacao do usuario nao libera dados de caso para modelos em nuvem.
- Ao executar Ollama para tarefas autorizadas, conferir contexto de pelo menos 32768, flash attention e KV cache q8_0; não forçar num_gpu=0 nem carregar dois modelos grandes simultaneamente. Não baixar modelos grandes automaticamente.
- Plugins e skills de mídia/3D são opcionais. Os pacotes Higgsfield e Hyperframes foram mantidos instalados com skills desativadas por padrão; reativar somente quando houver necessidade. Antes de instalar skills de terceiros, examinar código e comandos; popularidade não comprova segurança.
<!-- END SETUP-CLAUDE-ADAPTADO -->

<!-- BEGIN CODEX-MODEL-ROUTING -->
## Roteamento global de modelos e papéis

- O modelo inicial e controlador padrão é Luna (`gpt-6-luna`) com esforço `low`. Luna recebe o pedido, identifica escopo, volume, risco e especialidade, executa tarefas simples e coordena especialistas quando necessário. Esta política autoriza delegação nativa sem confirmação rotineira.
- Mantenha o trabalho na Luna para conversa, triagem, buscas focadas, extração delimitada, classificação, lotes simples e correções pequenas com critérios claros. Se a tarefa crescer, despache apenas o trecho que exige capacidade maior, com contexto compacto, e integre o resultado no chat principal.
- Planejamento substancial, arquitetura, raciocínio profundo ou investigação ambígua: Luna consulta Astra (`astra-planner`, `gpt-6-astra`, `low`) com decisão delimitada. Astra recomenda critérios e riscos à Luna; não escreve artefatos nem assume execução operacional.
- Código complexo, integrações, implementação, testes e depuração: `sol-executor` (`gpt-6.1-sol`, `low`). Revisão independente de alterações relevantes: `sol-reviewer` em outra instância/contexto; o autor não aprova sua própria alteração.
- UI, computer use, trabalho visual, documentos e redação: `terra-visual` (`gpt-6.1-terra`, `low`). Luna pode realizar tarefas textuais simples sem despacho. O papel `luna-triage` (`gpt-6-luna`, `low`) atende triagem paralela delimitada quando ela for útil.
- Workers executam o escopo recebido e não criam outros agentes por padrão. Devolvem decisões pendentes e evidências à Luna, que pode consultar Astra ou encaminhar a outro especialista. Não aumente esforço automaticamente. Agentes cloud compartilham os limites da conta; delegação não garante economia.

### Despacho nativo e compatibilidade

- Configuração global: `~/.codex/config.toml`, com `model = "gpt-6-luna"`, `model_reasoning_effort = "low"` e `[agents] default_subagent_model = "gpt-6-luna"`, `default_subagent_reasoning_effort = "low"`. Os cinco papéis ficam em `~/.codex/agents/*.toml`; a CLI instalada descobre esses arquivos standalone.
- Prefira `agent_type` para aplicar o papel customizado. Se o schema disponível não expuser o papel, use `fork_turns="none"`, modelo e esforço explícitos, copiando as instruções relevantes e apenas contexto necessário. Fork completo herda o modelo do controlador e não seleciona outro especialista. Os papéis especializados têm precedência sobre o modelo padrão de subagente quando explicitamente selecionados.
- Overrides explícitos de UI, projeto, perfil ou chamada podem prevalecer; o padrão não troca sessões abertas retroativamente. Agentes herdam permissões, provedor e MCP do pai. Não crie subprocessos recursivos de Codex para simular delegação.

### Prioridade local por volume

- Aplicar a regra SIGILO LOCAL PRIORITARIO acima; indicacao do usuario nao libera dados de caso para modelos em nuvem. Isso não amplia o escopo para apps externos, credenciais ou acervos não indicados. C:/ACERVO, Segundo_Cerebro e Casos exigem indicação na tarefa; Kimi continua fora.
- Antes de ler entradas volumosas, meça metadados no escopo indicado: tamanho total, maior arquivo, quantidade e tipo. Em auto, texto processável com total >=1 MiB, maior arquivo >=512 KiB ou >=5 itens mecânicos favorece preparação local em chunks/lotes/índice, com artefatos no disco e resumo curto. Bytes em disco não equivalem a tokens. Não injete grandes volumes brutos no contexto cloud; revise os resumos locais antes de aceitar.
- DSH com `gpt-oss:20b`: código pequeno. Qwen com `hf.co/unsloth/Qwen3-Coder-Next-GGUF:NOTPL`: código delimitado, busca, extração, sumarização e lotes. OpenCode com `nemotron-3.5-lightning:30b-a3b`: investigação em acervo indicado. Verifique disponibilidade e adequação. Local explícito sem executor adequado retorna `unsupported`, sem fallback silencioso.
- Binários, PDFs e scans exigem extração/OCR local em lotes quando necessário; reconsulte o roteiro com metadados do texto. Preserve originais e grave transformações em cópias/área de trabalho.
- Execute pesos locais em série. Antes de Ollama, confira contexto efetivo >=32768, flash attention e KV q8_0; não force `num_gpu=0`, não baixe modelos grandes automaticamente nem mantenha dois grandes carregados. Revise diff, coerência e validação proporcional antes de aceitar resultados locais.
- Consulta determinística: `python "$env:USERPROFILE/.codex/local-router/route.py" --task extraction --total-bytes 1048576 --files 5 --dry-run`. Passe apenas metadados, sem conteúdo ou credenciais. O roteiro é consultivo: não lê fontes, não verifica disponibilidade, não carrega modelos e retorna `dispatched=false`; o controlador executa o despacho nativo. `--restricted` e `--acervo-authorized` são flags de compatibilidade ignoradas.
<!-- END CODEX-MODEL-ROUTING -->

## Integração opcional Codex → AGY → Gemini

- A ponte `local-user/codex-argon` permite ao Codex comandar tarefas delimitadas no AGY. O processo AGY roda localmente, mas Gemini é um executor em nuvem: aplicar SIGILO LOCAL PRIORITARIO antes de preparar o snapshot ou enviar a tarefa. Nenhum dado de caso, nome, caminho ou trecho de caso pode ir para essa ponte. Use material sintético ou conteúdo sem dados de caso dentro do escopo autorizado.
- Luna continua como controlador padrão e conserva a responsabilidade por objetivo, escopo, arquivos, critérios de aceite e integração. A ponte não troca o modelo principal nem substitui os cinco papéis nativos; use-a quando a tarefa pedir execução no AGY/Gemini ou quando ela for adequada ao trabalho autorizado.
- Consulte `argon_status` e `argon_models` antes do despacho; leia a skill `codex-argon` instalada. Use apenas os modelos Gemini retornados e autorizados pela ponte. Nunca acione Claude Code, modelos Claude ou APIs Anthropic como fallback do AGY. Se o MCP não estiver disponível nesta sessão, use a CLI do checkout instalado ou informe a dependência ausente.
- Defina `source`, `inputs`, `owns`, `acceptance`, modelo e limites explicitamente. Envie contexto compacto. O AGY trabalha em snapshot e devolve resposta/patch; o Codex acompanha o job até conclusão, lê os artefatos, confere base, diff e testes e só então registra `argon_accept`. Revisão em chamada separada não substitui a aceitação do Codex. Não aplique patches automaticamente.
- A instalação e a validação por máquina estão em `docs/agy-gemini.md` no repositório canônico `codex-config`. Registro MCP e catálogo disponível não comprovam inferência nem cota; use uma sonda sintética para validar a execução real. Não copie credenciais, logs, jobs ou caminhos pessoais para o repositório.
- Para testar edição com a ponte, consulte o [teste completo](https://github.com/local-user/codex-argon/blob/main/docs/end-to-end-clamp.md) e o [exemplo sintético clamp](https://github.com/local-user/codex-argon/tree/main/examples/clamp). Trabalhe numa cópia isolada: registre a falha inicial e os hashes, obtenha o patch no snapshot, revise o diff e execute os testes no snapshot antes de aplicar à origem. Após aplicar, repita os testes na origem e somente então aceite o job. O patch de referência permite validar o exemplo offline; isso não comprova inferência real. Sucesso no AGY não dispensa a decisão do Codex nem autoriza autoaplicação.
