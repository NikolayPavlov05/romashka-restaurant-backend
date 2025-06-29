# Используем официальный Python образ
FROM python:3.12.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
