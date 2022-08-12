import pickle
import shutil
import time

import PIL
import requests
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from preprocess import img_to_feature_vec

app = FastAPI()

origins = [
    "https://tinder.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clf = pickle.load(open('./models/lr.sav', 'rb'))


class Image(BaseModel):
    url: str

    class Config:
        schema_extra = {
            "example": {
                "url": "https://images-ssl.gotinder.com/u/f1vTkg9LiAy8q8DZ65vhHF/8VuqAeLbKE65e29BXHEmvm.webp",
            }
        }


class Response(BaseModel):
    code: str
    result: str

    class Config:
        schema_extra = {
            "example": {
                "code": "OK",
                "result": "HOT"
            }
        }


def download_image(url):
    """
    Download an image from a webp url and save it to a jpg.
    """
    response = requests.get(url, stream=True)
    image_name = f'./temp/{time.time_ns()}'
    image_file_jpg = f'{image_name}.jpg'
    if url[0:url.find('?')].endswith('.jpg'):
        with open(image_file_jpg, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return image_file_jpg
    else:
        image_file_webp = f'{image_name}.webp'
        with open(image_file_webp, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            img = PIL.Image.open(image_file_webp).convert('RGB')
            img.save(image_file_jpg, 'JPEG')
        del response
        return image_file_jpg


@app.post("/check", response_model=Response)
async def check(image: Image):
    """
    Check HOT or NOT for the given `image`
    """
    try:
        image_file = download_image(image.url)
        test = img_to_feature_vec(image_file, 'hot')
        if test is None:
            return Response(code="ERROR", result="FACE NOT FOUND")

        result = clf.predict([test[:-1]])[0]
        if result == 1:
            shutil.move(image_file, f'./dataset/hot/{time.time_ns()}.jpg')
            return Response(code="OK", result="HOT")
        else:
            shutil.move(image_file, f'./dataset/not/{time.time_ns()}.jpg')
            return Response(code="OK", result="NOT")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Server Runtime Error") from e
