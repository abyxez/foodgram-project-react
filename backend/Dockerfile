FROM python:3.10.10

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y libpq-dev gcc netcat-traditional

WORKDIR /app
COPY requirements.txt ./

RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "foodgram.wsgi"]
