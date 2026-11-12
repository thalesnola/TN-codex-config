# Script deterministico para geracao de docs/diagrama-motion.svg
# Compativel 100% com sanitizador do GitHub (SVG Puro sem <filter> e sem style= inline)

import pathlib

SVG_CONTENT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 920" width="1000" height="920">
  <defs>
    <!-- Degradê de fundo suave Motion -->
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F3EEFF"/>
      <stop offset="50%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#E9F7FF"/>
    </linearGradient>

    <!-- Ambient Glows em SVG Puro (substitui feGaussianBlur compatível com GitHub) -->
    <radialGradient id="glow_pink" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FF7AC6" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#FF7AC6" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_blue" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#2F9BFF" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#2F9BFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_purple" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_green" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#10B981" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#10B981" stop-opacity="0"/>
    </radialGradient>

    <!-- Motion Trails Diagonais -->
    <linearGradient id="trail_purple" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8A5CF6" stop-opacity="0"/>
      <stop offset="50%" stop-color="#8A5CF6" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#8A5CF6" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="trail_blue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#3B82F6" stop-opacity="0"/>
      <stop offset="50%" stop-color="#3B82F6" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#3B82F6" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Fundo -->
  <rect width="1000" height="920" fill="url(#bg)"/>

  <!-- Ambient Glows -->
  <circle cx="910" cy="110" r="230" fill="url(#glow_pink)"/>
  <circle cx="90" cy="790" r="250" fill="url(#glow_blue)"/>
  <circle cx="500" cy="330" r="280" fill="url(#glow_purple)"/>

  <!-- Motion Trails Diagonais (-12deg) -->
  <rect x="120" y="80" width="280" height="26" rx="13" fill="url(#trail_purple)" transform="rotate(-12 260 93)"/>
  <rect x="680" y="440" width="260" height="24" rx="12" fill="url(#trail_blue)" transform="rotate(-12 810 452)"/>
  <rect x="60" y="36" width="309.0" height="26" rx="13" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1"/>
  <text x="214.5" y="53" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="700" fill="#D97706" text-anchor="middle" letter-spacing="0.5">OPENAI CODEX CLI · AGENTES &amp; PREFLIGHT</text><text x="60" y="86" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="26" font-weight="800" fill="#1B1F3B">TN-codex-config · Agentes Especializados e Preflight</text><text x="60" y="114" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="14" font-weight="500" fill="#4A5568">Quadro dos 4 agentes (Luna, Astra, Sol, Terra) e rotinas locais de preflight com validação de hardware.</text>
  <rect x="82" y="158" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="81" y="154" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="80" y="150" width="240" height="110" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="92" y="160" width="65" height="18" rx="9" fill="#FEF3C7"/><text x="124" y="173" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#B45309" text-anchor="middle">LUNA</text><text x="92" y="196" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="700" fill="#1B1F3B">Análise &amp; Arquitetura</text><text x="92" y="214" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="92" dy="0">Lê bases, mapeia dependências</tspan><tspan x="92" dy="16">e define o plano de implementação.</tspan></text>
  <rect x="342" y="158" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="341" y="154" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="340" y="150" width="240" height="110" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="352" y="160" width="65" height="18" rx="9" fill="#FEF3C7"/><text x="384" y="173" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#B45309" text-anchor="middle">ASTRA</text><text x="352" y="196" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="700" fill="#1B1F3B">Qualidade &amp; Testes</text><text x="352" y="214" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="352" dy="0">Gera suítes de testes automatizados</tspan><tspan x="352" dy="16">e valida cobertura de código.</tspan></text>
  <rect x="82" y="288" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="81" y="284" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="80" y="280" width="240" height="110" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="92" y="290" width="65" height="18" rx="9" fill="#FEF3C7"/><text x="124" y="303" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#B45309" text-anchor="middle">SOL</text><text x="92" y="326" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="700" fill="#1B1F3B">Performance &amp; Otimização</text><text x="92" y="344" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="92" dy="0">Analisa gargalos de memória,</tspan><tspan x="92" dy="16">VRAM e tempos de resposta.</tspan></text>
  <rect x="342" y="288" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="341" y="284" width="240" height="110" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="340" y="280" width="240" height="110" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="352" y="290" width="65" height="18" rx="9" fill="#FEF3C7"/><text x="384" y="303" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#B45309" text-anchor="middle">TERRA</text><text x="352" y="326" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="700" fill="#1B1F3B">Automação &amp; Sistema</text><text x="352" y="344" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="352" dy="0">Scripts operacionais, preflight</tspan><tspan x="352" dy="16">e governança de diretórios.</tspan></text>
  <rect x="602" y="158" width="320" height="240" rx="18" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="601" y="154" width="320" height="240" rx="18" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="600" y="150" width="320" height="240" rx="18" fill="#1B1F3B" stroke="#334155" stroke-width="1.5"/><rect x="616" y="166" width="140" height="20" rx="10" fill="#3B82F6"/><text x="686" y="180" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">LOCAL-PREFLIGHT</text><text x="616" y="210" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="14" font-weight="800" fill="#FFFFFF">Invoke-LocalFirstWorker.ps1</text><text x="616" y="236" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="500" fill="#93C5FD"><tspan x="616" dy="0">✓ Memória RAM livre &gt; 12 GB</tspan><tspan x="616" dy="20">✓ VRAM disponível na GPU dedicada</tspan><tspan x="616" dy="20">✓ Mutex serial Ollama (NUM_PARALLEL=1)</tspan><tspan x="616" dy="20">✓ Barreira estrita de diretório do projeto</tspan><tspan x="616" dy="20">✓ Fallback automático para nuvem se faltar RAM</tspan></text>
  <!-- BLOCO DE DEMONSTRAÇÃO PRÁTICA -->
  
  <rect x="62" y="563" width="880" height="220" rx="22" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="61" y="559" width="880" height="220" rx="22" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="60" y="555" width="880" height="220" rx="22" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
  
  <rect x="80" y="569" width="225" height="24" rx="12" fill="#1B1F3B"/>
  <text x="192" y="585" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="800" fill="#60A5FA" text-anchor="middle" letter-spacing="0.8">DEMONSTRAÇÃO PRÁTICA</text>
  <text x="320" y="586" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="600" fill="#64748B">Fluxo operacional concreto do repositório</text>
  
  <!-- Coluna 1: Entrada -->
  
  <rect x="84" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="83" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="82" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#DDD6FE" stroke-width="1.5"/>
  <rect x="94" y="617" width="90" height="20" rx="10" fill="#EDE9FE"/>
  <text x="139" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#7C3AED" text-anchor="middle">COMANDO NO CODEX</text>
  <text x="96" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Disparo de Script Local</text>
  <text x="96" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="96" dy="0">Codex prepara execução de</tspan><tspan x="96" dy="16">tarefa pesada e aciona a rotina</tspan><tspan x="96" dy="16">Invoke-LocalFirstWorker.ps1.</tspan></text>
  
  <!-- Seta 1 -> 2 -->
  <circle cx="359" cy="682.5" r="14" fill="#EDE9FE" stroke="#C4B5FD" stroke-width="1.5"/>
  <text x="359" y="687.5" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#7C3AED" text-anchor="middle">→</text>
  
  <!-- Coluna 2: Processamento -->
  
  <rect x="379" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="378" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="377" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="1.5"/>
  <rect x="389" y="617" width="125" height="20" rx="10" fill="#E0F2FE"/>
  <text x="451" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#0284C7" text-anchor="middle">PREFLIGHT DE HARDWARE</text>
  <text x="391" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Validação Automática</text>
  <text x="391" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="391" dy="0">Script verifica RAM, VRAM e</tspan><tspan x="391" dy="16">mutex do Ollama local em 2s,</tspan><tspan x="391" dy="16">blindando a máquina contra travamento.</tspan></text>
  
  <!-- Seta 2 -> 3 -->
  <circle cx="654" cy="682.5" r="14" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1.5"/>
  <text x="654" y="687.5" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#0284C7" text-anchor="middle">→</text>
  
  <!-- Coluna 3: Saída -->
  
  <rect x="674" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="673" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="672" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#BBF7D0" stroke-width="1.5"/>
  <rect x="684" y="617" width="105" height="20" rx="10" fill="#DCFCE7"/>
  <text x="736" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#16A34A" text-anchor="middle">EXECUÇÃO LOCAL</text>
  <text x="686" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Processamento a Custo Zero</text>
  <text x="686" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="686" dy="0">Aprovado o hardware, o worker</tspan><tspan x="686" dy="16">executa a tarefa 100% offline</tspan><tspan x="686" dy="16">e devolve o status com código 0.</tspan></text>
  <!-- Faixa Navy Inferior de Conclusão Técnica -->
  <rect x="60" y="800" width="880" height="64" rx="18" fill="#1B1F3B"/>
  <circle cx="95" cy="832" r="15" fill="#3B82F6" fill-opacity="0.25"/>
  <text x="95" y="837" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="15" font-weight="800" fill="#60A5FA" text-anchor="middle">✓</text>
  <text x="125" y="829" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#FFFFFF">Blindagem de Recursos e Agentes Especializados</text>
  <text x="125" y="848" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="500" fill="#94A3B8">Separação de responsabilidades entre agentes e preflight que impede colapso de memória nas estações.</text>
</svg>'''

def main():
    p = pathlib.Path(__file__).parent.parent / 'docs' / 'diagrama-motion.svg'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(SVG_CONTENT, encoding='utf-8')
    print('SVG gerado em:', p)

if __name__ == '__main__':
    main()
