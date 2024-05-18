FROM python:3.12-slim

RUN pip install -U pip

WORKDIR /dashboard
EXPOSE 8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
