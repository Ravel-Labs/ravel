Please find the tutorial at https://medium.com/@samy_raps/flask-vue-mysql-on-docker-part-i-setting-up-320d55a85971

# Setting up Development Environment

For development, it's easiest to run the client and server apps separately
from their own processes. We use Docker and Docker-Compose for production, but
we won't need it for development.

## Python 3.7

Make sure you have the most up to date version of Python.
`python -V` should output `3.7.x` or higher.

Follow this guide to make sure you have Python setup correctly.
https://opensource.com/article/19/5/python-3-default-mac

Pyenv is nice for managing python versions. Make sure you get that, too.

2. Build the docker images. `docker-compose up --build -d` so that we have
them all cached and built and making sure they all still work.

3. Shut them all down. `docker-compose down`

4. Install requirement.txt
`cd api/ && pip install -r requirements.txt`

5. Run the Flask app
From inside `/api` folder, run `FLASK_APP=run FLASK_ENV=development flask run`
You should see output saying that the server has been started on port 5000.
Navigate your browser to that and you should see output from the api.

6. Install the vue app
`cd ui/ && yarn install && yarn serve` should start the front end up in one
fell swoop.

Navigate your browser to `localhost:8080` and you should see the client app.

### Important commands

Create a folder called `data` inside the `db` folder.

Build and run :: `docker-compose up --build`

Build and run in the background and view logs for all the instances ::
`docker-compose up --build -d && docker-compose logs --tail=all -f`

Stop instances :: `docker-compose down`

Stop and Delete all containers :: `docker container stop $(docker container ls -aq) && docker container rm $(docker container ls -aq)`

_Cheers!_

# Libraries & Resources
> A concise list of some of the more important frameworks we use in this app

### Python / Flask app:
*Flask RESTful: https://flask-restful.readthedocs.io/en/latest/


### Models / Flask-SQL-Alchemy
*Defining Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
*Methods on Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/