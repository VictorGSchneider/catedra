# Visão do Produto — Cátedra

> **Cátedra** — Plataforma de gestão de sala de aula online.

## 1. Problema a ser resolvido

Instituições de ensino precisam coordenar turmas, atividades, avaliações e a
comunicação entre professores e estudantes. Hoje esse fluxo costuma estar
espalhado em e-mail, planilhas, grupos de mensagem e arquivos soltos, o que
gera: perda de prazos, dificuldade de rastrear entregas, retrabalho na correção
e baixa transparência sobre o andamento da turma.

Plataformas existentes (Google Classroom, Moodle, Microsoft Teams) centralizam
parte desse fluxo, mas tratam **todos os estudantes de forma idêntica** e
dependem de um modelo de notificação que sobrecarrega o aluno com avisos
constantes. Estudantes com perfis distintos de atenção e organização (incluindo
estudantes neurodivergentes, que somam uma fração relevante de qualquer turma)
ficam mal atendidos por esse desenho, o que se traduz em prazos perdidos e
evasão.

Há ainda uma lacuna específica de **colaboração**: o trabalho em grupo é comum
no ensino, mas as plataformas atuais o suportam mal. No Google Classroom, por
exemplo, não há como **formar e gerenciar grupos** nem **vincular uma entrega e
uma nota a um grupo** — na prática um aluno entrega "por todos" e a organização
acontece em planilhas e conversas paralelas, fora da plataforma.

## 2. Público-alvo

- **Estudantes** de ensino superior e técnico que acompanham várias disciplinas
  em paralelo.
- **Professores** que precisam publicar atividades, receber entregas e corrigir
  com agilidade.
- **Coordenadores de curso** que acompanham o andamento das turmas.
- **Administradores** responsáveis pela operação da plataforma na instituição.

## 3. Objetivos da solução

1. Centralizar o ciclo de ensino: **criar turma → distribuir atividade →
   receber entrega → corrigir e devolver nota**.
2. Tornar prazos e pendências **visíveis e rastreáveis** para todos os papéis.
3. Reduzir o atrito da correção para o professor (entregas organizadas, estado
   claro de cada submissão, lançamento e devolução de notas).
4. **Adaptar a forma como cada estudante recebe informação e gerencia tarefas**,
   reduzindo sobrecarga e melhorando a retenção — o diferencial do produto
   (ver `mvp.md` e a seção de Funcionalidade Inovadora em `arquitetura.md`).
5. **Apoiar o trabalho em grupo de ponta a ponta** — formar/gerenciar grupos e
   vincular a entrega e a nota ao grupo — cobrindo uma lacuna das plataformas atuais.

## 4. Benefícios esperados

| Benefício | Indicador de sucesso |
|---|---|
| Menos prazos perdidos | Queda na taxa de entregas atrasadas por turma |
| Correção mais rápida | Redução do tempo médio entre entrega e devolução da nota |
| Transparência do andamento | Coordenação consegue ver status sem pedir relatório |
| Inclusão e engajamento | Estudantes configuram a cadência de avisos; menor evasão |
| Colaboração sem atrito | Grupos formados e avaliados na própria plataforma; menos gambiarra em planilhas |
| Organização institucional | Artefatos da disciplina num único lugar versionável |

## 5. Escopo (resumo)

**Dentro do escopo (visão de produto):** gestão de turmas e matrículas, mural de
avisos, atividades com prazo, entregas com versionamento, **formação e gestão de
grupos de trabalho**, correção e notas, perfis e permissões, e a camada
adaptativa de engajamento.

**Fora do escopo nesta etapa:** videoconferência nativa, integração com sistemas
acadêmicos legados (ERP da instituição), aplicativo móvel nativo, antiplágio e
analítica preditiva avançada — tratados como evolução futura.
