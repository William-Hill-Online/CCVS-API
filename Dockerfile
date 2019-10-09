FROM python:3.7.2

LABEL version="0.0.11"

RUN apt-get update -y

RUN pip install pipenv

COPY ./src /app/src
COPY ./Pipfile /app/src/Pipfile

COPY ./Pipfile.lock /app/src/Pipfile.lock
COPY ./start-app.sh /app/src/start-app.sh

RUN chmod a+rx /app/src/start-app.sh

WORKDIR /app/src/

RUN pipenv install

EXPOSE 8000

ENTRYPOINT ["/app/src/start-app.sh"]
