FROM python:3.6-buster

COPY packagebuilder/requirements.txt packagebuilder/requirements.txt
RUN pip3 install -r packagebuilder/requirements.txt

COPY . /tools
WORKDIR /tools/packagebuilder

ENTRYPOINT [ "python3", "builder.py" ]
