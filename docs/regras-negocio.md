# Regras de Negócio — Cátedra

As regras abaixo definem o comportamento do domínio. Mais do que listá-las, este
documento demonstra **como elas influenciam** requisitos, processos (BPMN),
modelagem e decisões arquiteturais (ver `arquitetura.md`).

## Catálogo de regras

| ID | Regra de negócio |
|---|---|
| **RN01** | Apenas **professores** podem criar turmas, atividades e avaliações. |
| **RN02** | Um estudante só acessa turmas nas quais está **matriculado** (via código de convite ou matrícula vinculada). |
| **RN03** | Toda atividade possui **prazo de entrega**. Entregas após o prazo são marcadas como **atrasadas**; o professor configura, por atividade, se entregas atrasadas são **aceitas** ou **bloqueadas**. |
| **RN04** | Cada entrega pertence a **uma única atividade** e a **um único autor** — um **estudante** (atividade individual) ou um **grupo** (atividade em grupo). É possível **reenviar** (versionar) a entrega até o prazo; vale a última versão. |
| **RN05** | A **nota** de uma atividade só fica visível ao estudante **depois que o professor publica a correção**. |
| **RN06** | Notas já lançadas só podem ser alteradas pelo **professor responsável** ou pelo **coordenador**, e toda alteração gera **registro de auditoria** (quem, quando, valor anterior e novo). |
| **RN07** | As **notificações** respeitam as **preferências de cadência** definidas pelo estudante (suporte ao Modo Foco). Nenhum evento gera notificação fora da janela/limite configurados. |
| **RN08** | O coordenador tem acesso **somente leitura** a todas as turmas do seu curso; não pode criar nem editar conteúdo dessas turmas. |
| **RN09** | Em atividades marcadas como **em grupo**, estudantes da turma formam grupos respeitando o **tamanho mínimo e máximo** definidos pelo professor. Cada estudante participa de **no máximo um grupo por atividade**. A formação é **travada** no prazo de fechamento (ou na primeira entrega), impedindo entradas/saídas depois disso. |
| **RN10** | Em atividade em grupo, **qualquer membro** pode enviar/reenviar a entrega até o prazo e ela vale para todos. A **nota publicada aplica-se a todos os membros** do grupo; ajustes individuais feitos pelo professor geram **registro de auditoria** (RN06). |

## Impacto das regras na solução

A seguir, o desdobramento de **três** regras pelos demais artefatos (a atividade
exige pelo menos duas; ampliamos para reforçar a rastreabilidade).

### RN01 — Apenas professores criam turmas/atividades

- **User Story:** US01 (criar turma), US03 (publicar atividade).
- **Caso de Uso:** *Criar Turma*, *Publicar Atividade* — ator **Professor**.
- **BPMN:** no processo de entrega/correção, a raia do **Professor** é a única
  que executa "Publicar atividade".
- **Arquitetura:** exige **autenticação** e **controle de autorização (RBAC)** —
  ver ADR-002.
- **Requisito Não Funcional:** segurança (controle de acesso por papel).

### RN05 — Nota só visível após publicação da correção

- **User Story:** US05 (corrigir e lançar nota), US06 (consultar nota).
- **Caso de Uso:** *Corrigir Entrega* e *Publicar Nota* (estados distintos).
- **BPMN:** a entrega percorre os estados `Entregue → Em correção → Corrigida →
  Publicada`; só no último estado o evento "Nota disponível" é emitido ao aluno.
- **Modelagem:** a entidade *Entrega* possui um atributo de **estado** e a nota
  tem visibilidade condicionada a `estado = Publicada`.
- **Arquitetura:** a transição "Publicada" dispara um **evento** no barramento
  publish-subscribe, que aciona a notificação — ver ADR-003.

### RN07 — Notificações respeitam a cadência do estudante

- **User Story:** US07 (configurar notificações adaptativas).
- **Caso de Uso:** *Configurar Preferências de Notificação*.
- **Arquitetura:** é o principal motor da **decisão de usar publish-subscribe**
  (ADR-003): produtores de eventos (entrega, nota, aviso) ficam **desacoplados**
  do consumidor de notificação, que aplica as regras de cadência por estudante.
- **Funcionalidade Inovadora:** sustenta o **Modo Foco** (camada adaptativa de
  engajamento).

### RN04 + RN09 + RN10 — Trabalhos em grupo (colaboração)

- **User Story:** US09 (formar/gerenciar grupo), US10 (atividade e avaliação em
  grupo).
- **Caso de Uso:** *Formar e Gerenciar Grupo* (Estudante) e *Configurar Trabalho
  em Grupo* (Professor).
- **BPMN:** processo dedicado *Formação de Grupo de Trabalho* (validação de
  tamanho, trava no prazo e habilitação da entrega coletiva).
- **Modelagem:** a *Entrega* passa a ter **autoria polimórfica** — referencia um
  *Estudante* **ou** um *Grupo*; surgem as entidades **Grupo** e **MembroDeGrupo**.
- **Arquitetura:** tratado como um **módulo do monólito** (ADR-001); os eventos
  de grupo (membro entrou, grupo travado, nota publicada) viajam pelo barramento
  **publish-subscribe** (ADR-003) e **compõem com o Modo Foco** — cada membro é
  notificado respeitando sua própria cadência.

## Matriz de rastreabilidade

| Regra | User Story | Caso de Uso | BPMN | Decisão arquitetural |
|---|---|---|---|---|
| RN01 | US01, US03 | Criar Turma / Publicar Atividade | Raia Professor | ADR-002 (RBAC) |
| RN02 | US02 | Matricular-se na Turma | Pré-condição de acesso | ADR-002 (RBAC) |
| RN03 | US04 | Entregar Atividade | Gateway "no prazo?" | — |
| RN04 | US04, US09 | Entregar Atividade (autor: estudante ou grupo) | Reenvio até o prazo | ADR-001 |
| RN05 | US05, US06 | Corrigir / Publicar Nota | Estados da entrega | ADR-003 (eventos) |
| RN06 | US05 | Alterar Nota (auditada) | — | ADR-002 / auditoria |
| RN07 | US07 | Configurar Notificações | — | ADR-003 (pub-sub) |
| RN08 | US08 | Acompanhar Turmas (leitura) | — | ADR-002 (RBAC) |
| RN09 | US09, US10 | Formar e Gerenciar Grupo / Configurar Trabalho em Grupo | Processo "Formação de Grupo" | ADR-001 (módulo) |
| RN10 | US10, US04 | Avaliar Entrega em Grupo | Entrega e nota por grupo | ADR-003 (eventos) |
