FROM python:3.7.2

RUN apt-get update
RUN apt-get install telnet -y

RUN pip install pipenv

ADD . /app
WORKDIR /app

RUN pipenv install --dev

RUN git clone https://github.com/vishnubob/wait-for-it.git /tmp/wait-for-it

ENTRYPOINT ["/tmp/wait-for-it/wait-for-it.sh", "ccvs_pgdb:5432", "--"]
