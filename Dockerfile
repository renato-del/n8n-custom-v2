FROM n8nio/n8n:latest
USER root

# Define as variáveis de ambiente de runtime
ENV DB_SQLITE_POOL_SIZE=1
ENV N8N_RUNNERS_ENABLED=true

# Instala Python e ferramentas com o gerenciador de pacotes 'apk' do Alpine Linux
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    unzip \
    wget \
    dbus \
    nss \
    mesa-gl \
    libxcomposite \
    libxext \
    libxfixes \
    libxi \
    libxrender \
    libxrandr \
    libxtst \
    xvfb \
    chromium \
    chromium-chromedriver \
    ttf-freefont \
    font-liberation \
    mesa-dri-gallium \
    freetype \
    harfbuzz \
    brotli-dev \
    glib \
    && rm -rf /var/cache/apk/*

# Corrige caminhos
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV PATH="$PATH:/usr/lib/chromium/"

# Cria venv e instala selenium
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --no-cache-dir selenium

# ... (instalação do Selenium e COPIAR seus arquivos)

DB_SQLITE_POOL_SIZE=1
N8N_RUNNERS_ENABLED=true

# define diretório de trabalho
WORKDIR /app

# copia do repositório para dentro da imagem
COPY procurar.py /app/procurar.py
COPY consultar.py /app/consultar.py

# IMPORTANTE: Garante que o usuário 'node' pode acessar e escrever nos diretórios
# O usuário 'node' é o padrão da imagem n8n.
USER root
RUN chown -R node:node /app \
    && chown -R node:node /home/node
USER node

