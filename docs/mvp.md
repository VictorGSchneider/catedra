# MVP — Cátedra

O MVP entrega o **menor conjunto de funcionalidades que torna a plataforma
realmente útil**: o ciclo completo de ensino, mais uma fatia mínima do
diferencial que distingue o produto.

## Funcionalidades essenciais (MVP)

| # | Funcionalidade | User Stories | Justificativa |
|---|---|---|---|
| 1 | Autenticação e perfis (Estudante/Professor/Coordenador/Admin) | — | Sem identidade e papéis nada funciona; base do RBAC. |
| 2 | Criar e gerenciar turmas (código de convite) | US01 | Unidade central de organização. |
| 3 | Matrícula via código | US02 | Sem isso o estudante não acessa nada. |
| 4 | Mural de avisos da turma | US03 | Comunicação mínima professor↔turma. |
| 5 | Publicar atividades com prazo | US03 | Coração da distribuição de tarefas. |
| 6 | Entregar atividade (com reenvio até o prazo) | US04 | Fecha o lado do estudante. |
| 7 | Corrigir, lançar e publicar nota | US05, US06 | Fecha o ciclo; entrega valor ao professor. |
| 8 | **Notificações adaptativas (versão básica)** + **painel de carga** | US07 | Diferencial barato e de alto valor: cadência configurável (imediato/diário) e visão unificada de prazos. |
| 9 | **Trabalhos em grupo** (formar grupo + entrega e nota por grupo) | US09, US10 | Lacuna real do Classroom. O essencial é barato: modelo *Grupo/MembroDeGrupo* + autoria coletiva da entrega; alto valor para o ensino. |

Esses nove itens formam o laço **criar → distribuir → entregar (individual ou em
grupo) → corrigir → devolver**, que é o mínimo para substituir o uso de e-mail +
planilha numa turma real.

## Funcionalidades futuras (pós-MVP)

| Funcionalidade | Por que fica para depois |
|---|---|
| Modo Foco completo (decomposição de atividades em subtarefas, modo baixo estímulo) | Alto valor, mas exige mais UI e modelagem; o painel de carga já entrega o ganho inicial. |
| Avaliação por pares e contribuição individual no grupo | O essencial (entrega e nota por grupo) já resolve o caso comum; medir contribuição exige mais UI e modelagem. |
| Acompanhamento do coordenador com indicadores ricos (US08 avançada) | A leitura simples basta no MVP; dashboards podem evoluir. |
| Videoconferência / aulas ao vivo | Integrável depois; não é o gargalo do problema central. |
| Antiplágio e detecção de conteúdo gerado por IA | Requer serviços externos e curadoria; não bloqueia o ciclo essencial. |
| Analítica preditiva de evasão | Depende de histórico de dados que só existe após uso real. |
| Aplicativo móvel nativo | A web responsiva atende o MVP. |
| Integração com ERP acadêmico da instituição | Alto custo de integração; tratável como projeto à parte. |

## Justificativa da priorização

A priorização seguiu três critérios, nesta ordem:

1. **Viabiliza o ciclo de valor?** Itens sem os quais a turma não funciona
   (auth, turma, matrícula, atividade, entrega, correção) vêm primeiro.
2. **Custo × valor do diferencial.** Os **dois diferenciais** entram no MVP
   **apenas na fatia barata e de maior impacto**: do Modo Foco, a cadência de
   notificação + painel de carga; dos Trabalhos em grupo, formar grupo + entrega
   e nota por grupo. As partes caras (decomposição, modo baixo estímulo,
   avaliação por pares) viram fast-follow.
3. **Dependência de dados/integrações externas.** Tudo que depende de histórico
   acumulado (preditiva) ou de terceiros (antiplágio, ERP, vídeo) é adiado para
   reduzir risco e tempo até a primeira versão útil.

> **Princípio:** o MVP precisa ser usável por uma turma real de ponta a ponta e,
> ao mesmo tempo, já mostrar **por que** o Cátedra é diferente das alternativas.
