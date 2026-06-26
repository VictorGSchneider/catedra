# Roteiro da Apresentação — Cátedra (20 min)

Segue a estrutura recomendada pela avaliação. Tempo total: até 20 min +
5 min de arguição.

---

## 1. Visão do Produto e MVP — *1 a 2 min*
- **Problema:** gestão de turmas/atividades espalhada em e-mail e planilhas;
  plataformas atuais tratam todos os alunos igual e sobrecarregam com avisos.
- **Público-alvo:** estudantes, professores, coordenadores, administradores.
- **MVP:** ciclo essencial (criar turma → atividade → entrega → correção → nota)
  + fatia básica do Modo Foco (cadência + painel de carga) + **trabalhos em
  grupo** (formar grupo + entrega/nota por grupo).

## 2. Regras de Negócio e Impactos — *2 min*
Mostrar a cadeia de rastreabilidade de **uma** regra forte:

> **RN05** (nota só visível após publicação)
> → **US05/US06** → **Caso de Uso** *Publicar Nota* → **BPMN** (estados da
> entrega) → **ADR-003** (evento `nota.publicada` no pub-sub).

Mencionar também **RN07** (cadência) como motor da inovação e do pub-sub.

## 3. Processo de Negócio (BPMN) — *5 min*
- Abrir `bpmn/entrega-correcao.png`.
- Percorrer as raias **Professor / Estudante / Sistema**.
- Destacar o gateway **"Dentro do prazo?"** (RN03) e os dois pontos de
  notificação que respeitam a cadência (RN07).
- Mostrar também o arquivo **`catedra-processos.bpmn`** (abre no bpmn.io), que
  traz os processos *Entrega e Correção*, *Notificações Adaptativas (Modo Foco)*
  e ***Formação de Grupo de Trabalho*** — este último amarrando RN09/RN10.

## 4. Arquitetura da Solução — *3 a 5 min*
- **Estilo:** híbrido (camadas + publish-subscribe). Dizer **por que não**
  microserviços (over-engineering para o contexto).
- **C4 Contexto** (`c4/contexto.png`): atores + sistemas externos.
- **C4 Containers** (`c4/containers.png`): SPA, API, Banco, Barramento, Worker.
- **Decisões (ADRs):** híbrido (ADR-001), JWT+RBAC (ADR-002), pub-sub para
  notificações (ADR-003), object storage para anexos (ADR-004).
- Foco em **justificar** cada decisão a partir de uma regra de negócio.

## 5. Evidências de Colaboração — *1 min*
- Mostrar o **repositório GitHub** (estrutura e histórico de commits).
- Mostrar o **GitHub Projects** (backlog importado, quadro Kanban, cartões
  movimentados, distribuição de tarefas).

## 6. Funcionalidades Inovadoras — *3 a 5 min* (atenção especial)
**Diferencial 1 — Modo Foco (engajamento):**
- **O que é:** camada adaptativa de engajamento.
- **Problema:** sobrecarga de notificação e desenho "tamanho único"; lacuna real
  para estudantes neurodivergentes.
- **Benefícios:** menos ansiedade, prazos sempre visíveis no painel de carga.
- **Impacto arquitetural:** é o caso de uso que justifica o pub-sub (ADR-003);
  nova entidade *PreferênciaDeNotificação*; painel como *read model*.

**Diferencial 2 — Grupos de Trabalho (colaboração):**
- **O que é:** formar/gerenciar grupos e tratar **entrega e nota por grupo**.
- **Problema:** o Classroom não suporta grupos; hoje "um aluno entrega por
  todos" e a organização vira planilha paralela.
- **Viabilidade:** entidades simples (*Grupo*, *MembroDeGrupo*) + autoria
  **polimórfica** da entrega (estudante ou grupo).
- **Impacto arquitetural:** módulo do monólito (ADR-001); eventos de grupo no
  pub-sub **compõem com o Modo Foco** (cada membro notificado na sua cadência).

---

### Preparação para a arguição (5 min)
Todos os integrantes devem saber explicar:
- por que a arquitetura é híbrida e não microserviços;
- como a RN05 atravessa BPMN → arquitetura;
- como o Modo Foco funciona tecnicamente sem acoplar ao núcleo;
- como os Grupos de Trabalho modelam a autoria da entrega (estudante ou grupo) e
  por que são um módulo do monólito, não um serviço à parte;
- o que está dentro e fora do MVP e **por quê**.

> **Dica:** gerar os slides a partir deste roteiro (1 slide por seção). Posso
> montar a apresentação final (PDF/PPTX) quando quiser.
