FROM tensorflow/tensorflow:latest

WORKDIR /code

RUN apt-get update
RUN apt-get install -y cmake
RUN apt-get install -y python3-opencv
RUN pip install opencv-python

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

