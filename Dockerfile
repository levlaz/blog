FROM python:3.6-alpine
ENV FLASK_APP blog/blog.py

EXPOSE 5000

WORKDIR /app

ADD . /app/
RUN pip install -r requirements.txt
RUN flask migrate

ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
