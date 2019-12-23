FROM python:3.7.2

LABEL version="0.0.13"

ENV DOCKYARD_SRC=src
ENV DOCKYARD_SRVHOME=/srv
ENV DOCKYARD_SRVPROJ=$DOCKYARD_SRVHOME/$DOCKYARD_SRC
ENV ALLOWED_HOSTS=127.0.0.1

# Update the default application repository sources list
RUN apt-get update -y
RUN apt-get install -y nginx
RUN pip install pipenv

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir logs

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ
COPY ./Pipfile $DOCKYARD_SRVPROJ/Pipfile
COPY ./Pipfile.lock $DOCKYARD_SRVPROJ/Pipfile.lock

# Port to expose
EXPOSE 8080

WORKDIR $DOCKYARD_SRVPROJ

# Install Python dependencies
RUN pipenv install

# Copy entrypoint script into the image
COPY ./docker-entrypoint.sh /
COPY ./ccvs_nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/ccvs_nginx.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf


USER ccvs:ccvs

ENTRYPOINT ["/docker-entrypoint.sh"]
