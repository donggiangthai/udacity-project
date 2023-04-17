#!/usr/bin/env bash

## Complete the following steps to get Docker running locally

# Step 1:
# Build image and add a descriptive tag
docker build --tag project-ml:v1.0.0 .

# Step 2: 
# List docker images
docker image list

# Step 3:
# Run flask app
docker run --detach --publish 8000:80 project-ml:v1.0.0
