FROM kyobad/jumanpp-alpine as jumanpp
FROM python:3.8-alpine

RUN apk add --update --no-cache musl-dev gcc boost
COPY --from=jumanpp /usr/local/bin/jumanpp /usr/local/bin/jumanpp
COPY --from=jumanpp /usr/local/share/jumanpp /usr/local/share/jumanpp

COPY . /tmp/tails-of-words
WORKDIR /tmp/tails-of-words
RUN python setup.py install
WORKDIR /

CMD ["tails-of-words"]
