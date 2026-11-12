"""Metadata-only, deterministic routing query. Never dispatches or reads task files."""
import argparse
import json
from pathlib import Path

TASKS = ('planning', 'architecture', 'implementation', 'testing', 'debug', 'review',
         'triage', 'extraction', 'batch', 'visual', 'writing', 'computer-use', 'investigation', 'search', 'summarization')


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('items must be positive')
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError('metadata must be nonnegative')
    return number


def decide(args, policy):
    mechanical = args.task in ('batch', 'triage', 'extraction', 'search', 'summarization')
    limits = policy['local_first']
    large = (args.total_bytes >= limits['total_bytes'] or
             args.largest_file_bytes >= limits['largest_file_bytes'] or
             (mechanical and max(args.items, args.files) >= limits['mechanical_count']))
    planning = args.task in ('planning', 'architecture')
    local = args.scope == 'local' or (args.scope == 'auto' and not planning and args.task not in ('review', 'visual', 'writing', 'computer-use') and
            (large or (args.acervo and args.task == 'investigation')))
    decision = {
        'policy_version': policy['version'], 'status': 'unsupported',
        'destination': 'local' if local else 'cloud', 'agent': None, 'model': None,
        'reasoning_effort': None, 'reason': '', 'dispatched': False,
        'cloud_forbidden': args.scope == 'local',
        'execution_queue': 'serial-local' if local else 'native-agents',
        'volume_local_first': large, 'compact_context_required': large,
        'preparation': 'local_chunking_or_index' if large else None,
        'cloud_input': 'compact_summary_only' if large else 'task_context',
        'preprocessing_required': args.input_kind == 'binary',
        'compatibility_flags_ignored': [name for name, active in
            [('restricted', args.restricted), ('acervo-authorized', args.acervo_authorized)] if active],
    }

    def block(reason):
        decision['reason'] = reason
        return decision

    def select(agent, reason):
        entry = policy['controller'] if agent == 'controller' else policy['local' if local else 'cloud'][agent]
        decision.update(status='selected', agent=agent, model=entry['model'],
                        reasoning_effort=entry.get('effort'), reason=reason)
        if local:
            decision['requirements'] = policy['local_requirements']
            decision['availability_verified'] = False
        return decision

    if args.input_kind == 'binary':
        decision.update(status='needs_preprocessing', destination='local',
                        preparation='local_extraction_or_ocr', cloud_input='none_until_preprocessed',
                        execution_queue='serial-local', availability_verified=False,
                        reason='Extrair texto/OCR local em lotes se necessario; ferramenta nao verificada. Reconsultar com metadados do texto extraido; nao enviar bytes ao modelo.')
        return decision
    if local:
        if planning:
            return block('Nao existe Astra local configurado. Devolver decisao pendente com contexto compacto à Luna controladora; sem fallback automatico.')
        if args.task == 'investigation':
            return select('opencode', 'Investigacao do escopo indicado pelo usuario; processamento local e retorno compacto.')
        if args.task in ('implementation', 'testing', 'debug') and args.complexity == 'small' and not large:
            return select('dsh', 'Codigo pequeno local; revisar diff e validar antes de aceitar.')
        if args.complexity != 'complex' and (mechanical or args.task in ('implementation', 'testing', 'debug')):
            return select('qwen', 'Processamento local delimitado: dividir arquivos em lotes/chunks, manter indices e artefatos no disco, devolver resumo compacto; validar resultados.')
        return block('Nenhum executor local adequado configurado para este tipo/complexidade; sem fallback automatico para cloud.')
    if args.task in ('planning', 'architecture'):
        return select('astra-planner', 'Luna controladora consulta Astra para planejamento e arquitetura; Astra devolve recomendacao compacta e Luna coordena a execucao.')
    if args.task == 'review':
        return select('sol-reviewer', 'Revisao independente por Sol, com evidencias e validacao.')
    if args.task in ('visual', 'writing', 'computer-use'):
        return select('terra-visual', 'Terra executa trabalho visual, UI, documentos, redacao ou computer use.')
    if args.task in ('implementation', 'testing', 'debug') and args.complexity == 'small':
        return select('controller', 'Luna executa codigo ou verificacao pequena e delimitada.')
    if args.task in ('triage', 'extraction', 'batch', 'search', 'summarization') and args.complexity != 'complex':
        return select('controller', 'Luna executa busca focada, extracao, resumo ou triagem delimitada.')
    return select('sol-executor', 'Sol executa codigo, integracoes, testes, debug e tarefas complexas.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', choices=TASKS, required=True)
    parser.add_argument('--complexity', choices=('small', 'medium', 'complex'), default='medium')
    parser.add_argument('--items', type=positive_int, default=1)
    parser.add_argument('--scope', choices=('auto', 'local', 'cloud'), default='auto')
    parser.add_argument('--total-bytes', type=nonnegative_int, default=0)
    parser.add_argument('--largest-file-bytes', type=nonnegative_int, default=0)
    parser.add_argument('--files', type=nonnegative_int, default=0)
    parser.add_argument('--input-kind', choices=('text', 'binary'), default='text')
    parser.add_argument('--restricted', action='store_true', help='Ignored compatibility metadata')
    parser.add_argument('--acervo', action='store_true', help='Collection already supplied/indicated for task; metadata only')
    parser.add_argument('--acervo-authorized', action='store_true', help='Ignored compatibility metadata')
    parser.add_argument('--dry-run', action='store_true', help='All invocations are dry runs')
    args = parser.parse_args()
    if args.total_bytes and args.largest_file_bytes and args.largest_file_bytes > args.total_bytes:
        parser.error('largest-file-bytes cannot exceed known total-bytes; zero means unknown')
    policy = json.loads(Path(__file__).with_name('policy.json').read_text(encoding='utf-8'))
    print(json.dumps(decide(args, policy), ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
