FROM python:3.12-slim
WORKDIR /app

#Install system deps including curl
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*


#Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the model
RUN python - <<EOF
from sentence_transformers import SentenceTransformer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("Model downloaded successfully")
EOF

#Copy project files
COPY . .

ENV FLASK_PORT=5000     
ENV GRADIO_PORT=8080    


EXPOSE 8080 


CMD ["bash", "-lc", "python -m app.api.flask & \
    FLASK_PID=$!; \
    echo '⏳ Waiting for Flask health endpoint...' && \
    until curl -s http://localhost:5000/healthz > /dev/null; do \
        echo '   Flask not ready yet...'; \
        sleep 1; \
    done && \
    echo '🚀 Starting Gradio...' && \
    python -m app.ui.gradio_app; \
    wait $FLASK_PID"]
