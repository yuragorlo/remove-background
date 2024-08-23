curl -X POST \
    'http://localhost:8080/remove_background/' \
    -H 'content-type: multipart/form-data' \
    -F image_file="@./input_examples/example_input.jpg" \
     > "output_examples/curl_example_input_no_background.png"