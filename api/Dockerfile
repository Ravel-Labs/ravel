FROM python:3.7.2
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]