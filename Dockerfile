FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} run:app"]
