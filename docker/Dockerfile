FROM python:3.6-alpine
COPY ./ /app/
WORKDIR /app/spiders/run
RUN apk add -U --no-cache libc-dev gcc libxslt-dev build-base linux-headers ca-certificates &&\ 
	apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
			python3 python3-dev libffi-dev libressl-dev && \
	pip install --upgrade pip && \
	pip install --upgrade setuptools && \
	pip install -r ../../requirements.txt 

