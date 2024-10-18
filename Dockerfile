FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum install -y gcc python3-devel

# Set the working directory to /var/task
WORKDIR /var/task

# Create necessary directories
RUN mkdir -p ./model ./output_examples

# Copy application files and requirements
COPY ./app ./input_examples ./requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the CMD to your handler
CMD [ "main.lambda_handler" ]