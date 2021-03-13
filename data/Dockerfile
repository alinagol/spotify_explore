FROM python:3.9-slim-buster

WORKDIR /data

COPY ./requirements.txt /data
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /data

CMD ["python", "get_data.py"]
