# Biblioteca Online

Sistema de gerenciamento de biblioteca em Flask.

## Deploy no Render

1. Push do repositório para GitHub
2. No Render: New Web Service → conectar repositório
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn app:app


Notes:



http://localhost:5000/diagnostico

Acesse na ORDEM:

http://localhost:5000/criar-admin (se necessário)

http://localhost:5000/fix-database

http://localhost:5000/popular-biblioteca ⬅️ ESSA É A IMPORTANTE!

http://localhost:5000/
