FROM python:3.7

ENV PYTHONUNBUFFERED 1
RUN mkdir app
COPY requirements.txt app/
WORKDIR app/
RUN wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb \
    && dpkg -i erlang-solutions_1.0_all.deb \
    && apt update \
    && apt install erlang -y \
    && apt update \
    && apt install -y python perl libtemplate-perl gnuplot \
    && curl http://tsung.erlang-projects.org/dist/tsung-1.6.0.tar.gz --output /tmp/tsung-1.6.0.tar.gz \
    && cd /tmp/ \
    && tar xzf ./tsung-1.6.0.tar.gz \
    && cd tsung-1.6.0 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/tsung* \
    && cd /app/ \
    && apt update -y \
    && apt upgrade -y \
    && pip install -r requirements.txt
EXPOSE 8990
