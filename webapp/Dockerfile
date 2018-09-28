FROM python:3.6-slim
WORKDIR /webapp
ADD . /webapp
RUN pip install --trusted-host pypi.python.org -r requirements.txt 
## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.3.0/wait /wait
RUN chmod +x /wait

## Launch the wait tool and then your application
#CMD /wait && ./startup
