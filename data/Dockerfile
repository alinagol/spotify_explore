FROM python:3.9-slim-buster

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "get_data.py"]
