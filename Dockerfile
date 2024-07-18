FROM python:3.12-slim

RUN pip install -U pip
RUN pip install poetry

WORKDIR /app
EXPOSE 8000

# Enabling virtual environment will make it difficult to access the shell inside.
# Therefore, using pip to directly install packages to the container.
COPY pyproject.toml poetry.lock .
RUN poetry export --with dev > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard .

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
