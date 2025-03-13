#!/bin/bash

# Install Git LFS (for large file support)
apt-get update && apt-get install -y git-lfs

# Initialize and pull database file from Git LFS
git lfs install
git lfs pull

# Start the Flask app with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
