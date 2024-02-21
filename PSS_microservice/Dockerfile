
FROM python:3.10-slim

# Set the working directory in the container
#WORKDIR 

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 (this is not necessary as it's already specified in the CMD)
# EXPOSE 5000

# Run main.py when the container launches
CMD ["python", "main.py", "--port", "5000", "--reload"]