FROM python:3.11-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./main.py /app/main.py

EXPOSE 3000

RUN mkdir /app/data

ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:3000", "main:app" ]