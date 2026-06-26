#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um .bpmn (BPMN 2.0 / formato bpmn.io+Camunda, com biocolor) para o
sistema Cátedra, com layout DI calculado, e renderiza um preview PNG a partir
das MESMAS coordenadas (bpmn.io usa o DI literalmente, então o preview reflete
fielmente o que abre no modeler).
"""

from xml.sax.saxutils import escape
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle
from matplotlib.lines import Line2D
import os

# Opera a partir da raiz do repositório (este script vive em <raiz>/scripts/)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ----------------------------------------------------------------------
# Constantes de layout
# ----------------------------------------------------------------------
COL_W = 170
X0 = 280            # x do primeiro nó (canto esquerdo)
TASK_W, TASK_H = 110, 80
GW = 50
EV = 36
POOL_X = 160
LABEL_BAND = 30     # faixa do nome do pool/lane na esquerda
RIGHT_MARGIN = 60

COLORS = {
    "user":   dict(fill="#c8e6c9", stroke="#205022"),  # verde  -> tarefa humana
    "system": dict(fill="#e1bee7", stroke="#5b176d"),  # roxo   -> tarefa do sistema
    "send":   dict(fill="#fff2cc", stroke="#b58900"),  # âmbar  -> envio/notificação
    "none":   dict(fill="#ffffff", stroke="#000000"),
}

shapes = {}   # id -> dict(x,y,w,h,label,fill,stroke,stype,marker)
edges = {}    # id -> dict(src,tgt,name,wp=[(x,y)..],label_xy)
pools = []    # dict(id,name,proc,x,y,w,h)
lanes = []    # dict(id,name,pool,x,y,w,h,refs=[])
processes = {}  # proc_id -> dict(name, nodes=[], flows=[], lanes=[], annos=[], assocs=[], datastores=[], dataouts=[])

def col_x(c):
    return X0 + c * COL_W

def node_bounds(stype, cx_center, cy_center):
    if stype == "task":
        return cx_center - TASK_W/2, cy_center - TASK_H/2, TASK_W, TASK_H
    if stype == "gateway":
        return cx_center - GW/2, cy_center - GW/2, GW, GW
    if stype == "event":
        return cx_center - EV/2, cy_center - EV/2, EV, EV
    raise ValueError(stype)

# ----------------------------------------------------------------------
# Helpers para montar um processo
# ----------------------------------------------------------------------
def add_pool(pid, name, proc_id, y, lane_specs):
    """lane_specs: list of (lane_id, lane_name, height, [centers dict])"""
    total_h = sum(h for _, _, h, _ in lane_specs)
    processes[proc_id] = dict(name=name, nodes=[], flows=[], lanes=[],
                              annos=[], assocs=[], datastores=[], dataouts=[])
    p = dict(id=pid, name=name, proc=proc_id, y=y, h=total_h)
    pools.append(p)
    cur = y
    lane_centers = {}
    for lid, lname, h, centers in lane_specs:
        lane = dict(id=lid, name=lname, pool=pid, y=cur, h=h, refs=[])
        lanes.append(lane)
        processes[proc_id]["lanes"].append(lane)
        # centros nomeados dentro da lane (mid/up/down -> y absoluto)
        cc = {"mid": cur + h/2}
        cc["up"] = cur + h/2 - 60
        cc["down"] = cur + h/2 + 60
        if centers:
            cc.update({k: cur + h/2 + v for k, v in centers.items()})
        lane_centers[lid] = cc
        cur += h
    p["lane_centers"] = lane_centers
    return p

def add_node(proc_id, nid, stype, kind, lane_id, col, sub, name, color="none", marker=None):
    pool = next(p for p in pools if p["proc"] == proc_id)
    cy = pool["lane_centers"][lane_id][sub]
    cx = col_x(col) + (TASK_W/2 if stype == "task" else (GW/2 if stype == "gateway" else EV/2))
    x, y, w, h = node_bounds(stype, cx, cy)
    shapes[nid] = dict(x=x, y=y, w=w, h=h, label=name, stype=stype, marker=marker,
                       **COLORS[color])
    processes[proc_id]["nodes"].append(dict(id=nid, kind=kind, name=name,
                                            inc=[], out=[]))
    # registra na lane
    lane = next(l for l in lanes if l["id"] == lane_id)
    lane["refs"].append(nid)
    return nid

def add_flow(proc_id, fid, src, tgt, name=""):
    processes[proc_id]["flows"].append(dict(id=fid, src=src, tgt=tgt, name=name))
    # incoming/outgoing
    for n in processes[proc_id]["nodes"]:
        if n["id"] == src: n["out"].append(fid)
        if n["id"] == tgt: n["inc"].append(fid)
    # waypoints
    wp, lxy = route(src, tgt)
    edges[fid] = dict(src=src, tgt=tgt, name=name, wp=wp, label_xy=lxy)

def add_anno(proc_id, aid, text, x, y, w, h, attach_to):
    shapes[aid] = dict(x=x, y=y, w=w, h=h, label=text, stype="anno",
                       fill="#ffffff", stroke="#666666", marker=None)
    processes[proc_id]["annos"].append(dict(id=aid, text=text))
    assoc_id = "Assoc_" + aid
    processes[proc_id]["assocs"].append(dict(id=assoc_id, src=attach_to, tgt=aid))
    # edge (linha tracejada) do nó até a anotação
    s = shapes[attach_to]; a = shapes[aid]
    sx = s["x"] + s["w"]/2; sy = s["y"] + s["h"]
    ax = a["x"] + a["w"]/2; ay = a["y"]
    edges[assoc_id] = dict(src=attach_to, tgt=aid, name="", dashed=True,
                           wp=[(sx, sy), (ax, ay)], label_xy=None)

def add_datastore(proc_id, dsid, name, x, y):
    shapes[dsid] = dict(x=x, y=y, w=50, h=50, label=name, stype="datastore",
                        fill="#ffffff", stroke="#666666", marker=None)
    processes[proc_id]["datastores"].append(dict(id=dsid, name=name))

def add_dataout(proc_id, doid, src_task, datastore):
    processes[proc_id]["dataouts"].append(dict(id=doid, task=src_task, ds=datastore))
    s = shapes[src_task]; d = shapes[datastore]
    sx = s["x"] + s["w"]/2; sy = s["y"] + s["h"]
    dx = d["x"] + d["w"]/2; dy = d["y"]
    edges[doid] = dict(src=src_task, tgt=datastore, name="", dashed=True,
                       wp=[(sx, sy), (dx, dy)], label_xy=None)

# ----------------------------------------------------------------------
# Roteamento ortogonal de arestas (Z-route)
# ----------------------------------------------------------------------
def route(src, tgt):
    s = shapes[src]; t = shapes[tgt]
    scy = s["y"] + s["h"]/2
    tcy = t["y"] + t["h"]/2
    sx_r = s["x"] + s["w"]      # porta de saída: direita-centro
    tx_l = t["x"]               # porta de entrada: esquerda-centro
    if abs(scy - tcy) < 1:      # mesma linha -> reto
        wp = [(sx_r, scy), (tx_l, tcy)]
        lxy = (sx_r + 6, scy - 18)          # rótulo logo após a saída
    else:                       # cotovelo no x médio
        midx = (sx_r + tx_l) / 2
        wp = [(sx_r, scy), (midx, scy), (midx, tcy), (tx_l, tcy)]
        lxy = (midx - 10, (scy + tcy) / 2 - 8)  # rótulo no trecho vertical do cotovelo
    return wp, lxy

# ======================================================================
# PROCESSO 1 — Entrega e Correção de Atividade  (Professor/Sistema/Estudante)
# ======================================================================
P1 = "Process_EntregaCorrecao"
add_pool("Pool_EntregaCorrecao", "Entrega e Correção de Atividade", P1, 80,
         [("Lane_Professor", "Professor", 150, None),
          ("Lane_SistemaEC", "Sistema", 260, None),
          ("Lane_Estudante", "Estudante", 150, None)])

# nós
add_node(P1, "Start_AtividadePronta", "event", "start", "Lane_Professor", 0, "mid",
         "Atividade pronta")
add_node(P1, "Task_PublicarAtividade", "task", "userTask", "Lane_Professor", 1, "mid",
         "Publicar atividade (com prazo)", "user")
add_node(P1, "Task_NotificarTurma", "task", "sendTask", "Lane_SistemaEC", 2, "mid",
         "Notificar estudantes (cadência)", "send")
add_node(P1, "Task_EnviarEntrega", "task", "userTask", "Lane_Estudante", 3, "mid",
         "Elaborar e enviar entrega", "user")
add_node(P1, "Gw_DentroPrazo", "gateway", "exclusiveGateway", "Lane_SistemaEC", 4, "mid",
         "Dentro do prazo?", marker=True)
add_node(P1, "Task_RegistrarEntregue", "task", "serviceTask", "Lane_SistemaEC", 5, "up",
         "Registrar como Entregue", "system")
add_node(P1, "Task_RegistrarAtrasada", "task", "serviceTask", "Lane_SistemaEC", 5, "down",
         "Registrar como Atrasada", "system")
add_node(P1, "Task_CorrigirEntrega", "task", "userTask", "Lane_Professor", 6, "mid",
         "Corrigir entrega", "user")
add_node(P1, "Task_PublicarNota", "task", "userTask", "Lane_Professor", 7, "mid",
         "Publicar nota", "user")
add_node(P1, "Task_EmitirEvento", "task", "sendTask", "Lane_SistemaEC", 8, "mid",
         "Emitir evento e notificar", "send")
add_node(P1, "Task_ConsultarNota", "task", "userTask", "Lane_Estudante", 9, "mid",
         "Consultar nota e feedback", "user")
add_node(P1, "End_Fim", "event", "end", "Lane_Estudante", 10, "mid", "Fim")

# fluxos
add_flow(P1, "f1", "Start_AtividadePronta", "Task_PublicarAtividade")
add_flow(P1, "f2", "Task_PublicarAtividade", "Task_NotificarTurma")
add_flow(P1, "f3", "Task_NotificarTurma", "Task_EnviarEntrega")
add_flow(P1, "f4", "Task_EnviarEntrega", "Gw_DentroPrazo")
add_flow(P1, "f5", "Gw_DentroPrazo", "Task_RegistrarEntregue", "Sim")
add_flow(P1, "f6", "Gw_DentroPrazo", "Task_RegistrarAtrasada", "Não")
add_flow(P1, "f7", "Task_RegistrarEntregue", "Task_CorrigirEntrega")
add_flow(P1, "f8", "Task_RegistrarAtrasada", "Task_CorrigirEntrega")
add_flow(P1, "f9", "Task_CorrigirEntrega", "Task_PublicarNota")
add_flow(P1, "f10", "Task_PublicarNota", "Task_EmitirEvento")
add_flow(P1, "f11", "Task_EmitirEvento", "Task_ConsultarNota")
add_flow(P1, "f12", "Task_ConsultarNota", "End_Fim")

# anotações (rastreabilidade das regras de negócio)
add_anno(P1, "Ann_RN07", "Cadência por estudante (RN07 / Modo Foco)",
         col_x(2)-20, 690, 185, 56, "Task_NotificarTurma")
add_anno(P1, "Ann_RN03", "Prazo aceita ou bloqueia atraso (RN03)",
         col_x(4)-35, 690, 175, 56, "Gw_DentroPrazo")
add_anno(P1, "Ann_RN05", "Nota só visível após publicação (RN05)",
         col_x(7)-20, 690, 185, 56, "Task_PublicarNota")

# ======================================================================
# PROCESSO 2 — Notificações Adaptativas / Modo Foco  (Estudante/Sistema)
# ======================================================================
P2 = "Process_ModoFoco"
add_pool("Pool_ModoFoco", "Notificações Adaptativas (Modo Foco)", P2, 840,
         [("Lane_EstudanteMF", "Estudante", 150, None),
          ("Lane_SistemaMF", "Sistema", 230, None)])

add_node(P2, "Start_AjustarNotif", "event", "start", "Lane_EstudanteMF", 0, "mid",
         "Quer ajustar notificações")
add_node(P2, "Task_AbrirPref", "task", "userTask", "Lane_EstudanteMF", 1, "mid",
         "Abrir preferências de notificação", "user")
add_node(P2, "Task_SelecionarCadencia", "task", "userTask", "Lane_EstudanteMF", 2, "mid",
         "Selecionar cadência de notificação", "user")
add_node(P2, "Task_ValidarPref", "task", "serviceTask", "Lane_SistemaMF", 3, "mid",
         "Validar preferências", "system")
add_node(P2, "Gw_PrefValida", "gateway", "exclusiveGateway", "Lane_SistemaMF", 4, "mid",
         "Configuração válida?", marker=True)
add_node(P2, "Task_SalvarPref", "task", "serviceTask", "Lane_SistemaMF", 5, "mid",
         "Salvar preferências (Modo Foco)", "system")
add_node(P2, "End_Invalida", "event", "end", "Lane_SistemaMF", 5, "down",
         "Configuração inválida")
add_node(P2, "Task_AplicarMotor", "task", "serviceTask", "Lane_SistemaMF", 6, "mid",
         "Aplicar ao motor de eventos", "system")
add_node(P2, "Task_ConfirmarAluno", "task", "sendTask", "Lane_SistemaMF", 7, "mid",
         "Confirmar ao estudante", "send")
add_node(P2, "End_Aplicada", "event", "end", "Lane_EstudanteMF", 8, "mid",
         "Preferências aplicadas")

add_flow(P2, "g1", "Start_AjustarNotif", "Task_AbrirPref")
add_flow(P2, "g2", "Task_AbrirPref", "Task_SelecionarCadencia")
add_flow(P2, "g3", "Task_SelecionarCadencia", "Task_ValidarPref")
add_flow(P2, "g4", "Task_ValidarPref", "Gw_PrefValida")
add_flow(P2, "g5", "Gw_PrefValida", "Task_SalvarPref", "Sim")
add_flow(P2, "g6", "Gw_PrefValida", "End_Invalida", "Não")
add_flow(P2, "g7", "Task_SalvarPref", "Task_AplicarMotor")
add_flow(P2, "g8", "Task_AplicarMotor", "Task_ConfirmarAluno")
add_flow(P2, "g9", "Task_ConfirmarAluno", "End_Aplicada")

add_anno(P2, "Ann_Cadencia", "Cadências configuráveis (RN07)",
         col_x(2)+5, 1160, 165, 52, "Task_SelecionarCadencia")
add_anno(P2, "Ann_Inovacao", "Funcionalidade Inovadora: Modo Foco",
         col_x(6)-10, 1160, 180, 52, "Task_AplicarMotor")

# ======================================================================
# PROCESSO 3 — Formação de Grupo de Trabalho  (Estudante/Sistema)
# ======================================================================
P3 = "Process_FormacaoGrupo"
add_pool("Pool_FormacaoGrupo", "Formação de Grupo de Trabalho", P3, 1260,
         [("Lane_EstudanteGR", "Estudante", 150, None),
          ("Lane_SistemaGR", "Sistema", 230, None)])

add_node(P3, "Start_GrupoDisp", "event", "start", "Lane_EstudanteGR", 0, "mid",
         "Atividade em grupo disponível")
add_node(P3, "Task_CriarEntrar", "task", "userTask", "Lane_EstudanteGR", 1, "mid",
         "Criar grupo ou entrar em grupo existente", "user")
add_node(P3, "Task_ValidarRegras", "task", "serviceTask", "Lane_SistemaGR", 2, "mid",
         "Validar regras (tamanho, 1 grupo por atividade)", "system")
add_node(P3, "Gw_FormacaoOk", "gateway", "exclusiveGateway", "Lane_SistemaGR", 3, "mid",
         "Formação permitida?", marker=True)
add_node(P3, "Task_RegistrarMembro", "task", "serviceTask", "Lane_SistemaGR", 4, "mid",
         "Registrar participação no grupo", "system")
add_node(P3, "End_Recusada", "event", "end", "Lane_SistemaGR", 4, "down",
         "Formação recusada")
add_node(P3, "Task_NotificarMembros", "task", "sendTask", "Lane_SistemaGR", 5, "mid",
         "Notificar membros do grupo", "send")
add_node(P3, "Gw_Fechado", "gateway", "exclusiveGateway", "Lane_SistemaGR", 6, "mid",
         "Grupo completo ou prazo encerrado?", marker=True)
add_node(P3, "Task_TravarGrupo", "task", "serviceTask", "Lane_SistemaGR", 7, "mid",
         "Travar grupo e habilitar entrega coletiva", "system")
add_node(P3, "End_Aberto", "event", "end", "Lane_EstudanteGR", 7, "mid",
         "Grupo aberto (aguardando prazo)")
add_node(P3, "End_Pronto", "event", "end", "Lane_EstudanteGR", 8, "mid",
         "Grupo pronto para entrega")

add_flow(P3, "h1", "Start_GrupoDisp", "Task_CriarEntrar")
add_flow(P3, "h2", "Task_CriarEntrar", "Task_ValidarRegras")
add_flow(P3, "h3", "Task_ValidarRegras", "Gw_FormacaoOk")
add_flow(P3, "h4", "Gw_FormacaoOk", "Task_RegistrarMembro", "Sim")
add_flow(P3, "h5", "Gw_FormacaoOk", "End_Recusada", "Não")
add_flow(P3, "h6", "Task_RegistrarMembro", "Task_NotificarMembros")
add_flow(P3, "h7", "Task_NotificarMembros", "Gw_Fechado")
add_flow(P3, "h8", "Gw_Fechado", "End_Aberto", "Não")
add_flow(P3, "h9", "Gw_Fechado", "Task_TravarGrupo", "Sim")
add_flow(P3, "h10", "Task_TravarGrupo", "End_Pronto")

add_anno(P3, "Ann_RN09", "Tamanho e 1 grupo por atividade (RN09)",
         col_x(2)+5, 1660, 175, 52, "Task_ValidarRegras")
add_anno(P3, "Ann_RN10", "Entrega e nota por grupo (RN10)",
         col_x(7)-15, 1660, 175, 52, "Task_TravarGrupo")

# ----------------------------------------------------------------------
# Largura dos pools/lanes (a partir do conteúdo)
# ----------------------------------------------------------------------
max_right = max(s["x"] + s["w"] for s in shapes.values())
POOL_W = max_right - POOL_X + RIGHT_MARGIN
for p in pools:
    p["x"] = POOL_X
    p["w"] = POOL_W
for l in lanes:
    l["x"] = POOL_X + LABEL_BAND
    l["w"] = POOL_W - LABEL_BAND

# ======================================================================
# EMISSÃO DO XML
# ======================================================================
def el_node(n):
    tag = {"start": "startEvent", "end": "endEvent",
           "userTask": "userTask", "serviceTask": "serviceTask",
           "sendTask": "sendTask", "exclusiveGateway": "exclusiveGateway"}[n["kind"]]
    name = escape(n["name"])
    lines = [f'    <bpmn:{tag} id="{n["id"]}" name="{name}">']
    for i in n["inc"]:
        lines.append(f'      <bpmn:incoming>{i}</bpmn:incoming>')
    for o in n["out"]:
        lines.append(f'      <bpmn:outgoing>{o}</bpmn:outgoing>')
    # data output association (dentro da serviceTask)
    for do in processes_cur["dataouts"] if False else []:
        pass
    lines.append(f'    </bpmn:{tag}>')
    return "\n".join(lines)

def build_process_xml(proc_id):
    pr = processes[proc_id]
    out = [f'  <bpmn:process id="{proc_id}" name="{escape(pr["name"])}" isExecutable="true">']
    # laneSet
    pool = next(p for p in pools if p["proc"] == proc_id)
    out.append(f'    <bpmn:laneSet id="LaneSet_{proc_id}">')
    for lane in pr["lanes"]:
        out.append(f'      <bpmn:lane id="{lane["id"]}" name="{escape(lane["name"])}">')
        for ref in lane["refs"]:
            out.append(f'        <bpmn:flowNodeRef>{ref}</bpmn:flowNodeRef>')
        out.append('      </bpmn:lane>')
    out.append('    </bpmn:laneSet>')
    # data stores
    for ds in pr["datastores"]:
        out.append(f'    <bpmn:dataStoreReference id="{ds["id"]}" name="{escape(ds["name"])}" />')
    # nós
    dataouts_by_task = {}
    for do in pr["dataouts"]:
        dataouts_by_task.setdefault(do["task"], []).append(do)
    for n in pr["nodes"]:
        tag = {"start": "startEvent", "end": "endEvent",
               "userTask": "userTask", "serviceTask": "serviceTask",
               "sendTask": "sendTask", "exclusiveGateway": "exclusiveGateway"}[n["kind"]]
        out.append(f'    <bpmn:{tag} id="{n["id"]}" name="{escape(n["name"])}">')
        for i in n["inc"]:
            out.append(f'      <bpmn:incoming>{i}</bpmn:incoming>')
        for o in n["out"]:
            out.append(f'      <bpmn:outgoing>{o}</bpmn:outgoing>')
        for do in dataouts_by_task.get(n["id"], []):
            out.append(f'      <bpmn:dataOutputAssociation id="{do["id"]}">')
            out.append(f'        <bpmn:targetRef>{do["ds"]}</bpmn:targetRef>')
            out.append('      </bpmn:dataOutputAssociation>')
        out.append(f'    </bpmn:{tag}>')
    # fluxos
    for f in pr["flows"]:
        nm = f' name="{escape(f["name"])}"' if f["name"] else ""
        out.append(f'    <bpmn:sequenceFlow id="{f["id"]}"{nm} sourceRef="{f["src"]}" targetRef="{f["tgt"]}" />')
    # anotações + associações
    for a in pr["annos"]:
        out.append(f'    <bpmn:textAnnotation id="{a["id"]}">')
        out.append(f'      <bpmn:text>{escape(a["text"])}</bpmn:text>')
        out.append('    </bpmn:textAnnotation>')
    for asc in pr["assocs"]:
        out.append(f'    <bpmn:association id="{asc["id"]}" sourceRef="{asc["src"]}" targetRef="{asc["tgt"]}" />')
    out.append('  </bpmn:process>')
    return "\n".join(out)

def build_di():
    out = ['  <bpmndi:BPMNDiagram id="BPMNDiagram_1">',
           '    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_Catedra">']
    # pools
    for p in pools:
        out.append(f'      <bpmndi:BPMNShape id="{p["id"]}_di" bpmnElement="{p["id"]}" isHorizontal="true">')
        out.append(f'        <dc:Bounds x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}" />')
        out.append('      </bpmndi:BPMNShape>')
    # lanes
    for l in lanes:
        out.append(f'      <bpmndi:BPMNShape id="{l["id"]}_di" bpmnElement="{l["id"]}" isHorizontal="true">')
        out.append(f'        <dc:Bounds x="{l["x"]}" y="{l["y"]}" width="{l["w"]}" height="{l["h"]}" />')
        out.append('      </bpmndi:BPMNShape>')
    # nós (shapes)
    for nid, s in shapes.items():
        if s["stype"] in ("anno", "datastore"):
            continue
        color_attr = ""
        if s["stype"] == "task" or (s["stype"] == "gateway"):
            if s["fill"] != "#ffffff":
                color_attr = (f' bioc:stroke="{s["stroke"]}" bioc:fill="{s["fill"]}"'
                              f' color:background-color="{s["fill"]}" color:border-color="{s["stroke"]}"')
        marker = ' isMarkerVisible="true"' if s.get("marker") else ""
        out.append(f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{nid}"{marker}{color_attr}>')
        out.append(f'        <dc:Bounds x="{int(s["x"])}" y="{int(s["y"])}" width="{int(s["w"])}" height="{int(s["h"])}" />')
        # label para eventos e gateways (texto fora da forma)
        if s["stype"] in ("event", "gateway"):
            lx = int(s["x"] + s["w"]/2 - 45)
            ly = int(s["y"] + s["h"] + 4)
            out.append('        <bpmndi:BPMNLabel>')
            out.append(f'          <dc:Bounds x="{lx}" y="{ly}" width="90" height="27" />')
            out.append('        </bpmndi:BPMNLabel>')
        out.append('      </bpmndi:BPMNShape>')
    # datastores
    for nid, s in shapes.items():
        if s["stype"] != "datastore":
            continue
        out.append(f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{nid}">')
        out.append(f'        <dc:Bounds x="{int(s["x"])}" y="{int(s["y"])}" width="50" height="50" />')
        out.append('        <bpmndi:BPMNLabel>')
        out.append(f'          <dc:Bounds x="{int(s["x"]-30)}" y="{int(s["y"]+52)}" width="110" height="27" />')
        out.append('        </bpmndi:BPMNLabel>')
        out.append('      </bpmndi:BPMNShape>')
    # anotações
    for nid, s in shapes.items():
        if s["stype"] != "anno":
            continue
        out.append(f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{nid}">')
        out.append(f'        <dc:Bounds x="{int(s["x"])}" y="{int(s["y"])}" width="{int(s["w"])}" height="{int(s["h"])}" />')
        out.append('      </bpmndi:BPMNShape>')
    # arestas (edges) — fluxos, associações, data outputs
    for eid, e in edges.items():
        out.append(f'      <bpmndi:BPMNEdge id="{eid}_di" bpmnElement="{eid}">')
        for (x, y) in e["wp"]:
            out.append(f'        <di:waypoint x="{int(x)}" y="{int(y)}" />')
        if e.get("name"):
            lx, ly = e["label_xy"]
            out.append('        <bpmndi:BPMNLabel>')
            out.append(f'          <dc:Bounds x="{int(lx)}" y="{int(ly)}" width="40" height="20" />')
            out.append('        </bpmndi:BPMNLabel>')
        out.append('      </bpmndi:BPMNEdge>')
    out.append('    </bpmndi:BPMNPlane>')
    out.append('  </bpmndi:BPMNDiagram>')
    return "\n".join(out)

processes_cur = None  # (compat; não usado)

header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<bpmn:definitions '
          'xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" '
          'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
          'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" '
          'xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
          'xmlns:bioc="http://bpmn.io/schema/bpmn/biocolor/1.0" '
          'xmlns:color="http://www.omg.org/spec/BPMN/non-normative/color/1.0" '
          'xmlns:camunda="http://camunda.org/schema/1.0/bpmn" '
          'id="Definitions_Catedra" targetNamespace="http://bpmn.io/schema/bpmn" '
          'exporter="Claude AI" exporterVersion="1.0">')

collab = ['  <bpmn:collaboration id="Collaboration_Catedra">']
for p in pools:
    collab.append(f'    <bpmn:participant id="{p["id"]}" name="{escape(p["name"])}" processRef="{p["proc"]}" />')
collab.append('  </bpmn:collaboration>')

xml_parts = [header, "\n".join(collab),
             build_process_xml(P1), build_process_xml(P2), build_process_xml(P3),
             build_di(),
             '</bpmn:definitions>\n']
xml = "\n".join(xml_parts)

OUT = "bpmn/catedra-processos.bpmn"
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(xml)
print("BPMN escrito em", OUT, "-", len(xml.splitlines()), "linhas")

# ======================================================================
# PREVIEW (matplotlib) a partir das MESMAS coordenadas
# ======================================================================
def draw():
    all_x = [s["x"] for s in shapes.values()] + [p["x"] for p in pools]
    all_y = [s["y"] for s in shapes.values()] + [p["y"] for p in pools]
    all_x2 = [s["x"]+s["w"] for s in shapes.values()] + [p["x"]+p["w"] for p in pools]
    all_y2 = [s["y"]+s["h"] for s in shapes.values()] + [p["y"]+p["h"] for p in pools]
    minx, maxx = min(all_x)-20, max(all_x2)+20
    miny, maxy = min(all_y)-20, max(all_y2)+40
    fig, ax = plt.subplots(figsize=((maxx-minx)/90, (maxy-miny)/90))
    ax.set_xlim(minx, maxx); ax.set_ylim(maxy, miny)  # y invertido (BPMN cresce p/ baixo)
    ax.axis("off")

    # pools
    for p in pools:
        ax.add_patch(Rectangle((p["x"], p["y"]), p["w"], p["h"], fill=False,
                               edgecolor="#333", lw=1.5))
        ax.add_patch(Rectangle((p["x"], p["y"]), LABEL_BAND, p["h"], facecolor="#eee",
                               edgecolor="#333", lw=1.0))
        ax.text(p["x"]+LABEL_BAND/2, p["y"]+p["h"]/2, p["name"], rotation=90,
                ha="center", va="center", fontsize=8, fontweight="bold")
    # lanes
    for l in lanes:
        ax.add_patch(Rectangle((l["x"], l["y"]), l["w"], l["h"], fill=False,
                               edgecolor="#999", lw=0.8))
        ax.add_patch(Rectangle((l["x"], l["y"]), LABEL_BAND, l["h"], facecolor="#f6f6f6",
                               edgecolor="#999", lw=0.6))
        ax.text(l["x"]+LABEL_BAND/2, l["y"]+l["h"]/2, l["name"], rotation=90,
                ha="center", va="center", fontsize=7, color="#444")

    # edges primeiro (atrás)
    for eid, e in edges.items():
        xs = [w[0] for w in e["wp"]]; ys = [w[1] for w in e["wp"]]
        dashed = e.get("dashed", False)
        ax.add_line(Line2D(xs, ys, color="#555", lw=1.0,
                           linestyle="--" if dashed else "-"))
        # seta
        x0, y0 = e["wp"][-2]; x1, y1 = e["wp"][-1]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.0))
        if e.get("name"):
            lx, ly = e["label_xy"]
            ax.text(lx, ly, e["name"], fontsize=6.5, color="#222",
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))

    # shapes
    for nid, s in shapes.items():
        st = s["stype"]
        cx, cy = s["x"]+s["w"]/2, s["y"]+s["h"]/2
        if st == "task":
            ax.add_patch(FancyBboxPatch((s["x"], s["y"]), s["w"], s["h"],
                         boxstyle="round,pad=0,rounding_size=8",
                         facecolor=s["fill"], edgecolor=s["stroke"], lw=1.4))
            ax.text(cx, cy, s["label"], ha="center", va="center", fontsize=6.7,
                    wrap=True)
        elif st == "gateway":
            diamond = Polygon([(cx, s["y"]), (s["x"]+s["w"], cy),
                               (cx, s["y"]+s["h"]), (s["x"], cy)],
                              facecolor=s["fill"], edgecolor=s["stroke"], lw=1.4)
            ax.add_patch(diamond)
            ax.text(cx, cy, "×", ha="center", va="center", fontsize=11, color=s["stroke"])
            ax.text(cx, s["y"]+s["h"]+12, s["label"], ha="center", va="top", fontsize=6.5)
        elif st == "event":
            ax.add_patch(Circle((cx, cy), s["w"]/2, facecolor="#fff",
                                edgecolor=s["stroke"], lw=1.6))
            ax.text(cx, s["y"]+s["h"]+12, s["label"], ha="center", va="top", fontsize=6.5)
        elif st == "datastore":
            ax.add_patch(Rectangle((s["x"], s["y"]), s["w"], s["h"], facecolor="#fafafa",
                                   edgecolor="#666", lw=1.0))
            ax.text(cx, s["y"]+s["h"]+10, s["label"], ha="center", va="top", fontsize=6, color="#444")
        elif st == "anno":
            ax.add_patch(Rectangle((s["x"], s["y"]), s["w"], s["h"], facecolor="#fffef2",
                                   edgecolor="#999", lw=0.7, linestyle="--"))
            ax.text(cx, cy, s["label"], ha="center", va="center", fontsize=6, color="#555")

    plt.tight_layout()
    fig.savefig("bpmn/catedra-processos-preview.png", dpi=130, bbox_inches="tight")
    print("Preview salvo em bpmn/catedra-processos-preview.png")

draw()
