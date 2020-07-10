FROM python:3.7.2-slim-buster
WORKDIR /app
COPY ./api /app/api
COPY ./ravellib ./app/ravellib
COPY ./run.py ./app.ini ./__init__.py /app/
RUN pip install -r /app/api/requirements.txt
CMD [ "uwsgi", "app.ini"]
