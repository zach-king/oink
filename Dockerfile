FROM python:3.6
WORKDIR /usr/src/oink
RUN mkdir data

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application's code
COPY . /usr/src/oink

# Run the app
CMD ["python3", "cli.py"]

