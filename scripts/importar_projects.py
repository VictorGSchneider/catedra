#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
importar_projects.py — cria um GitHub Project (v2) e importa o backlog do CSV.

O que faz:
  1. Cria o Project no seu usuário/organização.
  2. Cria campos personalizados a partir do CSV:
       - Tipo, Epic, Prioridade, Etapa  -> SINGLE_SELECT (opções vêm do CSV)
       - Story Points                   -> NUMBER
     (o GitHub Projects "standalone" não tem labels nativas; campos
      personalizados são o substituto correto)
  3. Cria um cartão (draft) por linha do CSV e preenche os campos.

Colunas esperadas no CSV (gestao/backlog-kanban.csv):
  Title, Tipo, Epic, Prioridade, Story Points, Status, Descricao
  (a coluna "Status" vira o campo "Etapa")

Pré-requisitos:
  - GitHub CLI (gh) instalado e autenticado COM o escopo 'project':
        gh auth login
        gh auth refresh -s project        # adiciona o escopo necessário
  - Python 3

Uso (a partir da raiz do repositório):
  python3 scripts/importar_projects.py
  # ou personalizando:
  python3 scripts/importar_projects.py \
      --owner "@me" \
      --title "Cátedra — Backlog" \
      --csv gestao/backlog-kanban.csv \
      --repo VictorGSchneider/catedra      # opcional: linka o projeto ao repo
