from pathlib import Path
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import app, db, Usuario
import os

with app.app_context():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print("SQLALCHEMY_DATABASE_URI:", uri)
    if uri and uri.startswith("sqlite:///"):
        path = uri.replace("sqlite:///", "")
        print("Resolved DB path:", os.path.abspath(path))
    else:
        print("DB is not sqlite or URI not recognized")

    # garante tabelas no DB que o app usa
    db.create_all()
    users = Usuario.query.all()
    print("Users found:", len(users))
    for u in users:
        print(f"  id={u.id} | email={u.email} | nome={u.nome}")