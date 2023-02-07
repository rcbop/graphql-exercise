FROM python:3-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY api .
WORKDIR /app/api
RUN pip install .
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]