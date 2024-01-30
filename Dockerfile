
# Use the official Python image as the base image
FROM python:3

WORKDIR /sh06-main

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3" "/src/models.py"]