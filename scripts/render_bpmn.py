#!/usr/bin/env python3
# Renderiza um BPMN (raias Professor / Estudante / Sistema) para o processo
# "Entrega e Correção de Atividade" do Cátedra.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Polygon, Rectangle
from matplotlib.lines import Line2D
import os

# Opera a partir da raiz do repositório (este script vive em <raiz>/scripts/)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Paleta
C_TASK   = "#2E6CA4"
C_TASK_T = "white"
C_GW     = "#E9A319"
C_START  = "#4CAF50"
C_END    = "#C0392B"
C_LANE_A = "#F5EFE3"
C_LANE_B = "#ECE3CF"
C_POOL   = "#5a3e1b"
C_NOTE   = "#FFF7D6"

fig, ax = plt.subplots(figsize=(16.5, 7.2))
ax.set_xlim(0, 16.5)
ax.set_ylim(0, 6.4)
ax.axis("off")

# ---- Pool + Raias ----
LANE_X0, LANE_X1 = 0.2, 16.3
lanes = [("Professor", 4.2, 6.2, C_LANE_A),
         ("Estudante", 2.2, 4.2, C_LANE_B),
         ("Sistema",   0.2, 2.2, C_LANE_A)]
for name, y0, y1, col in lanes:
    ax.add_patch(Rectangle((LANE_X0, y0), LANE_X1-LANE_X0, y1-y0,
                           facecolor=col, edgecolor=C_POOL, linewidth=1.2, zorder=1))
    # faixa de rótulo
    ax.add_patch(Rectangle((LANE_X0, y0), 0.55, y1-y0,
                           facecolor="#D8C9A8", edgecolor=C_POOL, linewidth=1.2, zorder=2))
    ax.text(LANE_X0+0.27, (y0+y1)/2, name, rotation=90, va="center", ha="center",
            fontsize=11, fontweight="bold", color="#3a2a12", zorder=3)
# título do pool
ax.text((LANE_X0+LANE_X1)/2, 6.28, "Cátedra — Processo: Entrega e Correção de Atividade",
        ha="center", va="bottom", fontsize=13, fontweight="bold", color="#3a2a12")

LANE_Y = {"Prof": 5.2, "Est": 3.2, "Sist": 1.2}

def task(x, lane, text, w=1.5, h=0.95):
    y = LANE_Y[lane]
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.12",
                 facecolor=C_TASK, edgecolor="#1d466A",
                 linewidth=1.2, zorder=4))
    ax.text(x, y, text, ha="center", va="center", fontsize=8.3, color=C_TASK_T,
            zorder=5, wrap=True)
    return (x, y)

def task2(x, y, text, w=1.6, h=0.7):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.10",
                 facecolor=C_TASK, edgecolor="#1d466A", linewidth=1.2, zorder=4))
    ax.text(x, y, text, ha="center", va="center", fontsize=7.8, color=C_TASK_T, zorder=5)
    return (x, y)

def event(x, lane, kind="start", label=""):
    y = LANE_Y[lane]
    col = C_START if kind == "start" else C_END
    lw = 2.0 if kind == "start" else 3.2
    ax.add_patch(Circle((x, y), 0.32, facecolor="white", edgecolor=col,
                        linewidth=lw, zorder=4))
    if label:
        ax.text(x, y-0.5, label, ha="center", va="top", fontsize=7.5, color="#333")
    return (x, y)

def gateway(x, lane, label=""):
    y = LANE_Y[lane]
    d = 0.42
    ax.add_patch(Polygon([(x, y+d), (x+d, y), (x, y-d), (x-d, y)],
                 closed=True, facecolor=C_GW, edgecolor="#9c6f10",
                 linewidth=1.3, zorder=4))
    ax.text(x, y, "×", ha="center", va="center", fontsize=14, fontweight="bold",
            color="#7a5600", zorder=5)
    if label:
        ax.text(x, y+0.62, label, ha="center", va="bottom", fontsize=8, fontweight="bold",
                color="#3a2a12")
    return (x, y)

def flow(p1, p2, label="", style="-", rad=0.0, color="#444"):
    arr = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                          linewidth=1.3, color=color, zorder=3,
                          connectionstyle=f"arc3,rad={rad}",
                          linestyle=style, shrinkA=18, shrinkB=18)
    ax.add_patch(arr)
    if label:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        ax.text(mx, my+0.12, label, ha="center", va="bottom", fontsize=7.6,
                fontweight="bold", color="#222",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))

def note(x, y, text):
    ax.add_patch(FancyBboxPatch((x-1.05, y-0.34), 2.1, 0.68,
                 boxstyle="round,pad=0.04", facecolor=C_NOTE, edgecolor="#caa64a",
                 linewidth=1.0, linestyle=(0,(4,2)), zorder=6))
    ax.text(x, y, text, ha="center", va="center", fontsize=7.2, color="#5a4a1a", zorder=7)

# ---- Elementos ----
e_start = event(1.15, "Prof", "start", "Atividade pronta")
t_pub   = task(2.7, "Prof", "Publicar\natividade")
t_notif = task(4.3, "Sist", "Notificar estudantes\n(cadência)")
t_send  = task(5.9, "Est", "Elaborar e\nenviar entrega")
g_prazo = gateway(7.5, "Sist", "Dentro do prazo?")
t_ok    = task2(9.1, 1.55, "Registrar\ncomo Entregue")
t_late  = task2(9.1, 0.62, "Registrar\ncomo Atrasada")
t_avail = task(10.7, "Prof", "Corrigir\nentrega")
t_grade = task(12.3, "Prof", "Publicar\nnota")
t_event = task(13.6, "Sist", "Emitir evento +\nnotificar (cadência)")
t_view  = task(15.1, "Est", "Consultar nota\ne feedback")
e_end   = event(15.95, "Est", "end", "Fim")

# ---- Fluxos de sequência ----
flow(e_start, t_pub)
flow(t_pub, t_notif, rad=-0.15)
flow(t_notif, t_send, rad=-0.15)
flow(t_send, g_prazo, rad=-0.15)
flow(g_prazo, t_ok, "Sim", rad=0.0)
flow(g_prazo, t_late, "Não", rad=0.0)
flow(t_ok, t_avail, rad=-0.1)
flow(t_late, t_avail, rad=-0.2)
flow(t_avail, t_grade)
flow(t_grade, t_event, rad=-0.15)
flow(t_event, t_view, rad=-0.15)
flow(t_view, e_end)

# ---- Anotações de regras de negócio ----
note(4.3, 2.0, "RN07 — respeita a\ncadência do estudante")
note(11.4, 4.18, "RN05 — nota visível ao\nestudante só após publicação")

# legenda
legend_items = [
    ("Tarefa", C_TASK), ("Gateway (decisão)", C_GW),
    ("Início", C_START), ("Fim", C_END),
]
lx = 0.9
for lab, col in legend_items:
    ax.add_patch(Rectangle((lx, 6.02), 0.22, 0.16, facecolor=col, edgecolor="#555"))
    ax.text(lx+0.30, 6.10, lab, fontsize=7.6, va="center")
    lx += len(lab)*0.075 + 0.9

plt.tight_layout()
plt.savefig("bpmn/entrega-correcao.png", dpi=170, bbox_inches="tight",
            facecolor="white")
print("BPMN renderizado.")
