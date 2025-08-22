FROM python:3.13-slim
 
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
 
# Set work directory
WORKDIR /app
 
# Install Python dependencies
COPY hunter-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy project
COPY hunter-api/ .

# Create logs directory
RUN mkdir -p /app/logs
 
# Expose port
EXPOSE 8000
 
# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]