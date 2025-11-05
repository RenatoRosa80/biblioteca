from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta

# ---------------------- CONFIGURAÇÕES ----------------------
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'biblioteca.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
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

class Emprestimo(db.Model):
    __tablename__ = 'emprestimo' 
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    data_emprestimo = db.Column(db.DateTime, default=datetime.now)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    usuario = db.relationship('Usuario')
    livro = db.relationship('Livro')
    
    @property
    def dias_decorridos(self):
        if self.data_devolucao:
            return (self.data_devolucao - self.data_emprestimo).days
        return (datetime.now() - self.data_emprestimo).days
    
    @property
    def ativo(self):
        return self.data_devolucao is None

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    preco = db.Column(db.Float)
    data_venda = db.Column(db.DateTime, default=datetime.now)
    cancelada = db.Column(db.Boolean, default=False)
    usuario = db.relationship('Usuario')
    livro = db.relationship('Livro')

# ---------------------- LOGIN ----------------------

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ---------------------- ROTAS TEMPORÁRIAS PARA CORREÇÃO ----------------------

@app.route('/fix-database')
def fix_database():
    """Corrige a estrutura do banco de dados"""
    try:
        # Fecha conexões existentes
        db.session.close()
        
        # Usa SQLite diretamente para adicionar as colunas faltantes
        import sqlite3
        conn = sqlite3.connect('biblioteca.db')
        cursor = conn.cursor()
        
        # 🔥 CORREÇÃO: usar o nome correto da tabela
        cursor.execute("PRAGMA table_info(empresimo)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'data_devolucao' not in columns:
            cursor.execute("ALTER TABLE empresimo ADD COLUMN data_devolucao DATETIME")
            print("✅ Coluna data_devolucao adicionada!")
        
        # Verifica e adiciona coluna cancelada se não existir
        cursor.execute("PRAGMA table_info(venda)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'cancelada' not in columns:
            cursor.execute("ALTER TABLE venda ADD COLUMN cancelada BOOLEAN DEFAULT FALSE")
            print("✅ Coluna cancelada adicionada!")
        
        # 🔥 CORREÇÃO: renomear coluna data_empresimo para data_emprestimo se existir
        cursor.execute("PRAGMA table_info(empresimo)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'data_empresimo' in columns and 'data_emprestimo' not in columns:
            print("🔄 Renomeando coluna data_empresimo para data_emprestimo...")
            # SQLite não suporta RENAME COLUMN, então criamos uma nova tabela
            cursor.execute('''
                CREATE TABLE temp_empresimo (
                    id INTEGER PRIMARY KEY,
                    usuario_id INTEGER,
                    livro_id INTEGER,
                    data_emprestimo DATETIME,
                    data_devolucao DATETIME,
                    FOREIGN KEY (usuario_id) REFERENCES usuario (id),
                    FOREIGN KEY (livro_id) REFERENCES livro (id)
                )
            ''')
            cursor.execute('''
                INSERT INTO temp_empresimo (id, usuario_id, livro_id, data_emprestimo, data_devolucao)
                SELECT id, usuario_id, livro_id, data_empresimo, data_devolucao FROM empresimo
            ''')
            cursor.execute("DROP TABLE empresimo")
            cursor.execute("ALTER TABLE temp_empresimo RENAME TO empresimo")
            print("✅ Coluna renomeada com sucesso!")
        
        conn.commit()
        conn.close()
        
        return """
        <h1>✅ Banco de dados corrigido com sucesso!</h1>
        <p>As colunas necessárias foram adicionadas.</p>
        <a href="/" class="btn btn-primary">Ir para o Dashboard</a>
        """
        
    except Exception as e:
        return f"<h1>❌ Erro:</h1><p>{str(e)}</p>"

@app.route('/popular-biblioteca')
def popular_biblioteca():
    """Adiciona todos os livros do arquivo livros_exemplo.py à biblioteca"""
    try:
        # Importa os livros do arquivo externo
        try:
            from livros_exemplo import LIVROS_EXEMPLO
            livros_para_adicionar = LIVROS_EXEMPLO
            print(f"✅ Importado {len(livros_para_adicionar)} livros do arquivo livros_exemplo.py")
        except ImportError as e:
            return f"""
            <div style="padding: 20px; font-family: Arial, sans-serif;">
                <h1 style="color: red;">❌ Erro ao importar livros</h1>
                <p>Arquivo livros_exemplo.py não encontrado ou com erro.</p>
                <p><strong>Erro:</strong> {str(e)}</p>
                <p>Verifique se o arquivo existe na mesma pasta do app.py</p>
                <a href="/" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar</a>
            </div>
            """
        
        livros_adicionados = 0
        livros_duplicados = 0
        
        for livro_data in livros_para_adicionar:
            # Verifica se o livro já existe
            livro_existente = Livro.query.filter_by(
                titulo=livro_data["titulo"],
                autor=livro_data["autor"]
            ).first()
            
            if not livro_existente:
                livro = Livro(
                    titulo=livro_data["titulo"],
                    autor=livro_data["autor"],
                    genero=livro_data["genero"],
                    preco=livro_data["preco"],
                    disponivel=True
                )
                db.session.add(livro)
                livros_adicionados += 1
                print(f"✅ Adicionado: {livro_data['titulo']} - {livro_data['autor']}")
            else:
                livros_duplicados += 1
                print(f"⏭️  Já existe: {livro_data['titulo']} - {livro_data['autor']}")
        
        db.session.commit()
        
        return f"""
        <div style="padding: 20px; font-family: Arial, sans-serif;">
            <h1 style="color: green;">✅ Biblioteca populada com sucesso!</h1>
            <p><strong>Livros processados:</strong> {len(livros_para_adicionar)}</p>
            <p><strong>Novos livros adicionados:</strong> {livros_adicionados}</p>
            <p><strong>Livros já existentes:</strong> {livros_duplicados}</p>
            <p><strong>Total de livros na biblioteca:</strong> {Livro.query.count()}</p>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                <h3>📊 Resumo por Categoria:</h3>
                <p>🇧🇷 <strong>Autores Brasileiros:</strong> {len([l for l in livros_para_adicionar if l['autor'] in ['Machado de Assis', 'Aluísio Azevedo', 'José de Alencar', 'Carolina Maria de Jesus', 'João Guimarães Rosa', 'Raul Pompeia', 'Jorge Amado', 'Clarice Lispector', 'Graciliano Ramos', 'Pepetela']])} livros</p>
                <p>🇺🇸 <strong>Autores Americanos:</strong> {len([l for l in livros_para_adicionar if l['autor'] in ['George Orwell', 'J.D. Salinger', 'Harper Lee', 'F. Scott Fitzgerald', 'Herman Melville', 'John Steinbeck', 'Jack Kerouac', 'Alice Walker', 'Ray Bradbury']])} livros</p>
                <p>🇪🇺 <strong>Autores Europeus:</strong> {len([l for l in livros_para_adicionar if l['autor'] in ['Miguel de Cervantes', 'Jane Austen', 'Fiódor Dostoiévski', 'Liev Tolstói', 'Alexandre Dumas', 'Gustave Flaubert', 'James Joyce', 'Umberto Eco', 'Antoine de Saint-Exupéry']])} livros</p>
                <p>🇱🇦 <strong>Autores Latinos:</strong> {len([l for l in livros_para_adicionar if l['autor'] in ['Gabriel García Márquez', 'Julio Cortázar', 'Isabel Allende', 'Jorge Luis Borges', 'Carlos Fuentes', 'Juan Rulfo', 'Mario Vargas Llosa', 'Ernesto Sabato']])} livros</p>
                <p>🌟 <strong>Autores Contemporâneos:</strong> {len([l for l in livros_para_adicionar if l['autor'] in ['J.K. Rowling', 'Dan Brown', 'Markus Zusak', 'J.R.R. Tolkien', 'C.S. Lewis']])} livros</p>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Ver Biblioteca</a>
                <a href="/diagnostico" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Diagnóstico</a>
            </div>
        </div>
        """
    
    except Exception as e:
        return f"""
        <div style="padding: 20px; font-family: Arial, sans-serif;">
            <h1 style="color: red;">❌ Erro ao popular biblioteca:</h1>
            <p><strong>Erro:</strong> {str(e)}</p>
            <a href="/" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar</a>
        </div>
        """
        
        
@app.route('/diagnostico')
def diagnostico():
    """Página de diagnóstico detalhada"""
    total_livros = Livro.query.count()
    livros = Livro.query.all()
    livros_disponiveis = Livro.query.filter_by(disponivel=True).count()
    
    # Estatísticas por autor
    autores = {}
    for livro in livros:
        if livro.autor in autores:
            autores[livro.autor] += 1
        else:
            autores[livro.autor] = 1
    
    info = f"""
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h1>📊 Diagnóstico do Sistema</h1>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
            <div style="background: #007bff; color: white; padding: 15px; border-radius: 5px;">
                <h3>Total de Livros</h3>
                <p style="font-size: 24px; margin: 0;">{total_livros}</p>
            </div>
            <div style="background: #28a745; color: white; padding: 15px; border-radius: 5px;">
                <h3>Livros Disponíveis</h3>
                <p style="font-size: 24px; margin: 0;">{livros_disponiveis}</p>
            </div>
            <div style="background: #ffc107; color: black; padding: 15px; border-radius: 5px;">
                <h3>Autores Diferentes</h3>
                <p style="font-size: 24px; margin: 0;">{len(autores)}</p>
            </div>
        </div>
        
        <h3>📚 Lista de Livros no Banco:</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <thead>
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Título</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Autor</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Gênero</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Preço</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Disponível</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for livro in livros:
        status = "✅" if livro.disponivel else "❌"
        info += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{livro.titulo}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{livro.autor}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{livro.genero}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">R$ {livro.preco:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{status}</td>
                </tr>
        """
    
    info += """
            </tbody>
        </table>
        
        <h3>👤 Estatísticas por Autor:</h3>
        <ul>
    """
    
    for autor, quantidade in sorted(autores.items(), key=lambda x: x[1], reverse=True):
        info += f"<li><strong>{autor}:</strong> {quantidade} livro(s)</li>"
    
    info += """
        </ul>
        
        <div style="margin-top: 20px;">
            <a href="/popular-biblioteca" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Popular Biblioteca</a>
            <a href="/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ir para Dashboard</a>
        </div>
    </div>
    """
    
    return info


@app.route('/criar-admin')
def criar_admin():
    """Rota temporária para criar o usuário admin"""
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
        return """
        <h1>✅ Admin criado com sucesso!</h1>
        <p><strong>Email:</strong> admin@biblioteca.com</p>
        <p><strong>Senha:</strong> admin</p>
        <a href="/login" class="btn btn-primary">Fazer Login</a>
        """
    return "Admin já existe"

# ---------------------- ROTAS PRINCIPAIS ----------------------

@app.route('/')
@login_required
def index():
    # Estatísticas
    total_livros = Livro.query.count()
    livros_disponiveis = Livro.query.filter_by(disponivel=True).count()
    # 🔥 CORREÇÃO: usar o nome correto da tabela
    emprestimos_ativos = Emprestimo.query.filter_by(data_devolucao=None).count()
    total_vendas = Venda.query.filter_by(cancelada=False).count()
    
    # Dados para as tabelas
    livros = Livro.query.all()
    usuarios = Usuario.query.all() if current_user.is_admin else []
    # 🔥 CORREÇÃO: usar o nome correto da tabela
    emprestimos = Emprestimo.query.filter_by(data_devolucao=None).all()
    vendas = Venda.query.filter_by(cancelada=False).order_by(Venda.data_venda.desc()).limit(10).all()
    
    return render_template('index.html', 
                         livros=livros, 
                         usuarios=usuarios,
                         emprestimos=emprestimos,
                         vendas=vendas,
                         total_livros=total_livros,
                         livros_disponiveis=livros_disponiveis,
                         emprestimos_ativos=emprestimos_ativos,
                         total_vendas=total_vendas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login inválido', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ---------------------- EMPRÉSTIMOS ----------------------

@app.route('/emprestimo/novo', methods=['GET', 'POST'])
@login_required
def novo_emprestimo():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    if request.method == 'POST':
        livro_id = request.form['livro_id']
        usuario_id = request.form['usuario_id']
        
        livro = Livro.query.get(livro_id)
        usuario = Usuario.query.get(usuario_id)
        
        if not livro or not usuario:
            flash("Livro ou usuário não encontrado!", "danger")
            return redirect(url_for('novo_emprestimo'))
        
        if not livro.disponivel:
            flash("Livro não disponível para empréstimo!", "danger")
            return redirect(url_for('novo_emprestimo'))
        
        # Cria o empréstimo
        emprestimo = Emprestimo(usuario_id=usuario_id, livro_id=livro_id)
        livro.disponivel = False
        
        db.session.add(emprestimo)
        db.session.commit()
        
        flash(f'Empréstimo de "{livro.titulo}" para {usuario.nome} realizado com sucesso!', 'success')
        return redirect(url_for('index'))
    
    livros = Livro.query.filter_by(disponivel=True).all()
    usuarios = Usuario.query.all()
    return render_template('novo_emprestimo.html', livros=livros, usuarios=usuarios)

@app.route('/emprestimo/devolver/<int:emprestimo_id>')
@login_required
def devolver_emprestimo(emprestimo_id):
    emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
    
    if not current_user.is_admin and emprestimo.usuario_id != current_user.id:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    if emprestimo.data_devolucao:
        flash("Este empréstimo já foi devolvido!", "warning")
        return redirect(url_for('index'))
    
    # Marca como devolvido
    emprestimo.data_devolucao = datetime.now()
    emprestimo.livro.disponivel = True
    
    db.session.commit()
    flash(f'Livro "{emprestimo.livro.titulo}" devolvido com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/emprestimo/cancelar/<int:emprestimo_id>')
@login_required
def cancelar_emprestimo(emprestimo_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
    livro_titulo = emprestimo.livro.titulo
    
    # Libera o livro
    emprestimo.livro.disponivel = True
    db.session.delete(emprestimo)
    db.session.commit()
    
    flash(f'Empréstimo de "{livro_titulo}" cancelado com sucesso!', 'success')
    return redirect(url_for('index'))

# ---------------------- VENDAS ----------------------

@app.route('/venda/nova', methods=['GET', 'POST'])
@login_required
def nova_venda():
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    if request.method == 'POST':
        livro_id = request.form['livro_id']
        usuario_id = request.form['usuario_id']
        
        livro = Livro.query.get(livro_id)
        usuario = Usuario.query.get(usuario_id)
        
        if not livro or not usuario:
            flash("Livro ou usuário não encontrado!", "danger")
            return redirect(url_for('nova_venda'))
        
        if not livro.disponivel:
            flash("Livro não disponível para venda!", "danger")
            return redirect(url_for('nova_venda'))
        
        # Cria a venda
        venda = Venda(usuario_id=usuario_id, livro_id=livro_id, preco=livro.preco)
        livro.disponivel = False
        
        db.session.add(venda)
        db.session.commit()
        
        flash(f'Venda de "{livro.titulo}" para {usuario.nome} realizada com sucesso!', 'success')
        return redirect(url_for('index'))
    
    livros = Livro.query.filter_by(disponivel=True).all()
    usuarios = Usuario.query.all()
    return render_template('nova_venda.html', livros=livros, usuarios=usuarios)

@app.route('/venda/cancelar/<int:venda_id>')
@login_required
def cancelar_venda(venda_id):
    if not current_user.is_admin:
        flash("Acesso restrito!", "danger")
        return redirect(url_for("index"))
    
    venda = Venda.query.get_or_404(venda_id)
    
    if venda.cancelada:
        flash("Esta venda já foi cancelada!", "warning")
        return redirect(url_for('index'))
    
    # Marca como cancelada e libera o livro
    venda.cancelada = True
    venda.livro.disponivel = True
    
    db.session.commit()
    flash(f'Venda de "{venda.livro.titulo}" cancelada com sucesso!', 'success')
    return redirect(url_for('index'))

# ---------------------- RELATÓRIOS PDF ----------------------

def gerar_relatorio_emprestimos(emprestimos, caminho):
    # Implementação básica - você pode expandir isso
    with open(caminho, 'w') as f:
        f.write("Relatório de Empréstimos\n\n")
        for emp in emprestimos:
            f.write(f"Livro: {emp.livro.titulo} | Usuário: {emp.usuario.nome} | Data: {emp.data_emprestimo}\n")

def gerar_relatorio_vendas(vendas, caminho):
    # Implementação básica - você pode expandir isso
    with open(caminho, 'w') as f:
        f.write("Relatório de Vendas\n\n")
        for venda in vendas:
            if not venda.cancelada:
                f.write(f"Livro: {venda.livro.titulo} | Usuário: {venda.usuario.nome} | Valor: R$ {venda.preco:.2f}\n")

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
    vendas = Venda.query.filter_by(cancelada=False).all()
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
        livro.disponivel = 'disponivel' in request.form
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
    
    # Verifica se o livro está em empréstimo ou venda ativa
    emprestimo_ativo = Emprestimo.query.filter_by(livro_id=livro_id, data_devolucao=None).first()
    venda_ativa = Venda.query.filter_by(livro_id=livro_id, cancelada=False).first()
    
    if emprestimo_ativo:
        flash("Não é possível deletar um livro que está emprestado!", "danger")
        return redirect(url_for('index'))
    
    if venda_ativa:
        flash("Não é possível deletar um livro que foi vendido!", "danger")
        return redirect(url_for('index'))
    
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
    
    # Verifica se o usuário tem empréstimos ou vendas ativas
    emprestimos_ativos = Emprestimo.query.filter_by(usuario_id=usuario_id, data_devolucao=None).count()
    vendas_ativas = Venda.query.filter_by(usuario_id=usuario_id, cancelada=False).count()
    
    if emprestimos_ativos > 0:
        flash("Não é possível deletar usuário com empréstimos ativos!", "danger")
        return redirect(url_for('index'))
    
    if vendas_ativas > 0:
        flash("Não é possível deletar usuário com vendas ativas!", "danger")
        return redirect(url_for('index'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário deletado com sucesso!", "success")
    return redirect(url_for('index'))

# ---------------------- INICIALIZAÇÃO ----------------------

def init_db():
    """Inicializa o banco de dados com dados de exemplo"""
    with app.app_context():
        db.create_all()
        
        # Verifica se o admin já existe
        admin = Usuario.query.filter_by(email='admin@biblioteca.com').first()
        if not admin:
            # Cria admin
            admin = Usuario(
                nome='Administrador',
                email='admin@biblioteca.com',
                senha=generate_password_hash('admin', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Adiciona alguns livros básicos se a biblioteca estiver vazia
            if Livro.query.count() == 0:
                livros_basicos = [
                    Livro(titulo='Dom Casmurro', autor='Machado de Assis', genero='Romance', preco=35.90),
                    Livro(titulo='1984', autor='George Orwell', genero='Distopia', preco=42.90),
                    Livro(titulo='O Pequeno Príncipe', autor='Antoine de Saint-Exupéry', genero='Infantil', preco=25.00),
                ]
                
                for livro in livros_basicos:
                    db.session.add(livro)
            
            db.session.commit()
            print("✅ Banco de dados inicializado com sucesso!")

# ---------------------- EXECUÇÃO ----------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)