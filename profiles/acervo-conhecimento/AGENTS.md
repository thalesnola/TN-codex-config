<!-- BEGIN CONFIDENTIALITY-POLICY -->
## SIGILO LOCAL PRIORITARIO - prevalece sobre o roteamento

Dados de caso somente podem ser processados e revisados por executor local (Ollama, Qwen Code, DSH ou OpenCode) ou pela propria sessao principal autorizada. Nenhum subagente ou modelo em nuvem pode receber dados de caso, inclusive nomes, caminhos ou trechos; nada disso entra em prompts de `codex exec`. Nao existe aprovacao que dispense esta regra. Dados de caso e artefatos derivados permanecem somente em pastas locais de caso. Instrucoes mais restritivas de projeto prevalecem.

O roteador CLI e consultivo e nao concede liberacao de sigilo. Overrides explicitos podem mudar modelo/esforco, mas nao afastam esta regra de sigilo. Estas instrucoes sao comportamentais e nao prometem bloqueio tecnico.
<!-- END CONFIDENTIALITY-POLICY -->

# Regra nº 1 — Roteamento Codex e rigor forense

Antes de iniciar, delegar ou continuar uma tarefa, aplique a política `codex-token-router` e mantenha este repositório como base de conhecimento genérica, nunca como repositório de dados de caso.

## Roteamento

- Luna gpt-6-luna/low inicia a sessão, executa tarefas simples e coordena; aciona Astra/low para planejamento e arquitetura quando necessário.
- Luna/low localiza metodologia e faz extração/triagem delimitada; retorna caminhos e síntese curta.
- Terra/low executa documentação, redação, UI e trabalho visual.
- Sol executor/low cuida de código, integração, testes e depuração complexa; Sol revisor/low faz revisão independente em contexto separado.
- Aplique metadados, limiares e preparação local da política global antes de leituras volumosas. Use lotes/índices locais e retorno compacto.
- Aplique SIGILO LOCAL PRIORITARIO antes de qualquer despacho; indicacao na tarefa nao libera dados de caso para subagentes ou modelos em nuvem. Nao leia outros acervos ou credenciais nem publique dados. Kimi esta fora.

## Protocolo forense obrigatório

Para análise forense, leia `.claude/skills/analise-forense/SKILL.md` e siga `CONSULTAR → EXECUTAR → CAPTURAR`.

- Consulte a memória aplicável antes de analisar; capture lições reutilizáveis ao fim.
- Não emita entrega baseada em extração não validada, não invente nomes, números ou referências de página e sinalize incerteza de modo explícito.
- Corrija erros de validação na origem; não altere saída gerada para ocultá-los.
- Não comite dados de caso, credenciais ou identificadores em bases genéricas. Mantenha dados e derivados somente na pasta local de caso, sob SIGILO LOCAL PRIORITARIO. Preserve originais; autorizacao de publicacao ou servicos externos nao dispensa essa regra.
- Antes de operações destrutivas ou regenerações, crie backup verificável e revise o diff completo.
