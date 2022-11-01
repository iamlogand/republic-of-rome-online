# Republic of Rome Online

A web application powered by Django and React that doesn't really do anything. Currently, I'm just learning how to make all the parts fit together. This is a foundation on which to build something more complex: an online adaption of a board game called [The Republic of Rome](https://en.wikipedia.org/wiki/Republic_of_Rome_(game)).

## Environments

The backend and frontend live in separate environments within the AWS platform. The frontend React app communicates with the Django app in the backend via the Django REST Framework API. Besides the Django app, the other main component of the backend is the Postgres database.

### URLs

- Frontend: [www.roronline.com](https://www.roronline.com)
- DRF web browsable API: [api.roronline.com/rorapp/api](https://api.roronline.com/rorapp/api)

## Deployment

A GitHub Actions Workflow is used to deploy the backend to AWS Elastic Beanstalk when there is a push to the "main" branch that includes changes in the "backend" directory. AWS Amplify is used to deploy and host the frontend, these deployments are triggered by pushes to the "main" branch that include changes in the "frontend" directory.

## Development

How to setup a local development environment:

1. Clone this repository
2. Create a Python-3.8 virtual environment
3. Install packages from `requirements.txt`
4. Install Postgres-12
5. Create a database
6. Set the following environment variables in a `backend/.env` file:
   - `SECRET_KEY`
   - `DEBUG` (set this to `True`)
   - `RDS_DB_NAME`
   - `RDS_USERNAME`
   - `RDS_PASSWORD`
   - `RDS_HOSTNAME`
   - `RDS_PORT`
   - `FRONTEND_ORIGIN` (set this to `http://localhost:3000`)
7. Run `migrate`, `createsuperuser` then `runserver` at `backend/`
8. Set the following environment variable in a `frontend/.env` file:
   - `REACT_APP_BACKEND_ORIGIN` (set this to `http://127.0.0.1:8000`)
10. Run `npm run start` at `frontend/`
