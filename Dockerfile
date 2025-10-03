FROM n8nio/n8n:latest
USER root

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

# define diretório de trabalho
WORKDIR /app

# copia do repositório para dentro da imagem
COPY procurar.py /app/procurar.py
COPY consultar.py /app/consultar.py


USER node