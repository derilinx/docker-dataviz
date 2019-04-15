FROM ubuntu:16.04

USER root

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN python3.6 -m pip install pip --upgrade


COPY ./cso-DataViz /cso-DataViz
WORKDIR /cso-DataViz
RUN python3.6 -m  pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python3.6"]
CMD ["app.py"]

