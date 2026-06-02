FROM python:3.11.15-trixie



ADD server /server
ADD client /client
RUN pip install -r /server/requirements.txt
ENTRYPOINT ["python", "/server/server.py"] 