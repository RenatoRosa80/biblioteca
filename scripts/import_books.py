import sys
from pathlib import Path

# garante que a raiz do projeto (pasta acima de scripts) esteja no sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import os
import csv
import json
import argparse
from app import app as flask_app, db, Livro

def ensure_database():
    """Ensure database and tables exist"""
    with flask_app.app_context():
        db.create_all()
        print("Database tables created/verified.")

def parse_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return True
    return str(v).strip().lower() in ("1", "true", "t", "sim", "s", "yes", "y")

def import_from_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        livros = list(reader)
    return livros

def import_from_json(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data if isinstance(data, list) else []

def upsert_books(items, commit=True):
    inserted = 0
    with flask_app.app_context():
        # Ensure database exists before attempting operations
        ensure_database()
        
        for row in items:
            titulo = (row.get('titulo') or row.get('title') or "").strip()
            autor = (row.get('autor') or row.get('author') or "").strip()
            genero = (row.get('genero') or row.get('genre') or "").strip()
            preco_raw = row.get('preco') or row.get('price') or 0
            try:
                preco = float(preco_raw) if preco_raw != "" else 0.0
            except Exception:
                preco = 0.0
            disponivel = parse_bool(row.get('disponivel', row.get('available', True)))

            if not titulo or not autor:
                continue

            # evita duplicatas por título+autor
            exists = Livro.query.filter_by(titulo=titulo, autor=autor).first()
            if exists:
                exists.genero = genero or exists.genero
                exists.preco = preco or exists.preco
                exists.disponivel = disponivel
            else:
                livro = Livro(titulo=titulo, autor=autor, genero=genero, 
                             preco=preco, disponivel=disponivel)
                db.session.add(livro)
                inserted += 1
        
        if commit:
            db.session.commit()
            print(f"Committed {inserted} new books to database")
    return inserted

def main():
    parser = argparse.ArgumentParser(
        description="Importar livros para a base (CSV ou JSON).")
    parser.add_argument("file", 
        help="Caminho para arquivo .csv ou .json (relativo à raiz do projeto ou absoluto)")
    args = parser.parse_args()
    raw = args.file
    print("DEBUG: caminho recebido ->", repr(raw))

    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = project_root / p
    p = p.resolve(strict=False)
    print("DEBUG: caminho normalizado ->", str(p))

    if not p.exists():
        parent = p.parent
        print(f"Arquivo não encontrado: {p}")
        if parent.exists():
            print(f"Conteúdo da pasta {parent}:")
            for f in sorted(parent.iterdir()):
                print("  ", f.name)
        else:
            print(f"Pasta {parent} não existe. Conteúdo da raiz do projeto ({project_root}):")
            for f in sorted(project_root.iterdir()):
                print("  ", f.name)
        raise SystemExit(1)

    ext = p.suffix.lower()
    if ext == ".csv":
        items = import_from_csv(str(p))
    elif ext == ".json":
        items = import_from_json(str(p))
    else:
        raise SystemExit("Formato não suportado. Use .csv ou .json")

    inserted = upsert_books(items)
    print(f"Importação concluída. {inserted} novos livros inseridos/atualizados.")

if __name__ == "__main__":
    main()