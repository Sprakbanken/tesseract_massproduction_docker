FROM ubuntu:20.04

ENV TZ=Europe/Oslo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
	autoconf \
	autoconf-archive \
	automake \
	build-essential \
	ca-certificates \
	checkinstall \
	cmake \
	g++ \
	git \
	libcairo2-dev \
	libicu-dev \
	libjpeg-dev \
	libpango1.0-dev \
	libgif-dev \
	libleptonica-dev \
	libwebp-dev \
	libopenjp2-7-dev \
	libpng-dev \
	libtiff-dev \
	libtool \
	make \
	pkg-config \
	wget \
	xzgv \
	zlib1g-dev \
	python3-pip \
	libcurl4-gnutls-dev

RUN mkdir /home/test && \
	cd /home/test && \
	git clone --depth 1 https://github.com/tesseract-ocr/tesseract.git && \
	cd tesseract && \
	./autogen.sh && \
	mkdir -p bin/release && \
	cd bin/release && \
	../../configure --disable-openmp --disable-shared 'CXXFLAGS=-g -O2 -fno-math-errno -Wall -Wextra -Wpedantic -fPIC' && \
	make && \
	make install && \
	make training && \
	make training-install && \
	ldconfig

RUN pip install tesserocr Pillow requests

WORKDIR /code
COPY process.py .
