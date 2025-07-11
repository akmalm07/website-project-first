FROM python:3.11-slim-buster

WORKDIR /user-db-manager

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]