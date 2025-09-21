# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn  # for production server

# Copy app source
COPY . .

# Expose port
EXPOSE 5000

# Run Flask app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
