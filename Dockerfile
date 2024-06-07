# Use the official Python image as a base image
FROM python:3.10-slim

# Install dependencies
RUN pip install --no-cache-dir ansible-core==2.16

# Set the default command to run Ansible
CMD ["ansible"]
