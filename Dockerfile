FROM python:3.7

ENV PYTHONUNBUFFERED 1
RUN mkdir app
COPY requirements.txt app/
WORKDIR app/
RUN apt-get update \
    && apt-get install apt-utils -y \
    && curl http://erlang.org/download/otp_src_18.3.tar.gz --output /tmp/otp_src_18.3.tar.gz \
    && cd /tmp/ \
    && tar xzf ./otp_src_18.3.tar.gz \
    && cd otp_src_18.3 \
    && export ERL_TOP=`pwd` \
    && ./configure \
    && make \
    && make install \
    && curl http://tsung.erlang-projects.org/dist/tsung-1.7.0.tar.gz --output /tmp/tsung-1.7.0.tar.gz \
    && cd /tmp/ \
    && tar xzf ./tsung-1.7.0.tar.gz \
    && cd tsung-1.7.0 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/tsung* \
    && cd /app/ \
    && apt-get update -y \
    && apt-get upgrade -y \
    && pip install -r requirements.txt
EXPOSE 8990
