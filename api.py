import json
import os
import pickle
import shutil
import time
from multiprocessing import Pool

import PIL
import requests
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from preprocess import img_to_feature_vec

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clf = pickle.load(open('./models/rf_n500.sav', 'rb'))


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
            return Response(code="ERROR", result="Extract features error")

        result = clf.predict([test[:-1]])
        if result is None:
            return Response(code="ERROR", result="Can't predict")

        result = result[0]
        if result == 1:
            print('HOT', test)
            shutil.move(image_file, f'./dataset/hot/{time.time_ns()}.jpg')
            return Response(code="OK", result="HOT")
        else:
            print('NOT', test)
            shutil.move(image_file, f'./dataset/not/{time.time_ns()}.jpg')
            return Response(code="OK", result="NOT")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail=str(e))


class Profile(BaseModel):
    name: str
    age: int | None = None
    verified: bool = False
    livesIn: str
    bio: str
    job: str
    school: str

    passions: list[str] = []
    lifeStyles: list[str] = []
    photoUrls: list[str] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "Zwolf Cookie",
                "age": 27,
                "verified": True,
                "livesIn": "Bangkok, Thailand",
                "bio": "I’m a dog person 🐶\nIG : Cookieb2uty\n165cm",
                "job": "Marketing",
                "school": "PSU",
                "passions": ["Dog lover", "Travel", "Netfilx", "Cooking", "Running"],
                "lifeStyles": ["A", "Non-smoker", "Taurus", "Dog", "Cooking", "Bachelor"],
                "photoUrls": [
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_b16edea3-e424-47be-85d8-a94c2cd210b1.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_6019c045-25bd-4da6-81cb-6577ac2a36ea.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_cb8ef2cd-5db3-4e3c-adf0-7e0308a0e44e.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_6c1ed192-31d3-46ac-a750-786d4056cdcd.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_be04a41f-4f7b-45c3-9c88-a1fe1bccda61.jpg"
                ],
            }
        }


class Response(BaseModel):
    code: str
    result: str

    class Config:
        schema_extra = {
            "example": {
                "code": "OK",
                "result": "SAVED",
            }
        }


def download_image_save(url):
    """
    Download an image from the url, convert and save it to a jpg.
    """
    try:
        response = requests.get(url, stream=True)
        file_name = f"{time.time_ns()}"
        image_temp = f'./temp/{file_name}'
        image_file_jpg = f'{image_temp}.jpg'
        if url[0:url.find('?')].endswith('.jpg') or url.endswith('.jpg') or url.endswith('.jpeg'):
            with open(image_file_jpg, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            return image_file_jpg, f'{file_name}.jpg'
        else:
            image_file_webp = f'{image_temp}.webp'
            with open(image_file_webp, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                img = PIL.Image.open(image_file_webp).convert('RGB')
                img.save(image_file_jpg, 'JPEG')

            os.remove(image_file_webp)
            del response
            return image_file_jpg, f'{file_name}.jpg'
    except Exception as e:
        return None, None


def get_instagram_username(bio):
    """
    Get an instagram profile from bio.
    """
    lines = bio.split('\n')
    for line in lines:
        line = line.strip().lower()
        if line.startswith('instagram'):
            line = line.replace('instagram', '')
            line = line.replace(':', '')
            line = line.replace(' ', '')
            return line
        if line.startswith('ig'):
            line = line.replace('ig', '')
            line = line.replace(':', '')
            line = line.replace(' ', '')
            return line

    return ""


@app.post("/save", response_model=Response)
async def save(profile: Profile):
    """
    Save Tinder profile data.
    """
    uid = f"{time.time_ns()}"  # Use nano time epoch as uid
    user = {
        "uuid": uid,
        "instagram": get_instagram_username(profile.bio),
        "name": profile.name,
        "age": profile.age,
        "verified": profile.verified,
        "livesIn": profile.livesIn,
        "bio": profile.bio,
        "job": profile.job,
        "school": profile.school,
        "passions": profile.passions,
        "lifeStyles": profile.lifeStyles,
        "photos": [],
    }
    os.mkdir(f'./dataset/{uid}')
    with Pool(4) as p:
        image_files = p.map(download_image_save, profile.photoUrls)
        for image_file, file_name in image_files:
            if image_file is not None:
                user["photos"].append(file_name)
                shutil.move(image_file, f'./dataset/{uid}/{file_name}')

    with open('./dataset.txt', 'a') as df:
        df.write(json.dumps(user) + '\n')

    return Response(code="OK", result="SAVED")
