#!/bin/bash

bash prepare_payload.sh

curl -X POST \
  'http://localhost:9000/2015-03-31/functions/function/invocations' \
  -H 'Content-Type: application/json' \
  -d @payload.json \
  -o response.json

jq -r '.body' response.json | base64 --decode > "output_examples/curl_example_input_no_background.png"
rm -f payload.json response.json
