# Use an official Python runtime as a parent image
# Using python:3.9-slim-buster provides a lightweight version of Python 3.9 on Debian Buster
# FROM instruction initializes a new build stage and sets the Base Image for subsequent instructions.
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
# The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow it.
# If the WORKDIR doesn't exist, it will be created.
WORKDIR /app

# Copy the requirements.txt file from the host's app directory to the container's /app directory (the current WORKDIR)
# This is done as a separate early step to leverage Docker's layer caching.
# If requirements.txt doesn't change between builds (and this COPY instruction remains the same),
# Docker can reuse the cached layer where dependencies are installed (the next RUN step),
# significantly speeding up build times when only application source code changes later.
COPY app/requirements.txt .

# Install Python dependencies specified in requirements.txt
# The RUN instruction executes any commands in a new layer on top of the current image and commits the results.
# The committed image will be used for the next step in the Dockerfile.
# `pip install -r requirements.txt` reads the file and installs all listed packages.
RUN pip install -r requirements.txt

# Copy the rest of the application's source code from the host's app directory
# to the container's /app directory (the current WORKDIR).
# This includes all subdirectories and files within the 'app' directory on the host.
COPY app .

# Define the command to run when the container starts.
# The CMD instruction provides defaults for an executing container. These defaults can include an executable,
# or they can omit the executable, in which case you must specify an ENTRYPOINT instruction as well.
# There can only be one CMD instruction in a Dockerfile. If you list more than one CMD then only the last CMD will take effect.
# This command executes `python ./main.py` from the /app directory.
CMD ["python", "./run.py"]
