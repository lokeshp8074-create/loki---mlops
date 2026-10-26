FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py train_model.py model.pkl ./
COPY templates ./templates
COPY static ./static

RUN addgroup --system gradecast && adduser --system --ingroup gradecast gradecast
USER gradecast

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:5000/health', timeout=3)"]

CMD ["waitress-serve", "--listen=0.0.0.0:5000", "app:app"]