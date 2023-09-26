import supervisely_lib as sly
from PIL import Image
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import numpy as np
import cv2, zlib, base64, io
from PIL import Image
import csv, pandas as pd
from tqdm import tqdm

#Following the description here:
#https://developer.supervisely.com/getting-started/basics-of-authentication
#I have my webaddress and token stored in a .env file in my home directory
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()

# Alternatively, you can specify the address and token manually
#address = "https://app.supervise.ly/"
#token = os.environ["API_TOKEN"]
#api = sly.Api(address, token)

# Specify the project to download
# project = api.project.get_info_by_name('<your-team>', '<your-project>')

WORKSPACE_ID = 83434
project = api.project.get_or_create(
    workspace_id=WORKSPACE_ID, name="plast_data"
)

def base64_2_mask(s):
    z = zlib.decompress(base64.b64decode(s))
    n = np.fromstring(z, np.uint8)
    mask = cv2.imdecode(n, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(bool)
    return mask

def mask_2_base64(mask):
    img_pil = Image.fromarray(np.array(mask, dtype=np.uint8))
    img_pil.putpalette([0,0,0,255,255,255])
    bytes_io = io.BytesIO()
    img_pil.save(bytes_io, format='PNG', transparency=0, optimize=0)
    bytes = bytes_io.getvalue()
    return base64.b64encode(zlib.compress(bytes)).decode('utf-8')


# Download images and annotations
out_dir_images = "data/annotated_images/"
os.makedirs(out_dir_images, exist_ok=True)
out_dir_objects = "data/annotated_objects/"
os.makedirs(out_dir_objects, exist_ok=True)
dict_id_to_orignal_filename = {}
list_of_objects = []

for dataset in api.dataset.get_list(project.id):
    for image in tqdm(api.image.get_list(dataset.id)):
        image_id = image.id
        ann = api.annotation.download(image.id).annotation
        # img = api.image.download_np(image.id)
        
        # if objects (masks) exist for this image, download the objects and masks
        if ann["objects"] != []:
            img = api.image.download_np(image.id)
            dict_id_to_orignal_filename[image_id] = image.name
            img_output_filename = 'imageId_' + str(image_id)
            np.save(out_dir_images + img_output_filename + '.npy', img)
            #could also use tifffile.imwrite('output.tiff', img) here

            for i in range(len(ann["objects"])):
                dict_this_object = {}
                dict_this_object['objectId'] = ann['objects'][i]['id']
                dict_this_object['imageId'] = image_id
                dict_this_object['image_original_filename'] = image.name
                dict_this_object['origin_x0'] = ann['objects'][i]['bitmap']['origin'][0]
                dict_this_object['origin_x1'] = ann['objects'][i]['bitmap']['origin'][1]
                
                origin_coords = 'x0_' + str(dict_this_object['origin_x0'])
                origin_coords += '_x1_' + str(dict_this_object['origin_x1'])
                
                mask = base64_2_mask(ann["objects"][i]["bitmap"]["data"])
                object_name = img_output_filename
                object_name += '_objectId_' + str(dict_this_object['objectId'])
                object_name += '_origin_' + origin_coords
                np.save(out_dir_objects + object_name + '.npy', mask)

                dict_this_object['object_size0'] = mask.shape[0]
                dict_this_object['object_size1'] = mask.shape[1]
                list_of_objects.append(dict_this_object)

out_metadata = "data/"
with open(out_metadata + 'annotated_images_metadata.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['image_id', 'original_filename'])
    writer.writerows(dict_id_to_orignal_filename.items())

df = pd.DataFrame(list_of_objects)
df.to_csv(out_metadata + 'annotated_objects_metadata.csv', index=False)