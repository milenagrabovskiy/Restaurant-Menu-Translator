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

EXPOSE 5000

CMD ["sh", "-c", "flask --app menu_translator.app:create_app db upgrade && flask --app menu_translator.app:create_app run --host=0.0.0.0 --port=5000"]