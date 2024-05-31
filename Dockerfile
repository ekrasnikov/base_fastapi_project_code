FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

RUN mkdir -p /app/src
WORKDIR /app

COPY Pipfile .
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY src /app/src
COPY Pipfile .

EXPOSE 8000

CMD ["pipenv", "run", "gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000", "--disable-redirect-access-to-syslog", "--forwarded-allow-ips=\"*\"", "--keep-alive=5", "--timeout=120"]
