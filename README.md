# Practical Task

This task is to develop a social media platform using Django Rest Framework & Django (Domain Driven Design). The API should provide functionalities to manage users, posts, comments, likes, and followers. The goal is to create a robust and scalable API that allows users to interact with the social media platform.


## Requirements

- Python 3.9.13
- Pipenv
- PostgreSQL 15.0.2


## Quickstart

To run this project, you will need to copy the environment variables to your `.env` file inside the root directory from the `.env.example` file and customize it.

```bash
  pipenv shell
  pipenv install
  ./manage.py migrate
  ./manage.py createsuperuser
  ./manage.py runserver
```


## Running Tests Locally

```bash
  ./manage.py test
  ./manage.py test --verbosity=3 --exclude-tag=extended_slow --parallel   (To run it parallel)
```


## Directory Structure

```text
root/
    nexify/                 -> Base project directory
        application/
        domain/
        drivers/            -> asgi.py and wsgi.py
        infrastructure/
        interface/
        settings.py
    utils/
    .env
    manage.py
    ...
```


## An Object Storage Solution

**Using MinIO Object Storage with Python in Local**

Here is a guide on how to set up and use MinIO, an open-source object storage server, in combination with Python. MinIO is an excellent solution for creating your object storage service that is compatible with the Amazon S3 API.

**Prerequisites**

- Python 3.x installed (https://www.python.org/downloads/)
- MinIO server running (Installation steps provided below)
- minio Python library (pip install minio)


**Setting Up MinIO Server (Installation)**

*To set up a MinIO server locally for testing, you can follow these steps:*

- Download the MinIO executable from: https://dl.min.io/server/minio/release/windows-amd64/minio.exe
- In PowerShell or the Command Prompt, navigate to the location of the executable file.
- Use the following command to start a local MinIO instance in the `C:\minio` folder.

    ```bash
    .\minio.exe server C:\minio --console-address :9001
    ```

- Access the MinIO Console by going to `http://127.0.0.1:9001` or one of the Console addresses specified in the minio server command’s output.
- Log in to the Console with the `RootUser` and `RootPass` user credentials displayed in the output.

**Access and Secret Keys**

While running the MinIO server, you'll be provided with access and secret keys. Make note of those, as they will be required to interact with the server.

For more information, see the [MinIO](https://docs.min.io/) documentation.


## Periodic tasks

Periodic tasks are scheduled tasks at specific time intervals, which don't require to be called directly by any method or class created in the nexify project. Thus, those task requires to run celery in "beat" mode and in "worker" mode. This can be achieved by running the next two commands on the terminal (read [Celery](https://docs.celeryq.dev/en/stable/) documentation for more information):

```bash
  celery --app=nexify.celery worker --pool=solo --loglevel=DEBUG
  celery --app=nexify.celery beat --loglevel=DEBUG
```
