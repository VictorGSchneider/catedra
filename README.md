# Cátedra

> Plataforma de gestão de sala de aula online — semelhante ao Google Classroom,
> com um diferencial de **engajamento adaptativo (Modo Foco)**.
>
> Avaliação Integradora — **Modelagem e Projetos em Engenharia de Software**
> (Profª Fabricia Roos).

## Resumo

O **Cátedra** centraliza o ciclo de ensino — criar turma → distribuir atividade
→ receber entrega → corrigir e devolver nota — e personaliza como cada estudante
recebe informação e gerencia tarefas, reduzindo sobrecarga e evasão.

- **Stack:** Vue.js · FastAPI (Python) · PostgreSQL · Redis Pub/Sub · Object Storage
- **Arquitetura:** híbrida — camadas (núcleo) + publish-subscribe (notificações)
- **Funcionalidades inovadoras:** Modo Foco (notificações adaptativas + painel de carga) e Grupos de Trabalho (formar/gerenciar grupos + entrega e nota por grupo)

## Integrantes

- Alan Eduardo Ziebert
- Artur Petry Ruver
- Luis Antônio Zardin
- Victor Gabriel Schneider

## Links

- **Repositório GitHub:** <https://github.com/victorgschneider/catedra>
- **Gestor de Projetos (GitHub Projects):** <https://github.com/users/VictorGSchneider/projects/4>

## Estrutura do repositório

```
catedra/
├── README.md
├── .gitignore
├── docs/
│   ├── visao-produto.md      # Problema, público, objetivos, benefícios
│   ├── stakeholders.md       # Envolvidos e interesses
│   ├── regras-negocio.md     # 10 regras + impactos + matriz de rastreabilidade
│   ├── user-stories.md       # 10 histórias com critérios de aceitação
│   ├── mvp.md                # Essencial vs. futuro + justificativa
│   ├── arquitetura.md        # Estilo, stack, C4, 4 ADRs e as 2 inovações
│   └── sprint.md             # Diário de sprint + divisão de responsabilidades
├── bpmn/
│   ├── entrega-correcao.md            # Processo (narrativa + Mermaid)
│   ├── entrega-correcao.png           # Diagrama renderizado
│   ├── catedra-processos.bpmn         # BPMN 2.0 (XML) — 3 processos (bpmn.io/Camunda)
│   └── catedra-processos-preview.png  # Preview do .bpmn
├── uml/
│   ├── casos-de-uso.puml     # Fonte PlantUML
│   └── casos-de-uso.png      # Diagrama de casos de uso
├── c4/
│   ├── contexto.puml/.png    # C4 Nível 1 — Contexto
│   └── containers.puml/.png  # C4 Nível 2 — Containers
├── gestao/
│   └── backlog-kanban.csv    # Backlog para importar no GitHub Projects
├── apresentacao/
│   └── roteiro.md            # Roteiro da apresentação (20 min)
├── scripts/                  # Geração dos artefatos (ver "Como reproduzir")
│   ├── gerar_tudo.sh         # Roda tudo de uma vez
│   ├── gen_bpmn.py           # Gera o .bpmn (3 processos) + preview
│   ├── render_pdf.py         # Gera o ENTREGA-catedra.pdf
│   └── render_bpmn.py        # Renderiza o BPMN narrativo
└── ENTREGA-catedra.pdf       # PDF único de entrega
```

## Funcionalidades inovadoras (resumo)

Dois diferenciais frente ao Google Classroom:

**1. Modo Foco (engajamento).** Plataformas atuais tratam todos os estudantes de
forma idêntica e os sobrecarregam com notificações. O Modo Foco deixa cada
estudante definir a **cadência** dos avisos (imediato, resumo diário/semanal) e
oferece um **painel de carga** unificado com os prazos de todas as turmas,
ordenado por urgência. Atende uma lacuna real (incluindo estudantes
neurodivergentes) com alta viabilidade técnica.

**2. Grupos de Trabalho (colaboração).** No Classroom não há como formar/gerenciar
grupos nem vincular uma entrega e uma nota a um grupo. O Cátedra permite **formar
e gerenciar grupos** dentro da turma e tratar a **entrega e a nota por grupo** —
qualquer membro entrega, e a nota publicada vale para todos.

Os dois se apoiam no barramento **publish-subscribe** da arquitetura e **se
compõem**: cada membro do grupo é notificado respeitando a própria cadência.

## Como reproduzir os artefatos

Todos os artefatos gerados por código (o `.bpmn`, os diagramas e o PDF) são
regenerados de uma vez:

```sh
sh scripts/gerar_tudo.sh
```

O script instala as dependências Python (`matplotlib`, `reportlab`) se faltarem,
gera o `.bpmn` + preview, o PDF de entrega e o BPMN narrativo, e renderiza os
diagramas PlantUML. Para os `.puml` é necessário **Java + Graphviz** e o
`plantuml.jar` — baixe em <https://plantuml.com/download> e coloque na raiz do
repositório, ou aponte com `PLANTUML_JAR=/caminho/plantuml.jar`. Os C4 usam
`!include` do C4-PlantUML via internet na primeira execução.

> O `plantuml.jar` **não** é versionado (está no `.gitignore`); os diagramas já
> renderizados (`.png`) permanecem no repositório.
