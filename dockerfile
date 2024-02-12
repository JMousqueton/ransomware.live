FROM python:3.13.0a2-slim-bullseye

LABEL org.opencontainers.image.source https://github.com/jmousqueton/ransomwatch

COPY *.py /
COPY *.json /
COPY assets/useragents.txt /assets/useragents.txt
COPY requirements.txt /requirements.txt

RUN apt-get update -yy
RUN apt-get upgrade -yy
RUN apt install -yy \
    g++ gcc libxml2-dev \
    libxslt-dev libffi-dev \
    make curl jq firefox-esr \
    chromium

RUN curl -L `curl -sL https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r '.assets[].browser_download_url' | grep 'linux64.tar.gz$'` | tar -xz
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "ransomwatch.py"]