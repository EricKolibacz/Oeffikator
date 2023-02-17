# From the Fastapi website (https://fastapi.tiangolo.com/deployment/docker/#docker-image-with-poetry)
FROM python:3.11-slim-buster as requirements-stage
# create requirements.txt from poetry
WORKDIR /tmp
RUN pip install poetry
COPY . /tmp/
RUN poetry build && poetry export -f requirements.txt --output requirements.txt --without-hashes --with visualization
FROM python:3.11-slim-buster
WORKDIR /code
RUN apt update
RUN apt install gunicorn3 -y
# install required python packages
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# install oeffikator package too (seems to be important to get the actual verion)
COPY --from=requirements-stage /tmp/dist /code
RUN pip install /code/*.whl
# and now let's get the source code
COPY .env/ /code
COPY visualization/ /code/visualization/
ENV PYTHONPATH "${PYTHONPATH}:/code"

CMD ["gunicorn", "-b", "0.0.0.0:8080", "visualization.main:server"]
