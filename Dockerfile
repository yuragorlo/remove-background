FROM docker.io/nvidia/cuda:11.6.2-base-ubuntu20.04

EXPOSE 8080

WORKDIR /app

RUN bash -c 'mkdir -p ./{model,output_examples}'

COPY ./app ./input_examples ./requirements.txt /app/

RUN set -xe && apt-get update -y && apt-get install -y python3-pip
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
