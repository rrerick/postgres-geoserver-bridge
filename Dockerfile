FROM osgeo/gdal:ubuntu-small-3.5.1

RUN mkdir /app
ENV APP_HOME /app
ENV PORT 8000
WORKDIR ${APP_HOME}


#python run in UNBUFFERED mode, the stdout and stderr streams are sent straight to terminal
ENV PYTHONUNBUFFERED 1

#install system requirements
RUN apt update -y

#install python library
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

RUN apt-get install postgresql-client -y

#install pip requirements
RUN python -m pip install --upgrade pip

#install dependencies
COPY requirements*.txt /app
RUN pip install -r requirements.txt 

#COPY FILES
COPY . /app


CMD ["bash","/app/runserver.sh"]
