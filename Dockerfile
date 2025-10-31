FROM python:3.11-slim
WORKDIR /app

# Configurações Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências
COPY python/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia app Python
COPY python/app /app/app

# Porta da API FastAPI
EXPOSE 3000

# Comando padrão (usa PORT do ambiente, padrão 3000)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000}"]