"""Validate the portable bundle locally, including mandatory confidentiality policy."""
from pathlib import Path
import hashlib
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
POLICY_SHA256 = '92c666e3212afc1810201598846d4bd8c336382938c50f29ef3ad87d23564148'
AGENTS = ('astra-planner', 'luna-triage', 'sol-executor', 'sol-reviewer', 'terra-visual')
POLICY_CONSUMERS = ('AGENTS.md', 'skills/codex-token-router/SKILL.md',
                    'local-router/README.md', 'profiles/acervo-conhecimento/AGENTS.md',
                    'profiles/redacao-forense/AGENTS.md',
                    *(f'agents/{name}.toml' for name in AGENTS))
CONTRADICTIONS = (r'dispon[ií]veis a qualquer modelo',
                  r'podem ser processados por qualquer modelo',
                  r'podem ser usados por modelos adequados',
                  r'podem ser usados pelos modelos adequados',
                  r'autorizados aos modelos adequados',
                  r'sem bloqueio por categoria restrita',
                  r'sem nova barreira por categoria')


def require(condition, message):
    # Explicit checks remain active under python -O.
    if not condition:
        raise ValueError(message)


def validate(root=ROOT):
    policy_text = (root / 'policy/confidentiality.md').read_text(encoding='utf-8').strip()
    require(hashlib.sha256(policy_text.encode()).hexdigest() == POLICY_SHA256,
            'Confidentiality policy integrity check failed')
    for relative in POLICY_CONSUMERS:
        content = (root / relative).read_text(encoding='utf-8')
        require(policy_text in content, f'Missing or altered confidentiality policy: {relative}')
        require(not any(re.search(pattern, content, re.I) for pattern in CONTRADICTIONS),
                f'Contradictory confidentiality permission: {relative}')
    config = tomllib.loads((root / 'config/config.toml.example').read_text(encoding='utf-8'))
    require(config['model'] == 'gpt-6-luna', 'Unexpected controller model')
    require(config['model_reasoning_effort'] == 'low', 'Unexpected controller effort')
    require(config['agents']['default_subagent_model'] == 'gpt-6-luna', 'Unexpected default agent model')
    require(config['agents']['default_subagent_reasoning_effort'] == 'low', 'Unexpected default agent effort')
    policy = json.loads((root / 'local-router/policy.json').read_text(encoding='utf-8'))
    require(policy['controller']['model'] == config['model'], 'Controller policy mismatch')
    require(policy['controller']['effort'] == config['model_reasoning_effort'], 'Controller effort mismatch')
    require(policy['controller']['planner'] == 'astra-planner', 'Unexpected planner')
    agent_paths = list((root / 'agents').glob('*.toml'))
    require({path.stem for path in agent_paths} == set(AGENTS), 'Expected five named agents')
    for path in agent_paths:
        agent = tomllib.loads(path.read_text(encoding='utf-8'))
        require(agent['name'] == path.stem, f'Agent name mismatch: {path.name}')
        require(agent['model'] == policy['cloud'][path.stem]['model'], f'Model mismatch: {path.name}')
        require(agent['model_reasoning_effort'] == 'low', f'Effort mismatch: {path.name}')
        require(policy_text in agent['developer_instructions'], f'Missing instructions policy: {path.name}')
    skill = (root / 'skills/codex-token-router/SKILL.md').read_text(encoding='utf-8')
    require(skill.startswith('---\nname: codex-token-router\n'), 'Skill frontmatter must remain first')


if __name__ == '__main__':
    validate()
    print('Bundle valid: confidentiality policy, config, five agents and routing policy agree.')
