FROM kyobad/jumanpp-alpine as jumanpp

FROM python:3.8-alpine as knp
ARG KNP_VERSION=4.20
ARG JUMAN_VERSION=7.01

COPY --from=jumanpp /usr/local/bin/jumanpp /usr/local/bin/jumanpp
COPY --from=jumanpp /usr/local/share/jumanpp /usr/local/share/jumanpp

RUN apk add --update --no-cache musl-dev gcc g++ boost make wget zlib-dev
# juman
WORKDIR /tmp/juman-${JUMAN_VERSION}
RUN wget -q http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-${JUMAN_VERSION}.tar.bz2 -O /tmp/juman.tar.bz2 &&\ 
    tar xf /tmp/juman.tar.bz2 -C /tmp && \
    ./configure --prefix=/usr/local/ && \
    make && \
    make install

# knp
WORKDIR /tmp/knp-${KNP_VERSION} 
RUN wget -q http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-${KNP_VERSION}.tar.bz2 -O /tmp/knp.tar.bz2 && \
    tar xf /tmp/knp.tar.bz2 -C /tmp && \
    ./configure --prefix=/usr/local/ --with-juman-prefix=/usr/local/ && \
    make && \
    make install

WORKDIR /tmp/local
RUN mkdir bin && mkdir lib && mkdir share && \
    cp /usr/local/bin/knp bin/knp && \
    cp /usr/local/bin/juman bin/juman && \
    cp /usr/local/lib/libcrf* lib/ && \
    cp /usr/local/lib/libjuman* lib/ && \
    cp -r /usr/local/share/knp share/knp && \
    cp -r /usr/local/share/juman share/juman && \
    cp -r /usr/local/etc etc && \
    cp -r /usr/local/include include && \
    cp -r /usr/local/libexec libexec && \
    true

##########
#  main  #
##########
FROM python:3.8-alpine

RUN apk add --update --no-cache musl-dev gcc boost curl
COPY --from=knp /tmp/local /usr/local
COPY --from=jumanpp /usr/local/bin/jumanpp /usr/local/bin/jumanpp
COPY --from=jumanpp /usr/local/share/jumanpp /usr/local/share/jumanpp

COPY . /tmp/tails-of-words
WORKDIR /tmp/tails-of-words
RUN python setup.py install
WORKDIR /

ENTRYPOINT ["tails-of-words"]
