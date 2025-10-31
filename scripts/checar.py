from app import app, db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    users = Usuario.query.all()
    if not users:
        print("Nenhum usuário no banco de dados.")
    else:
        print(f"{len(users)} usuário(s) encontrados:")
        for u in users:
            print(f"  id={u.id} | nome={u.nome} | email={u.email} | hash={u.senha}")
            print("    check 'admin':", check_password_hash(u.senha, "admin"))

    admin_email = "admin@biblioteca.com"
    admin = Usuario.query.filter_by(email=admin_email).first()
    if not admin:
        senha = "admin"
        admin = Usuario(
            nome="Administrador",
            email=admin_email,
            senha=generate_password_hash(senha, method="pbkdf2:sha256"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin criado: {admin_email} / {senha}")
    else:
        print(f"Admin já existe: {admin.email}")