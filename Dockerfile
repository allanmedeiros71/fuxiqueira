# Use uma imagem Python oficial como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o projeto
COPY . .

# Criar diretórios necessários
RUN mkdir -p staticfiles media

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bioimpedancia.wsgi:application"]
