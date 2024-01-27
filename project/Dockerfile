FROM python:3.8
LABEL maintainer="Shashank Iyer"

WORKDIR /techtrends
COPY techtrends /techtrends
RUN pip install -r requirements.txt

EXPOSE 3111

RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]