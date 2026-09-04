FROM python:3.14-slim AS builder

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --prefix=/install .


FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

ENV FLASK_APP=menu_translator.app:create_app

EXPOSE 5000

CMD ["sh", "-c", "flask db upgrade && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 120 'menu_translator.app:create_app()'"]