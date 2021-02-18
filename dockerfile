# set base image (host OS)
FROM python:3.7-buster

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN chmod 777 /media

# copy the content of the local src directory to the working directory
COPY ggtv.py .

# command to run on container start
CMD [ "python3", "./ggtv.py", "-d /media", "-r GGTV"]