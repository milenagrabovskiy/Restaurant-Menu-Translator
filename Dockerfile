#build stage
FROM python:3.14-slim AS builder

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --prefix=/install .



# run stage
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

ENV FLASK_APP=menu_translator.app:create_app

EXPOSE 5000

CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=5000"]