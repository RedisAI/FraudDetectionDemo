FROM python:3.10.0b2

WORKDIR /app
ADD . /app

RUN set -ex; \
    pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt;

ENTRYPOINT [ "bash", "entrypoint.sh" ]
