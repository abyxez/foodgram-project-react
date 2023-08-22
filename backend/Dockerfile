FROM python:3.10.10

WORKDIR /app
COPY requirements.txt ./

RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8999", "foodgram.foodgram.wsgi"]