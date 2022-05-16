FROM python:3.10-slim-buster

WORKDIR /app

COPY ./python/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && pip install fastapi uvicorn

COPY ./python /app/python
COPY ./db /app/db
COPY ./image /app/image

EXPOSE 9000

CMD ["uvicorn", "python.main:app", "--host", "0.0.0.0", "--port", "9000"]

# STEP4-4では以下は変更しない
# CMD ["python", "-V"]
