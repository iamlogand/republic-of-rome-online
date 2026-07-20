# Setup a development environment

This guide is primarily aimed at Windows users, but the frontend and backend apps also work on Linux and macOS.

## Prerequisites

- [Git](https://git-scm.com/downloads)
- [Node.js](https://nodejs.org/en/download)
- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.12](https://www.python.org/downloads/release/python-31213/) — use this version specifically, as it matches production
- [PostgreSQL 12](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
- A [Google Cloud Platform](https://console.cloud.google.com/) account

## Setup

### 1. Clone the repository

Clone using [GitHub Desktop](https://desktop.github.com/) or the command line.

### Backend

### 2. Create a Python virtual environment

```
C:\Python\Python312\python -m venv venv
```

Replace the path with the location of your Python 3.12 installation.

### 3. Activate the virtual environment

Follow the [official guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) and verify the version:

```
python --version
```

### 4. Install dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Google authentication

- Create a new project in [Google Cloud Platform](https://console.cloud.google.com/)
- Go to **Google Auth Platform** and create an app named "Republic of Rome Online"
- Add OAuth scopes: `./auth/userinfo.email`, `./auth/userinfo.profile`, `openid`
- Create a **web application** OAuth client with these redirect URIs:
  - `http://localhost:8000/accounts/google/login/callback/`
  - `http://127.0.0.1:8000/accounts/google/login/callback/`
- Note your **Client ID** and **Client secret**

### 6. Create the backend environment file

Create `.env` in the `backend` folder:

```
ALLOWED_HOSTS=127.0.0.1
FRONTEND_ORIGINS=http://127.0.0.1:3000
DEBUG=True
PARENT_DOMAIN=127.0.0.1
RDS_HOSTNAME=localhost
RDS_NAME=postgres
RDS_PASSWORD=rdspassword
RDS_PORT=5432
RDS_USERNAME=postgres
REDIS_HOSTNAME=127.0.0.1
SECRET_KEY=abc123
SOCIALACCOUNT_GOOGLE_CLIENT_ID=googleclientid
SOCIALACCOUNT_GOOGLE_SECRET=googlesecret
```

Replace `rdspassword` with your PostgreSQL superuser password, `googleclientid` with your Google Client ID, and `googlesecret` with your Google secret.

### 7. Start PostgreSQL

On Windows, open **Services** (`services.msc`) and verify the PostgreSQL service is running. Look for a service beginning with "postgresql".

### 8. Initialize the database

```
python manage.py migrate
python manage.py createsuperuser
```

Provide a username and password when prompted.

### 9. Start Redis

```
docker run -p 6379:6379 -d redis:5
```

### 10. Run the backend development server

```
python manage.py runserver
```

Verify it's working at http://127.0.0.1:8000.

### Frontend

### 11. Create the frontend environment file

Create `.env` in the `frontend` folder:

```
BACKEND_URL=http://127.0.0.1:8000/
```

### 12. Install dependencies and start the frontend

```
npm install
npm run dev
```

Access the app at http://localhost:3000 and log in with your superuser credentials.

## Updating an existing environment

### Backend

```
pip install -r requirements.txt
python manage.py migrate
```

### Frontend

```
npm install
```

## IDE

The project includes a VS Code workspace file (`roronline.code-workspace`). Open the project through this file rather than as a folder for the best experience.
