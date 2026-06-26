#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import os

# Opera a partir da raiz do repositório (este script vive em <raiz>/scripts/)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

BROWN = colors.HexColor("#5a3e1b")
BLUE = colors.HexColor("#2E6CA4")

styles = getSampleStyleSheet()
h_disc = ParagraphStyle("disc", parent=styles["Normal"], fontName="Helvetica-Bold",
                        fontSize=10.5, textColor=colors.HexColor("#666666"))
h_title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold",
                         fontSize=26, textColor=BROWN, spaceBefore=4, spaceAfter=2)
h_sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=11,
                       textColor=colors.HexColor("#444444"))
label = ParagraphStyle("label", parent=styles["Normal"], fontName="Helvetica-Bold",
                       fontSize=11.5, textColor=BLUE, spaceBefore=10, spaceAfter=2)
value = ParagraphStyle("value", parent=styles["Normal"], fontSize=11.5, leading=16)
note_s = ParagraphStyle("note", parent=styles["Normal"], fontSize=11.5, leading=16,
                        textColor=colors.HexColor("#222222"))

doc = SimpleDocTemplate("ENTREGA-catedra.pdf", pagesize=A4,
                        topMargin=2.2*cm, bottomMargin=2*cm,
                        leftMargin=2.2*cm, rightMargin=2.2*cm)
story = []

story.append(Paragraph("MODELAGEM E PROJETOS EM ENGENHARIA DE SOFTWARE", h_disc))
story.append(Paragraph("Avaliação Integradora &nbsp;|&nbsp; Profª Fabricia Roos &nbsp;|&nbsp; UNIJUÍ", h_sub))
story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=1.2, color=BROWN))
story.append(Spacer(1, 16))

story.append(Paragraph("Nome do Projeto", label))
story.append(Paragraph("<b>Cátedra</b> — Plataforma de gestão de sala de aula online", value))

story.append(Paragraph("Integrantes", label))
integrantes = (
    "Alan Eduardo Ziebert<br/>"
    "Artur Petry Ruver<br/>"
    "Luis Antônio Zardin<br/>"
    "Victor Gabriel Schneider"
)
story.append(Paragraph(integrantes, value))

story.append(Paragraph("Link do GitHub", label))
story.append(Paragraph("https://github.com/victorgschneider/catedra", value))

story.append(Paragraph("Link do Gestor de Projetos", label))
story.append(Paragraph("[inserir link do GitHub Projects]", value))

story.append(Paragraph("Funcionalidade Inovadora (resumo)", label))
inov = (
    "Dois diferenciais frente ao Google Classroom. "
    "<b>(1) Modo Foco</b>: cada estudante define a cadência das notificações "
    "(imediato, resumo diário/semanal) e tem um painel de carga unificado com os "
    "prazos de todas as turmas. "
    "<b>(2) Grupos de Trabalho</b>: formar e gerenciar grupos e vincular a "
    "entrega e a nota ao grupo — lacuna real do Classroom. "
    "Ambos reduzem sobrecarga e atrito, apoiados no barramento "
    "publish-subscribe da arquitetura."
)
story.append(Paragraph(inov, note_s))

story.append(Spacer(1, 22))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 6))
foot = ParagraphStyle("foot", parent=styles["Normal"], fontSize=9,
                      textColor=colors.HexColor("#888888"))
story.append(Paragraph(
    "Arquitetura híbrida (camadas + publish-subscribe) · Vue.js · FastAPI · "
    "PostgreSQL · Redis Pub/Sub. Artefatos completos no repositório: visão, "
    "regras de negócio, user stories, MVP, BPMN, casos de uso, C4 e ADRs.", foot))

doc.build(story)
print("PDF de entrega gerado.")
