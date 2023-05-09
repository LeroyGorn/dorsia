FROM python:3.10

RUN apt update

RUN mkdir /dorsia

WORKDIR /dorsia

COPY ./dorsia ./dorsia

RUN python -m venv /dorsia/venv
ENV PATH="/dorsia/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt

RUN /dorsia/venv/bin/pip install --upgrade pip

RUN /dorsia/venv/bin/pip install gunicorn

COPY ./myvenv/lib/python3.10/site-packages/ /dorsia/venv/lib/python3.10/site-packages/

CMD ["/bin/bash", "-c", "source /dorsia/venv/bin/activate && exec /bin/bash"]
