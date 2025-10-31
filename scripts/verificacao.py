from pathlib import Path
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import app, Usuario
from werkzeug.security import check_password_hash

with app.app_context():
    users = Usuario.query.all()
    print("Users found:", len(users))
    for u in users:
        print(u.id, u.email, u.nome, "check admin:", check_password_hash(u.senha, "admin"))