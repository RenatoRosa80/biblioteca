from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from utils.pdf import gerar_relatorio_emprestimos, gerar_relatorio_vendas
from datetime import datetime

# ---------------------- CONFIGURAÇÕES ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'biblioteca.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ---------------------- MODELOS ----------------------
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150))
    autor = db.Column(db.String(100))
    genero = db.Column(db.String(50))
    preco = db.Column(db.Float)
    disponivel = db.Column(db.Boolean, default=True)
    # novos campos de status
    emprestado = db.Column(db.Boolean, default=False)
    vendido = db.Column(db.Boolean, default=False)
    devolvido = db.Column(db.Boolean, default=False)

    @classmethod
    def contar_livros(cls):
        return cls.query.count()

class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    data_emprestimo = db.Column(db.DateTime, default=datetime.now)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    usuario = db.relationship('Usuario')
    livro = db.relationship('Livro')

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    preco = db.Column(db.Float)
    data_venda = db.Column(db.DateTime, default=datetime.now)
    usuario = db.relationship('Usuario')
    livro = db.relationship('Livro')

# ---------------------- LOGIN ----------------------
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ---------------------- ROTAS PRINCIPAIS ----------------------
@app.route('/')
@login_required
def index():
    livros = Livro.query.all()
    usuarios = Usuario.query.all() if current_user.is_admin else []
    return render_template('index.html', livros=livros, usuarios=usuarios)

# ...existing code...
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        print("DEBUG login attempt:", repr(email))
        user = Usuario.query.filter_by(email=email).first()
        print("DEBUG user found:", bool(user))
        if user:
            print("DEBUG stored hash:", user.senha)
            from werkzeug.security import check_password_hash
            print("DEBUG password match:", check_password_hash(user.senha, senha))
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')
# ...existing code...

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------------- RELATÓRIOS PDF ----------------------
@app.route("/relatorio/emprestimos")
@login_required
def relatorio_emprestimos():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    emprestimos = Emprestimo.query.all()
    caminho = os.path.join("relatorio_emprestimos.pdf")
    gerar_relatorio_emprestimos(emprestimos, caminho)
    return send_file(caminho, as_attachment=True)

@app.route("/relatorio/vendas")
@login_required
def relatorio_vendas():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    vendas = Venda.query.all()
    caminho = os.path.join("relatorio_vendas.pdf")
    gerar_relatorio_vendas(vendas, caminho)
    return send_file(caminho, as_attachment=True)

