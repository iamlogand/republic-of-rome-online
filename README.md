# Republic of Rome

A 'Hello World!' Django app deployed to AWS with a Postgres database.

URL: http://rorsiteb-env.eba-q4m3zrnr.eu-west-2.elasticbeanstalk.com/

The app is deployed from the [**main** branch](https://github.com/iamlogand/RoR/tree/main) on GitHub to AWS by a local Jenkins instance.

## Setup for Development

1. Clone this repository
2. Create a Python-3.8 virtual environment
3. Install packages from `requirements.txt`
4. Install Postgres-12
5. Create a database
6. Set the following environment variables in a dotenv:
   - `SECRET_KEY`
   - `DEBUG` (recommended value: `True`)
   - `RDS_DB_NAME`
   - `RDS_USERNAME`
   - `RDS_PASSWORD`
   - `RDS_HOSTNAME`
   - `RDS_PORT`
7. Run `migrate`, `createsuperuser` and `startapp`
