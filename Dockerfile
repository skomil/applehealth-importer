FROM debian:stretch-slim

WORKDIR /main

COPY importer.py ./importer.py
ENV INFLUX_HOST=''
ENV INFLUX_USER=''
ENV INFLUX_PASS=''
ENV IMPORT_PATH=''

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    influxdb-client \
    && rm -rf /var/lib/apt/lists/*
#RUN more requirements.txt
RUN pip3 install pandas 

CMD python3 -u importer.py $IMPORT_PATH $INFLUX_HOST $INFLUX_USER $INFLUX_PASS
