FROM python:3.9

WORKDIR /app
COPY main.py .

RUN pip install Flask pymongo psycopg2 python-dotenv

ENV FLASK_APP=main.py

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]