
# 
FROM python:3.11

# 
WORKDIR /code

#
WORKDIR /sh06-main/PSS_microservice/src

# 
COPY ./requirements.txt /code/requirements.txt

#
COPY init-mongo.js /docker-entrypoint-initdb.d/init-mongo.js
#
RUN chmod +x /docker-entrypoint-initdb.d/init-mongo.js

#
ENV mongo_host "mongodb+srv://proteinLovers:protein-Lovers2@cluster0.pbzu8xb.mongodb.net/?retryWrites=true&w=majority"

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
RUN pip install pymongo

#
EXPOSE 27017

# 
COPY . /code

# below running a server
CMD ["python3", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
#potental issue: trying to run project within dockerfile can result in file never terminating
#(happens for docker compose/'any orchestration software - KUBERNETES')

