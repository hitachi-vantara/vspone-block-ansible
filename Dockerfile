# Use the official Python image as a base image
FROM python:3.10-slim

# Install dependencies
RUN pip install --no-cache-dir ansible

# Set the default command to run Ansible
CMD ["ansible"]
