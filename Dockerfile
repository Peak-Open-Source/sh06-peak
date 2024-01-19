# 
FROM python:3.11.7

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./PSS_microservice /code

# below running a server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
#potental issue: trying to run project within dockerfile can result in file never terminating
#(happens for docker compose/'any orchestration software - KUBERNETES')