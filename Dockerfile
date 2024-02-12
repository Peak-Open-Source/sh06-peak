
# docker run -it -p 80:80  pss-microservice
FROM python:3.11.7

# Set the working directory in the container
WORKDIR /microservice_build

# Copy the current directory contents into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .
# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PIP_ROOT_USER_ACTION=ignore

# Run main.py when the container launches
CMD ["python", "./PSS_microservice/main.py"]