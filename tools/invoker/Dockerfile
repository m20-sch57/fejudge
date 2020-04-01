FROM python:3.6-buster

COPY invoker/requirements.txt invoker/requirements.txt
RUN pip3 install -r invoker/requirements.txt

COPY . /tools
WORKDIR /tools/invoker

ENTRYPOINT [ "python3", "invoker.py" ]
