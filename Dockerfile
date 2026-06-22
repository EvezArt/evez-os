FROM python:3.12-slim
LABEL org.opencontainers.image.title="EVEZ Mesh"
LABEL org.opencontainers.image.description="Autonomous AI mesh — consciousness, music, voice, cross-domain correlation, and self-healing"
LABEL org.opencontainers.image.source="https://github.com/EvezArt/evez-os"
LABEL org.opencontainers.image.author="Steven Crawford-Maggard"

WORKDIR /app
COPY src/ /app/src/
COPY services/ /app/services/
EXPOSE 9111-9123

CMD ["python", "-m", "http.server", "9118"]
