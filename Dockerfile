FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir app
COPY requirements.txt app/
WORKDIR app/
RUN apt update -y && apt upgrade -y && pip install -r requirements.txt
EXPOSE 8990
