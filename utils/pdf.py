from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def gerar_relatorio_emprestimos(emprestimos, caminho):
    c = canvas.Canvas(caminho, pagesize=A4)
    c.setTitle("Relatório de Empréstimos")
    c.drawString(200, 800, "RELATÓRIO DE EMPRÉSTIMOS")
    c.drawString(50, 780, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y = 750
    for emp in emprestimos:
        texto = f"Usuário: {emp.usuario.nome} | Livro: {emp.livro.titulo} | Data: {emp.data_emprestimo.strftime('%d/%m/%Y')}"
        c.drawString(50, y, texto)
        y -= 20
        if y < 50:
            c.showPage()
            y = 780
    c.save()

def gerar_relatorio_vendas(vendas, caminho):
    c = canvas.Canvas(caminho, pagesize=A4)
    c.setTitle("Relatório de Vendas")
    c.drawString(220, 800, "RELATÓRIO DE VENDAS")
    c.drawString(50, 780, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    total = 0
    y = 750
    for v in vendas:
        texto = f"Usuário: {v.usuario.nome} | Livro: {v.livro.titulo} | Valor: R$ {v.preco:.2f}"
        c.drawString(50, y, texto)
        total += v.preco
        y -= 20
        if y < 50:
            c.showPage()
            y = 780
    c.drawString(50, y - 20, f"Total de vendas: R$ {total:.2f}")
    c.save()
