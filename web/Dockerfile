FROM python:3.9-slim-buster

WORKDIR /app

EXPOSE 5001

COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "app:app"]
