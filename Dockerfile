FROM ubuntu:latest
LABEL authors="nik"

ENTRYPOINT ["top", "-b"]