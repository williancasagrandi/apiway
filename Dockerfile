# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Porta padrão (o Vercel injeta $PORT)
ENV PORT 3000
EXPOSE 3000

# Usa shell form para expandir $PORT
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 3
