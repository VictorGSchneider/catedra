#!/bin/sh
# =============================================================================
# gerar_tudo.sh — regenera TODOS os artefatos gerados por código do Cátedra
# -----------------------------------------------------------------------------
# Roda os 3 scripts Python (BPMN .bpmn + preview, PDF de entrega, BPMN narrativo)
# e renderiza os 3 diagramas PlantUML (casos de uso + C4 contexto/containers).
#
# Uso (a partir de qualquer lugar):
#   sh scripts/gerar_tudo.sh
#
# Pré-requisitos:
#   - Python 3 (matplotlib e reportlab — instala se faltar)
#   - Java + Graphviz (para os diagramas PlantUML)
#   - plantuml.jar na raiz do repo ou em scripts/, ou aponte com:
#       PLANTUML_JAR=/caminho/plantuml.jar sh scripts/gerar_tudo.sh
# =============================================================================
set -e

# Este script vive em <raiz>/scripts/ ; a raiz do repositório é o diretório pai.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd)"
cd "$ROOT"

# Localiza o plantuml.jar
PLANTUML="${PLANTUML_JAR:-$ROOT/plantuml.jar}"
[ -f "$PLANTUML" ] || PLANTUML="$SCRIPT_DIR/plantuml.jar"

echo "==> Raiz do projeto: $ROOT"

# Garante a pasta de saída do BPMN, caso falte
mkdir -p bpmn

# -----------------------------------------------------------------------------
# 0) Dependências Python
# -----------------------------------------------------------------------------
echo "==> Verificando dependências Python (matplotlib, reportlab)..."
if ! python3 -c "import matplotlib, reportlab" 2>/dev/null; then
  echo "    Instalando matplotlib e reportlab..."
  pip install --break-system-packages matplotlib reportlab \
    || pip install matplotlib reportlab
fi

# -----------------------------------------------------------------------------
# 1) BPMN 2.0 (.bpmn) com os 3 processos + preview PNG
# -----------------------------------------------------------------------------
echo "==> [1/5] gen_bpmn.py   -> bpmn/catedra-processos.bpmn (+ preview)"
python3 scripts/gen_bpmn.py

# -----------------------------------------------------------------------------
# 2) PDF único de entrega
# -----------------------------------------------------------------------------
echo "==> [2/5] render_pdf.py  -> ENTREGA-catedra.pdf"
python3 scripts/render_pdf.py

# -----------------------------------------------------------------------------
# 3) BPMN narrativo (entrega-correcao.png, com raias)
# -----------------------------------------------------------------------------
echo "==> [3/5] render_bpmn.py -> bpmn/entrega-correcao.png"
python3 scripts/render_bpmn.py

# -----------------------------------------------------------------------------
# 4-5) Diagramas PlantUML (casos de uso + C4)
# -----------------------------------------------------------------------------
if [ -f "$PLANTUML" ] && command -v java >/dev/null 2>&1; then
  echo "==> [4/5] PlantUML: casos de uso -> uml/casos-de-uso.png"
  java -jar "$PLANTUML" -tpng uml/casos-de-uso.puml
  echo "==> [5/5] PlantUML: C4 contexto + containers -> c4/*.png"
  java -jar "$PLANTUML" -tpng c4/contexto.puml c4/containers.puml
else
  echo "!! Pulei os diagramas PlantUML (faltou plantuml.jar e/ou Java)."
  echo "   Baixe o PlantUML em https://plantuml.com/download (precisa de Java + Graphviz)"
  echo "   e rode de novo, ou aponte: PLANTUML_JAR=/caminho/plantuml.jar sh scripts/gerar_tudo.sh"
fi

# -----------------------------------------------------------------------------
echo ""
echo "==> Concluído. Artefatos em: $ROOT"
echo "    - bpmn/catedra-processos.bpmn        (3 processos, abre no bpmn.io)"
echo "    - bpmn/catedra-processos-preview.png (preview do .bpmn)"
echo "    - bpmn/entrega-correcao.png          (BPMN narrativo)"
echo "    - uml/casos-de-uso.png               (se PlantUML rodou)"
echo "    - c4/contexto.png  c4/containers.png (se PlantUML rodou)"
echo "    - ENTREGA-catedra.pdf                (PDF de entrega)"
