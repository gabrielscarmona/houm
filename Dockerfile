FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /houm
RUN apt-get update && apt-get install -y gdal-bin
RUN pip install --upgrade pip
COPY requirements.txt /houm/
RUN pip install -r requirements.txt
COPY . /houm/