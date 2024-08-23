import os
import torch
import logging
import uvicorn
import io as io_for_binary

from skimage import io
from PIL import Image
from briarmbg import BriaRMBG
from utilities import preprocess_image, postprocess_image
from fastapi import FastAPI, File, UploadFile, status
from fastapi.responses import Response


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

app = FastAPI(
    title="Remove Background Image Application",
    description="This is a simple FastAPI application for remove background from the image",
)


@app.post("/remove_background/")
async def image_remove_background(image_file: UploadFile = File(...), save_output_image=True):
    try:
        # not_allowed_operation = "" + 1 # uncomment to check 500 status code

        support_formats = ["jpg", "jpeg", "JPG", "JPEG"]
        background_file_prefix = "_no_background"
        image_name, image_format = image_file.filename.split(".")
        output_image_name = image_name + background_file_prefix + ".png"

        if image_format in support_formats:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logging.info(f"Image will be processing from {image_file.filename} to {output_image_name} on {device}")

            # get model
            net = BriaRMBG.from_pretrained(pretrained_model_name_or_path="briaai/RMBG-1.4", cache_dir='./model/')
            net.to(device)

            # prepare input
            orig_im = io.imread(image_file.file)
            height, width, _ = orig_im.shape
            model_input_size = [height, width]
            orig_im_size = orig_im.shape[0:2]
            image = preprocess_image(orig_im, model_input_size).to(device)

            # inference
            result = net(image)

            # post process image
            result_image = postprocess_image(result[0][0], orig_im_size)

            # add mask to original image
            pil_im = Image.fromarray(result_image)
            no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
            orig_image = Image.open(image_file.file)
            no_bg_image.paste(orig_image, mask=pil_im)

            # save image
            if save_output_image:
                no_bg_image.save(os.path.join("./output_examples/",  output_image_name))

            # prepare output
            img_byte_arr = io_for_binary.BytesIO()
            no_bg_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            logging.info(f"The input image {image_name}.{image_format} has been successfully processed "
                         f"and returned with filename {output_image_name}")
            return Response(
                content=img_byte_arr,
                media_type="image/png",
                headers={'Content-Disposition': f"attachment; filename={output_image_name}"},
                status_code=status.HTTP_200_OK,
            )
        else:
            logging.critical(f"Format {image_format} is not allowed. Allowed formats: {support_formats}")
            return Response(
                content=f"Invalid file format, use one of the formats from the list: {support_formats} instead",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )
    except Exception as ex:
        logging.error(f"Unsuccessful processing of file with internal server error: {ex}")
        return Response(
            content="Internal server error, try using it again",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.get("/health")
def health_check():
    net = BriaRMBG.from_pretrained(pretrained_model_name_or_path="briaai/RMBG-1.4", cache_dir='./model/')
    if isinstance(net, BriaRMBG):
        status_code = status.HTTP_200_OK
        logging.info(f"Health check passed successfully. Model was downloaded. Status code: {status_code}")
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logging.error(f"Unsuccessfully health check. Model can not be downloaded. Status code: {status_code}")
    return Response(status_code=status_code)


# test input file format
def test_main():
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # awaiting status_code 415
    # file = {"image_file": open("./input_examples/example_input._jpg", "rb")}

    # awaiting status_code 200
    file = {"image_file": open("./input_examples/example_input.jpg", "rb")}

    response = client.post("/remove_background/", files=file,)

    print(f"\nresponse:\n{response.status_code=}\n{response.headers=}")
    if response.status_code != 200:
        print(f"{response.content=} \n")

    assert response.status_code == 200


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080)
    # test_main()

