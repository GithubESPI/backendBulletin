FROM python:3.11

WORKDIR /code

# Install LibreOffice for DOCX to PDF conversion
RUN apt-get update && apt-get install -y libreoffice

# Copy the .env file into the container
COPY .env /code/.env

# Copy the requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code
COPY ./app /code/app
COPY ./excel /code/excel
COPY ./template /code/template
COPY ./json /code/json

# Create necessary directories
RUN mkdir -p /code/documents /code/downloads

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

