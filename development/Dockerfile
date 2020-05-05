FROM python:3.6

RUN apt-get update
RUN apt-get install telnet -y

RUN pip install pipenv

ADD . /app
WORKDIR /app

RUN git clone https://github.com/vishnubob/wait-for-it.git /tmp/wait-for-it

ENTRYPOINT ["/tmp/wait-for-it/wait-for-it.sh", "ccvs_pgdb:5432", "--"]
