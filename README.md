# Republic of Rome

A "Hello World" Django app deployed to AWS with a Postgres database. A foundation on which to build something more complex.

## Deployment

A GitHub Actions Workflow is used to automatically deploy the app to AWS Elastic Beanstalk when there is a push to the "main" branch.

## Development

How to setup a local development environment:

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
