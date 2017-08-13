FROM python:3.6.2-alpine3.6

RUN adduser -S serenata_de_amor
WORKDIR /home/serenata_de_amor/toolbox

RUN apk add --no-cache \
  bash \
  g++ \
  gcc \
  libxml2-dev \
  libxslt-dev \
  make \
  musl-dev \
  && mkdir /usr/include/libxml \
  && ln -s /usr/include/libxml2/libxml/xmlexports.h /usr/include/libxml/xmlexports.h \
  && ln -s /usr/include/libxml2/libxml/xmlversion.h /usr/include/libxml/xmlversion.h

COPY . .
RUN python setup.py develop
