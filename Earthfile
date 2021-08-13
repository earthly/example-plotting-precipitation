deps:
    FROM ubuntu:20.10
    RUN apt-get update && apt-get install -y python3 python3-pip
    RUN pip3 install matplotlib pandas

plot:
    FROM +deps
    WORKDIR /precipitation
    COPY --dir data .
    COPY plot-precipitation.py .
    RUN python3 plot-precipitation.py
    SAVE ARTIFACT cumulative-annual-precipitation.png AS LOCAL ./
