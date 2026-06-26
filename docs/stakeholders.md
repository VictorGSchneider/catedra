# Stakeholders — Cátedra

Identificação dos principais envolvidos no sistema, seus interesses e como
influenciam os requisitos.

## Stakeholders diretos (usuários do sistema)

| Papel | Descrição | Principais interesses | Influência nos requisitos |
|---|---|---|---|
| **Estudante** | Acompanha turmas, recebe e entrega atividades, consulta notas. | Saber o que precisa fazer e até quando; entregar sem fricção; receber feedback. | Mural, entrega com prazo, notificações adaptativas, painel de carga. |
| **Professor** | Cria turmas e atividades, recebe e corrige entregas, lança notas. | Distribuir conteúdo, organizar entregas, corrigir rápido, comunicar a turma. | Permissões de criação, fila de correção, lançamento/devolução de notas. |
| **Coordenador de Curso** | Acompanha as turmas do seu curso. | Visão consolidada do andamento; identificar turmas com problemas. | Acesso somente leitura às turmas do curso; auditoria de alterações de nota. |
| **Administrador do Sistema** | Gerencia contas, papéis e operação da plataforma. | Disponibilidade, segurança, gestão de usuários e instituições. | Autenticação, RBAC, requisitos não funcionais (segurança, disponibilidade). |

## Stakeholders indiretos

| Parte interessada | Interesse no sistema |
|---|---|
| **Instituição de Ensino** | Centralização dos processos acadêmicos e indicadores de engajamento/evasão. |
| **Secretaria Acadêmica** | Consistência entre matrículas na plataforma e registros oficiais. |
| **Responsáveis/Famílias** (contextos aplicáveis) | Acompanhamento do desempenho — fora do escopo do MVP. |

## Mapa de poder × interesse (resumo)

- **Alto poder / alto interesse:** Professor, Coordenador, Administrador →
  gerenciar de perto; são fonte primária de requisitos.
- **Baixo poder / alto interesse:** Estudante → manter informado e engajado; é o
  beneficiário central do diferencial do produto.
- **Alto poder / baixo interesse:** Instituição → manter satisfeita com
  indicadores e conformidade.
