
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /src

# Copy the current directory contents into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .
# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PIP_ROOT_USER_ACTION=ignore

# Run main.py when the container launches
CMD ["python", "./main.py"]