FROM python:3.11-slim

WORKDIR /app

# Install uv for faster package management
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv venv
RUN uv pip install -r requirements.txt

# Copy application code
COPY math_server.py .
COPY weather_server.py .
COPY multi_server_client.py .
COPY start.sh .

# Make the startup script executable
RUN chmod +x start.sh

# Expose the ports the servers run on
EXPOSE 8050 8051

# Command to run both servers
CMD ["./start.sh"]