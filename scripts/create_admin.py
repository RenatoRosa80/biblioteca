from pathlib import Path
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    email = "admin@biblioteca.com"
    senha = "admin"
    u = Usuario.query.filter_by(email=email).first()
    if u:
        print("Admin já existe:", u.email)
    else:
        admin = Usuario(
            nome="Administrador",
            email=email,
            senha=generate_password_hash(senha, method="pbkdf2:sha256"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin criado:", email, "/", senha)