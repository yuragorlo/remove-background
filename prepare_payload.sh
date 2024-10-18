#!/bin/bash

# Encode the image
BASE64_IMAGE=$(base64 -w 0 ./input_examples/example_input.jpg)

# Create the JSON payload
echo "{\"image\":\"${BASE64_IMAGE}\"}" > payload.json