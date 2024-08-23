# Remove background application  
  
This application removes background from jpg, jpeg, JPG, JPEG images and returns a png file without background.  It uses RMBG-1.4 (https://huggingface.co/briaai/RMBG-1.4) based on IS-Net (https://github.com/xuebinqin/DIS) with a unique learning scheme and its own dataset.
  
## Installation  
```
git clone https://github.com/yuragorlo/remove-background.git
cd remove-background
python3 -m venv venv  
source ./venv/bin/activate  
pip3 install -r requirements.txt
mkdir model output_examples  
python3 app/main.py  
```
  
  
## 1. Test endpoints
  
### 1.1  
Run the test_main function and check the /remove_background/ endpoint to see if the example_input.jpg file is being processed correctly.  It should return status code 200.  
```  
file = {"image_file": open("./input_examples/example_input.jpg", "rb")}  
  
if __name__ == "__main__":  
    test_main()  
```  
  
### 1.2  
Run the test_main function and check the /remove_background/ endpoint for an invalid extension of the input file example_input._jpg.  It should return a status code of 415.  
```  
file = {"image_file": open("./input_examples/example_input._jpg", "rb")}  
  
if __name__ == "__main__":  
    test_main()  
```  
  
### 1.3  
Override the not_allowed_operation line to check for an internal server error.  
It should return a status code of 500.  
```  
not_allowed_operation = "" + 1  
```  
  
  
  
## 2. Test web server  
  
### 2.1  
Check the status of the server and whether the model is loaded correctly  
```  
if __name__ == "__main__":  
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080)  
```  
```
curl -X GET http://localhost:8080/health
```
  
### 2.2  
Test the /remove_background/ endpoint using the curl_test_endpoint.sh file  
```  
if __name__ == "__main__":  
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080)  
```  
Run bash script and find the png file without background in the output_examples directory  
```  
bash curl_test_endpoint.sh  
```  
  
  
## 3 Test docker  

### 3.1
GPU support required additional installation steps:
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```
  
### 3.2
  
Building and running the docker container  
```  
docker pull docker.io/nvidia/cuda:11.6.2-base-ubuntu20.04
docker build -t rmbg:v0 .
docker run --runtime=nvidia --gpus=all -p 8080:8080 rmbg:v0
```  
  
Run bash script for test   
```  
bash curl_test_endpoint.sh  
```  
  
Check that the output file has been saved in the docker container correctly
```  
docker ps                                                                     # show container
docker cp 107bbbefaeb5:/app/output_examples/example_input_no_background.png . # replace container to actual
```