"""

import argparse
import csv
import json
import os
import subprocess
import sys


def run(args, check=True):
    """Executa um comando e devolve o CompletedProcess."""
    p = subprocess.run(args, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write("\n[ERRO] falhou: %s\n%s\n" % (" ".join(args), p.stderr))
        sys.exit(1)
    return p


def run_json(args):
    p = run(args)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        sys.stderr.write("[ERRO] saída não-JSON de: %s\n%s\n" % (" ".join(args), p.stdout))
        sys.exit(1)


def uniques(rows, col):
    seen = []
    for r in rows:
        v = (r.get(col) or "").strip()
        if v and v not in seen:
            seen.append(v)
    return seen


def main():
    ap = argparse.ArgumentParser(description="Cria e popula um GitHub Project (v2) a partir do CSV.")
    ap.add_argument("--owner", default="@me", help="dono do projeto (default: @me)")
    ap.add_argument("--title", default="Cátedra — Backlog", help="título do projeto")
    ap.add_argument("--csv", default="gestao/backlog-kanban.csv", help="caminho do CSV")
    ap.add_argument("--repo", default=None, help="opcional: owner/repo para linkar o projeto")
    args = ap.parse_args()

    # Opera a partir da raiz do repositório (este script vive em <raiz>/scripts/)
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

    # ---- checagens -----------------------------------------------------------
    if subprocess.run(["gh", "--version"], capture_output=True).returncode != 0:
        sys.exit("gh (GitHub CLI) não encontrado. Instale em https://cli.github.com")

    chk = subprocess.run(["gh", "project", "list", "--owner", args.owner, "--limit", "1"],
                         capture_output=True, text=True)
    if chk.returncode != 0:
        sys.stderr.write(chk.stderr)
        sys.exit("\nFalta o escopo 'project' no gh. Rode:  gh auth refresh -s project")

    if not os.path.exists(args.csv):
        sys.exit("CSV não encontrado: %s" % args.csv)

    # ---- ler CSV -------------------------------------------------------------
    with open(args.csv, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows = [r for r in rows if (r.get("Title") or "").strip()]
    if not rows:
        sys.exit("CSV sem linhas válidas: %s" % args.csv)

    tipos = uniques(rows, "Tipo")
    epics = uniques(rows, "Epic")
    prioridades = uniques(rows, "Prioridade")
    etapas = uniques(rows, "Status")

    # ---- 1) criar projeto ----------------------------------------------------
    print("==> Criando projeto: %s (owner=%s)" % (args.title, args.owner))
    proj = run_json(["gh", "project", "create", "--owner", args.owner,
                     "--title", args.title, "--format", "json"])
    number = proj.get("number")
    proj_id = proj.get("id")
    url = proj.get("url", "")

    # fallback: localizar pelo título, caso o create não traga os campos
    if not number or not proj_id:
        lst = run_json(["gh", "project", "list", "--owner", args.owner, "--format", "json"])
        items = lst.get("projects", lst) if isinstance(lst, dict) else lst
        for p in (items or []):
            if p.get("title") == args.title:
                number, proj_id, url = p.get("number"), p.get("id"), p.get("url", url)
                break
    if not number or not proj_id:
        sys.exit("Não consegui obter o número/ID do projeto recém-criado.")
    number = str(number)
    print("    Projeto #%s  %s" % (number, url))

    # ---- 2) criar campos personalizados --------------------------------------
    def field_create(name, dtype, options=None):
        a = ["gh", "project", "field-create", number, "--owner", args.owner,
             "--name", name, "--data-type", dtype]
        if options:
            a += ["--single-select-options", ",".join(options)]
        run(a)
        print("    + campo: %s (%s)" % (name, dtype))

    print("==> Criando campos personalizados...")
    if tipos:
        field_create("Tipo", "SINGLE_SELECT", tipos)
    if epics:
        field_create("Epic", "SINGLE_SELECT", epics)
    if prioridades:
        field_create("Prioridade", "SINGLE_SELECT", prioridades)
    if etapas:
        field_create("Etapa", "SINGLE_SELECT", etapas)
    field_create("Story Points", "NUMBER")

    # ---- 3) mapear campos -> ids (e opções -> ids) ---------------------------
    fl = run_json(["gh", "project", "field-list", number, "--owner", args.owner, "--format", "json"])
    fields = fl.get("fields", fl) if isinstance(fl, dict) else fl
    fmap = {}
    for f in (fields or []):
        entry = {"id": f.get("id"), "options": {}}
        for opt in (f.get("options") or []):
            entry["options"][opt.get("name")] = opt.get("id")
        fmap[f.get("name")] = entry

    def set_single(item_id, field_name, value):
        value = (value or "").strip()
        if not value:
            return
        fe = fmap.get(field_name)
        if not fe:
            return
        oid = fe["options"].get(value)
        if not oid:
            print("        ! opção '%s' não existe em '%s' (pulando)" % (value, field_name))
            return
        run(["gh", "project", "item-edit", "--id", item_id, "--project-id", proj_id,
             "--field-id", fe["id"], "--single-select-option-id", oid], check=False)

    def set_number(item_id, field_name, value):
        value = (value or "").strip()
        if not value:
            return
        fe = fmap.get(field_name)
        if not fe:
            return
        run(["gh", "project", "item-edit", "--id", item_id, "--project-id", proj_id,
             "--field-id", fe["id"], "--number", value], check=False)

    # ---- 4) criar cartões e preencher ----------------------------------------
    total = len(rows)
    print("==> Importando %d itens (pode levar alguns minutos)..." % total)
    for i, r in enumerate(rows, 1):
        title = (r.get("Title") or "").strip()
        body = (r.get("Descricao") or "").strip()
        item = run_json(["gh", "project", "item-create", number, "--owner", args.owner,
                         "--title", title, "--body", body, "--format", "json"])
        item_id = item.get("id")
        print("    [%2d/%d] %s" % (i, total, title))
        if not item_id:
            print("        ! não obtive o ID do item (pulando campos)")
            continue
        set_single(item_id, "Tipo", r.get("Tipo"))
        set_single(item_id, "Epic", r.get("Epic"))
        set_single(item_id, "Prioridade", r.get("Prioridade"))
        set_single(item_id, "Etapa", r.get("Status"))
        set_number(item_id, "Story Points", r.get("Story Points"))

    # ---- 5) opcional: linkar ao repositório ----------------------------------
    if args.repo:
        lk = subprocess.run(["gh", "project", "link", number, "--owner", args.owner,
                             "--repo", args.repo], capture_output=True, text=True)
        if lk.returncode == 0:
            print("==> Projeto linkado ao repositório %s" % args.repo)
        else:
            print("!! Não consegui linkar ao repo automaticamente (faça pela UI se quiser):")
            print("   " + lk.stderr.strip())

    print("\n==> Concluído! Abra: %s" % url)
    print("    Dica: no board, use 'Group by: Etapa' para ver as colunas")
    print("          Backlog / To Do / Done, ou 'Group by: Epic' para ver por épico.")


if __name__ == "__main__":
    main()
