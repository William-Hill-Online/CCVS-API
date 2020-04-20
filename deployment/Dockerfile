FROM python:3.7.2

LABEL maintainer="application-security@williamhill.co.uk"
LABEL version="1.0.0"

ENV DOCKYARD_SRCPROJ=src
ENV DOCKYARD_SRVHOME=/srv
ENV DOCKYARD_SRVPROJ=$DOCKYARD_SRVHOME/$DOCKYARD_SRCPROJ

# Update the default application repository sources list
RUN apt-get update -y
RUN pip install pipenv

# Create user ccvs
RUN useradd -m ccvs --uid=1000

# Copy application source code to SRVPROJ
COPY $DOCKYARD_SRCPROJ $DOCKYARD_SRVPROJ
COPY ./Pipfile $DOCKYARD_SRVPROJ/Pipfile
COPY ./Pipfile.lock $DOCKYARD_SRVPROJ/Pipfile.lock

# Change ownership to ccvs
RUN chown ccvs:ccvs -R $DOCKYARD_SRVHOME

# Change current user
USER ccvs:ccvs

# Set workdir
WORKDIR $DOCKYARD_SRVPROJ

# Install Python dependencies
RUN pipenv install
