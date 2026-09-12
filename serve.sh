#!/bin/bash
# Fetch the stock data using virtual environment

echo "Running Apple Stock Analysis..."
./venv/bin/python -m http.server --directory ./ 8000