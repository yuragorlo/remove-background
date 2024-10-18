import torch
import logging
import io as io_for_binary
import base64
import json

from skimage import io
from PIL import Image
from briarmbg import BriaRMBG
from utilities import preprocess_image, postprocess_image

# Configure logger
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


def get_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = BriaRMBG.from_pretrained(pretrained_model_name_or_path="briaai/RMBG-1.4", cache_dir='/tmp/model/')
    net.to(device)
    return net, device


def lambda_handler(event, context):
    try:
        if isinstance(event, str):
            event = json.loads(event)
        image_data = event.get('image')
        if isinstance(image_data, str):
            image_data = base64.b64decode(image_data)
        image_file = io_for_binary.BytesIO(image_data)

        support_formats = ["jpg", "jpeg", "JPG", "JPEG"]
        background_file_prefix = "_no_background"

        image_format = "jpeg"
        image_name = "input_image"
        output_image_name = image_name + background_file_prefix + ".png"

        if image_format.lower() in support_formats:
            net, device = get_model()
            logging.info(f"Image will be processing to {output_image_name} on {device}")

            orig_im = io.imread(image_file)
            height, width, _ = orig_im.shape
            model_input_size = [height, width]
            orig_im_size = orig_im.shape[0:2]
            image = preprocess_image(orig_im, model_input_size).to(device)

            result = net(image)
            result_image = postprocess_image(result[0][0], orig_im_size)

            pil_im = Image.fromarray(result_image)
            no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
            orig_image = Image.open(image_file)
            no_bg_image.paste(orig_image, mask=pil_im)

            img_byte_arr = io_for_binary.BytesIO()
            no_bg_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            logging.info(f"The input image has been successfully processed")
            return {
                'statusCode': 200,
                'body': base64.b64encode(img_byte_arr).decode('utf-8'),
                'headers': {
                    'Content-Type': 'image/png'
                },
                'isBase64Encoded': True
            }
        else:
            logging.critical(f"Format {image_format} is not allowed. Allowed formats: {support_formats}")
            return {
                'statusCode': 415,
                'body': json.dumps({
                    'error': f"Invalid file format, use one of the formats from the list: {support_formats} instead"
                })
            }
    except Exception as ex:
        logging.error(f"Unsuccessful processing of file with internal server error: {ex}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(ex)
            })
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            image_data = f.read()
        event = {'image': base64.b64encode(image_data).decode('utf-8')}
        result = lambda_handler(event, None)
        print(json.dumps(result, indent=2))
    else:
        print("Please provide an image file path as an argument for local testing.")