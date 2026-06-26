# Diário de Sprint — Cátedra

## Sprint 1 — Concepção e Projeto da Solução

**Objetivo da sprint:** conceber a solução (visão, regras, histórias, MVP) e
projetar (BPMN, casos de uso, arquitetura, C4, decisões) o sistema Cátedra.

## Divisão das responsabilidades

| Integrante | Responsabilidades principais | Artefatos |
|---|---|---|
| Alan Eduardo Ziebert | Engenharia de requisitos | `visao-produto.md`, `stakeholders.md`, `regras-negocio.md` |
| Artur Petry Ruver | Histórias e MVP | `user-stories.md`, `mvp.md`, backlog/Kanban |
| Luis Antônio Zardin | Modelagem | `bpmn/`, `uml/casos-de-uso` |
| Victor Gabriel Schneider | Arquitetura | `arquitetura.md`, `c4/`, ADRs |

> A evidência individual fica registrada no histórico de commits do GitHub e na
> movimentação dos cartões do quadro (GitHub Projects).

> A inovação de **Grupos de Trabalho** (colaboração) foi um esforço
> **transversal**: permeia requisitos (RN04/RN09/RN10), histórias (US09/US10),
> modelagem (processo *Formação de Grupo* no BPMN) e arquitetura (módulo do
> monólito + eventos no pub-sub). O roteiro de apresentação
> (`apresentacao/roteiro.md`) foi consolidado pela equipe.

## Principais decisões tomadas

1. **Escolha do estilo arquitetural híbrido** (camadas + publish-subscribe) em
   vez de microserviços, por ser proporcional ao contexto de uma instituição
   (ver ADR-001).
2. **Duas funcionalidades inovadoras** — **Modo Foco** (camada adaptativa de
   engajamento) e **Grupos de Trabalho** (camada de colaboração) —, escolhidas
   por atacarem lacunas reais dos concorrentes e por terem alta viabilidade técnica.
3. **Recorte enxuto do MVP**: dos diferenciais, incluir apenas a fatia barata e
   de maior impacto (do Modo Foco, a cadência de notificação + painel de carga;
   dos Grupos de Trabalho, formar grupo + entrega/nota por grupo), adiando as
   partes caras.
4. **Stack** Vue + FastAPI + PostgreSQL, por domínio da equipe e adequação ao
   desenho em camadas.

## Dificuldades encontradas e soluções adotadas

| Dificuldade | Solução |
|---|---|
| Definir o escopo do diferencial sem inflar o MVP | Separar a inovação em "fatia MVP" (barata) e "fast-follow" (cara) no `mvp.md`. |
| Garantir rastreabilidade entre regras e demais artefatos | Criar a **matriz de rastreabilidade** em `regras-negocio.md` ligando RN → US → Caso de Uso → BPMN → ADR. |
| Justificar a arquitetura para a banca | Documentar as alternativas rejeitadas e amarrar cada decisão a uma regra de negócio (seção 1 de `arquitetura.md`). |
| Representar notificações sem acoplar ao núcleo | Adotar publish-subscribe (ADR-003), isolando a política de cadência no Serviço de Notificação. |

## Próximos passos (Sprint 2 — fora desta entrega)

- Prototipar as telas do ciclo essencial (turma, atividade, entrega, correção).
- Detalhar o *read model* do painel de carga.
- Especificar as subtarefas do Modo Foco completo (decomposição e modo baixo
  estímulo).