# ---------------------- CRUD LIVROS ----------------------
@app.route('/livro/novo', methods=['GET', 'POST'])
@login_required
def novo_livro():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        genero = request.form['genero']
        preco = float(request.form['preco'])
        livro = Livro(titulo=titulo, autor=autor, genero=genero, preco=preco, disponivel=True)
        db.session.add(livro)
        db.session.commit()
        flash("Livro cadastrado com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('novo_livro.html')

@app.route('/livro/editar/<int:livro_id>', methods=['GET', 'POST'])
@login_required
def editar_livro(livro_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    livro = Livro.query.get_or_404(livro_id)
    if request.method == 'POST':
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.genero = request.form['genero']
        livro.preco = float(request.form['preco'])
        # status checkboxes
        livro.disponivel = 'disponivel' in request.form
        livro.emprestado = 'emprestado' in request.form
        livro.vendido = 'vendido' in request.form
        livro.devolvido = 'devolvido' in request.form

        # simples regra: se vendido => não disponível e não emprestado
        if livro.vendido:
            livro.disponivel = False
            livro.emprestado = False

        db.session.commit()
        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('editar_livro.html', livro=livro)

@app.route('/livro/deletar/<int:livro_id>')
@login_required
def deletar_livro(livro_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    livro = Livro.query.get_or_404(livro_id)
    db.session.delete(livro)
    db.session.commit()
    flash("Livro deletado com sucesso!", "success")
    return redirect(url_for('index'))

# ---------------------- CRUD USUÁRIOS ----------------------
@app.route('/usuario/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'], method='pbkdf2:sha256')
        is_admin = 'is_admin' in request.form
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado!", "danger")
            return redirect(url_for('cadastrar_usuario'))
        usuario = Usuario(nome=nome, email=email, senha=senha, is_admin=is_admin)
        db.session.add(usuario)
        db.session.commit()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('cadastrar_usuario.html')

@app.route('/usuario/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    usuario = Usuario.query.get_or_404(usuario_id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        if request.form['senha']:
            usuario.senha = generate_password_hash(request.form['senha'], method='pbkdf2:sha256')
        usuario.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuario/deletar/<int:usuario_id>')
@login_required
def deletar_usuario(usuario_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash("Você não pode deletar seu próprio usuário!", "danger")
        return redirect(url_for('index'))
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário deletado com sucesso!", "success")
    return redirect(url_for('index'))

@app.route('/quantidade_livros')
@login_required
def quantidade_livros():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    # Contagens
    total = Livro.query.count()
    emprestados = Emprestimo.query.filter(Emprestimo.data_devolucao == None).count()
    vendidos = Venda.query.count()
    disponiveis = Livro.query.filter_by(disponivel=True).count()
    devolvidos = Emprestimo.query.filter(Emprestimo.data_devolucao != None).count()
    
    # Listas detalhadas
    emprestimos_ativos = Emprestimo.query\
        .filter(Emprestimo.data_devolucao == None)\
        .order_by(Emprestimo.data_emprestimo.desc())\
        .limit(10)\
        .all()
    
    emprestimos_devolvidos = Emprestimo.query\
        .filter(Emprestimo.data_devolucao != None)\
        .order_by(Emprestimo.data_devolucao.desc())\
        .limit(10)\
        .all()
    
    vendas_recentes = Venda.query\
        .order_by(Venda.data_venda.desc())\
        .limit(10)\
        .all()

    return render_template('quantidade_livros.html',
                         total=total,
                         emprestados=emprestados,
                         vendidos=vendidos,
                         disponiveis=disponiveis,
                         devolvidos=devolvidos,
                         emprestimos_ativos=emprestimos_ativos,
                         emprestimos_devolvidos=emprestimos_devolvidos,
                         vendas_recentes=vendas_recentes)

@app.route('/devolver_livro/<int:emprestimo_id>')
@login_required
def devolver_livro(emprestimo_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
    emprestimo.data_devolucao = datetime.now()
    emprestimo.livro.disponivel = True
    db.session.commit()
    
    flash("Livro devolvido com sucesso!", "success")
    return redirect(url_for('quantidade_livros'))

# ---------------------- INICIALIZAÇÃO ----------------------
def init_database():
    """Initialize database with tables and admin user"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check/create admin user
        admin = Usuario.query.filter_by(email='admin@biblioteca.com').first()
        if not admin:
            admin = Usuario(
                nome='Administrador',
                email='admin@biblioteca.com',
                senha=generate_password_hash('admin', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")

def run_app():
    """Initialize and run the application"""
    if not os.path.exists('biblioteca.db'):
        init_database()
        
        with app.app_context():
            # Add sample books
            livros = [
                Livro(titulo='Dom Casmurro', autor='Machado de Assis', genero='Romance', preco=29.90),
                Livro(titulo='Memórias Póstumas de Brás Cubas', autor='Machado de Assis', genero='Romance', preco=34.90),
                Livro(titulo='O Pequeno Príncipe', autor='Antoine de Saint-Exupéry', genero='Infantil', preco=25.00),
                Livro(titulo='1984', autor='George Orwell', genero='Ficção Científica', preco=35.50),
                Livro(titulo='Senhora', autor='José de Alencar', genero='Romance', preco=29.90),
                Livro(titulo='Iracema', autor='José de Alencar', genero='Romance', preco=27.90),
                Livro(titulo='Romanceiro da Inconfidência', autor='Cecília Meireles', genero='Poesia', preco=39.90),
                Livro(titulo='A Rosa do Povo', autor='Carlos Drummond de Andrade', genero='Poesia', preco=42.90),
                Livro(titulo='A Hora da Estrela', autor='Clarice Lispector', genero='Romance', preco=31.90),
                Livro(titulo='Vidas Secas', autor='Graciliano Ramos', genero='Romance', preco=37.90),
                Livro(titulo='A Rua dos Cataventos', autor='Mario Quintana', genero='Poesia', preco=29.90),
                Livro(titulo='Grande Sertão: Veredas', autor='Guimarães Rosa', genero='Romance', preco=59.90)
            ]
            db.session.add_all(livros)
            db.session.commit()
            print("Sample books added successfully")
    
    app.run(debug=True)

if __name__ == "__main__":
    run_app()