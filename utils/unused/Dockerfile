# Usar uma imagem base do Windows com suporte ao Python
FROM python:3.13.2-server-ltsc2022

# Configurações básicas de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR C:/crawjudbot_app

# Copiar arquivos do projeto
COPY pyproject.toml poetry.lock windows/inst_vnc.ps1 C:/crawjudbot_app/

RUN powershell.exe -noexit ".\inst_vnc.ps1"

RUN scoop bucket add extras
RUN scoop install extras/googlechrome
RUN pip install --no-cache-dir poetry
RUN git config --global --add safe.directory C:/crawjudbot_app
RUN poetry config virtualenvs.create false
RUN poetry install --without dev
