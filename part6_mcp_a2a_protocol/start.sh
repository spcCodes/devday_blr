#!/bin/bash

# Activate the virtual environment
source /app/.venv/bin/activate

# Start math_server.py in the background
python math_server.py &

# Start weather_server.py in the foreground
python weather_server.py