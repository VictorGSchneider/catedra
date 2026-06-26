# User Stories — Cátedra

Cada história segue o formato **Como / quero / para** e traz **critérios de
aceitação** verificáveis. Os identificadores são referenciados pelas regras de
negócio (`regras-negocio.md`) e pelo backlog (`gestao/backlog-kanban.csv`).

---

### US01 — Criar turma
**Como** professor, **quero** criar uma turma com nome, disciplina e código de
convite, **para** organizar meus estudantes e atividades num único espaço.

**Critérios de aceitação**
- Dado que sou um usuário com papel *Professor*, quando crio uma turma, então um
  **código de convite único** é gerado automaticamente.
- A turma criada aparece imediatamente na minha lista de turmas.
- Usuários sem papel *Professor* não conseguem acessar a ação de criar turma (RN01).

---

### US02 — Matricular-se na turma
**Como** estudante, **quero** entrar em uma turma usando o código de convite,
**para** acessar avisos e atividades daquela disciplina.

**Critérios de aceitação**
- Dado um código válido, quando o informo, então passo a ver o mural e as
  atividades da turma.
- Código inválido ou expirado exibe mensagem de erro e **não** concede acesso.
- Só vejo turmas em que estou matriculado (RN02).

---

### US03 — Publicar atividade
**Como** professor, **quero** publicar uma atividade com título, descrição,
anexos e prazo, **para** disponibilizar a tarefa aos estudantes.

**Critérios de aceitação**
- A atividade exige obrigatoriamente um **prazo** (RN03).
- Posso escolher se **aceito ou bloqueio entregas atrasadas**.
- Ao publicar, os estudantes da turma recebem notificação **respeitando a
  cadência de cada um** (RN07).

---

### US04 — Entregar atividade
**Como** estudante, **quero** enviar minha entrega (arquivo e/ou texto) antes do
prazo, **para** cumprir a tarefa e poder reenviar se necessário.

**Critérios de aceitação**
- Posso **reenviar** quantas vezes quiser até o prazo; vale a última versão (RN04).
- Entregas após o prazo são marcadas como **atrasadas**; se a atividade bloquear
  atrasos, a entrega é recusada (RN03).
- Recebo confirmação visual do estado da minha entrega (`Entregue` / `Atrasada`).

---

### US05 — Corrigir e lançar nota
**Como** professor, **quero** ver as entregas organizadas, atribuir nota e
comentário e publicar a correção, **para** devolver o resultado aos estudantes.

**Critérios de aceitação**
- Vejo as entregas por estado (`Entregue`, `Em correção`, `Corrigida`).
- A nota **só fica visível ao estudante após eu publicar** a correção (RN05).
- Alterar uma nota já publicada gera **registro de auditoria** (RN06).

---

### US06 — Consultar nota e feedback
**Como** estudante, **quero** consultar minha nota e o comentário do professor,
**para** entender meu desempenho.

**Critérios de aceitação**
- A nota aparece somente quando a correção foi **publicada** (RN05).
- Vejo nota, comentário e a versão da entrega avaliada.

---

### US07 — Configurar notificações adaptativas *(inovação)*
**Como** estudante, **quero** definir a **cadência** das minhas notificações
(ex.: resumo diário às 18h, em vez de avisos a cada evento), **para** reduzir
sobrecarga e ansiedade sem perder prazos.

**Critérios de aceitação**
- Posso escolher entre **imediato**, **resumo diário** ou **resumo semanal**.
- Nenhuma notificação é enviada fora da janela/limite configurados (RN07).
- Eventos importantes (prazo em ≤ 24h) sempre aparecem no **painel de carga**,
  mesmo que o aviso esteja agrupado.

---

### US08 — Acompanhar turmas do curso
**Como** coordenador, **quero** visualizar (somente leitura) as turmas do meu
curso e seus indicadores, **para** acompanhar o andamento sem interferir.

**Critérios de aceitação**
- Vejo todas as turmas do curso, mas **não** consigo criar nem editar conteúdo
  (RN08).
- Tenho acesso aos indicadores de entregas/atrasos por turma.

---

### US09 — Formar e gerenciar grupo de trabalho *(inovação · colaboração)*
**Como** estudante, **quero** criar um grupo, convidar/entrar em um grupo
existente e sair antes do fechamento, **para** organizar a entrega de uma
atividade em grupo sem combinar tudo por fora da plataforma.

**Critérios de aceitação**
- Posso **criar** um grupo (com nome) ou **entrar** em um grupo aberto da turma,
  até o **tamanho máximo** definido pelo professor (RN09).
- Não consigo participar de **mais de um grupo** na mesma atividade (RN09).
- Posso **sair** do grupo enquanto a formação estiver aberta; após o **prazo de
  fechamento** (ou a primeira entrega) a composição é **travada** (RN09).
- Cada membro recebe aviso de mudanças do grupo respeitando sua **cadência** (RN07).

---

### US10 — Atividade e avaliação em grupo
**Como** professor, **quero** marcar uma atividade como **em grupo** (definindo
tamanho mínimo/máximo e prazo de formação) e corrigir/publicar a nota **por
grupo**, **para** avaliar trabalhos coletivos sem corrigir o mesmo trabalho
várias vezes.

**Critérios de aceitação**
- Ao publicar, posso ativar o **modo em grupo** e definir os **limites de
  tamanho** e o **prazo de formação** (RN09).
- Vejo **uma entrega por grupo**; qualquer membro pode ter enviado/reenviado até
  o prazo (RN10).
- Ao publicar a nota, ela fica visível a **todos os membros** do grupo (RN05, RN10).
- Posso aplicar **ajuste individual** a um membro; a alteração gera **auditoria**
  (RN06).

---

## Resumo de priorização (referência ao MVP)

| ID | Prioridade | Entra no MVP? |
|---|---|---|
| US01, US02, US03, US04, US05, US06 | Alta | **Sim** (ciclo essencial) |
| US07 | Alta (diferencial) | **Sim** (versão básica) |
| US09, US10 | Alta (diferencial) | **Sim** (fatia essencial de grupos) |
| US08 | Média | Parcial (leitura simples) |
