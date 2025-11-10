# Biblioteca Online

Sistema de gerenciamento de biblioteca em Flask.

## Deploy no Render

1. Push do repositório para GitHub
2. No Render: New Web Service → conectar repositório
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn app:app