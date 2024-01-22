# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY src/requirements.txt /code/
RUN pip install -r requirements.txt
# # Install dependencies
# COPY src/Pipfile src/Pipfile.lock /code/
# RUN pip install pipenv && pipenv install --system


# Copy the current directory contents into the container at /code/
COPY src/ /code/

# Cleanup unnecessary files to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Command to run Celery worker
CMD ["celery", "-A", "smart_home_project", "worker", "--loglevel=info"]

