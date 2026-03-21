FROM python:3.13

WORKDIR /app
RUN pip install uv
RUN uv venv
ADD requirements.txt /app/
RUN uv pip install -r requirements.txt
ADD . /app
