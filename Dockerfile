FROM python:3.10

RUN apt update

RUN mkdir /dorsia

WORKDIR /dorsia

COPY ./dorsia ./dorsia

COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "source /dorsia/venv/bin/activate && exec /bin/bash"]
