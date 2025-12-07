# # This runs both Flask API and Gradio via Gunicorn or you can run them separately. Simplest is: container exposes Flask API (Cloud Run), and you separately run Gradio in another service or locally. Below example builds a container for the Flask API (recommended for Cloud Run):
# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# # System deps (add others as required)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY app ./app
# COPY .env ./.env

# ENV PORT=8080

# CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.api.flask_app:create_app()"]

FROM python:3.12-slim
WORKDIR /app

#Install system deps including curl
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*


#Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

#Copy project files
COPY . .

ENV FLASK_PORT=8080     
ENV GRADIO_PORT=7860    

# External traffic will go to 7860 (Gradio)
EXPOSE 7860
EXPOSE 8080 

# ------------------------------
# Start both services in same container
# Flask → background @ 8080
# Gradio → foreground @ 7860 (Cloud Run public endpoint)
# ------------------------------

# CMD bash -c "\
#     python -m app.api.flask & \
#     echo '⏳ Waiting for Flask health endpoint...' && \
#     until curl -s http://localhost:8080/healthz > /dev/null; do \
#         echo '   Flask not ready yet...'; \
#         sleep 1; \
#     done; \
#     echo '✅ Flask is ready!' && \
#     echo '🚀 Starting Gradio...' && \
#     python -m app.ui.gradio_app \
# "


CMD ["bash", "-lc", "python -m app.api.flask & \
    FLASK_PID=$!; \
    echo '⏳ Waiting for Flask health endpoint...' && \
    until curl -s http://localhost:8080/healthz > /dev/null; do \
        echo '   Flask not ready yet...'; \
        sleep 1; \
    done && \
    echo '🚀 Starting Gradio...' && \
    python -m app.ui.gradio_app; \
    wait $FLASK_PID"]
