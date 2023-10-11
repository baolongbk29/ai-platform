import datetime
import pytz
import os
from os import path
import cv2
import requests
import numpy as np
from PIL import Image
from io import BytesIO

# import from file
from engine.core import config


def now_utc():
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    return now


def str_yyyy_mm_from_int(year, month, space="-"):
    if month < 10:
        str_month = "0" + str(month)
    else:
        str_month = str(month)
    return str(year) + space + str_month


def str_yyyy_mm_dd(time: datetime = now_utc(), space="-"):
    str_year = str(time.year)
    if time.month < 10:
        str_month = "0" + str(time.month)
    else:
        str_month = str(time.month)
    if time.day < 10:
        str_day = "0" + str(time.day)
    else:
        str_day = str(time.day)
    return str_year + space + str_month + space + str_day


def str_yyyy_mm(time=now_utc(), space="-"):
    str_year = str(time.year)
    if time.month < 10:
        str_month = "0" + str(time.month)
    else:
        str_month = str(time.month)
    return str_year + space + str_month


def create_path(path_dir):
    if path.exists(path_dir):
        pass
    else:
        os.mkdir(path_dir)


def upload_file_bytes(file_bytes, path):
    f = open(path, "wb")
    f.write(file_bytes)
    f.close()


def read_image_from_path_to_numpy(path):
    image = Image.open(path)
    image = image.convert("RGB")
    return np.asarray(image)


def read_image_file(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image


def read_image_from_dir(path) -> Image.Image:
    image = Image.open(path)
    return image


def read_bytes_image_from_url(url):
    response = requests.get(url)
    image_bytes = BytesIO(response.content)
    return image_bytes.read()


def read_image_from_url(url):
    im = Image.open(requests.get(url, stream=True).raw)
    return im


def io_bytes_to_numpy(io_bytes):
    image = Image.open(BytesIO(io_bytes))
    image = image.convert("RGB")
    return np.asarray(image)
