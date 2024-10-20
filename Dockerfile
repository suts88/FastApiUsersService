# Verwende das gewünschte FastAPI-Image als Basis
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-2024-09-02

# Setze das Arbeitsverzeichnis auf /app
WORKDIR /app

# Kopiere die requirements.txt in das Arbeitsverzeichnis
COPY ./requirements.txt /app/requirements.txt

# Installiere die Abhängigkeiten aus requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Kopiere den gesamten Inhalt des aktuellen Verzeichnisses ins Container-Verzeichnis /app
COPY . /app
