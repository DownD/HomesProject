FROM python:3.10

RUN pip3 install -r requirements.txt

ENV PROJECT_DIR /usr/src/flaskbookapi

WORKDIR ${PROJECT_DIR}

COPY ./house_collector/* ./house_collector
COPY setup.py ./
COPY requirements.py ./

RUN pip3 install .
CMD ["python3", "house_collector.main.py", "-v"]