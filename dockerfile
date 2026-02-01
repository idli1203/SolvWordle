FROM python:3.11-slim
WORKDIR /app

RUN pip install --no-cache-dir \
    textual \
    numpy \
    numba

COPY src/ ./src/

WORKDIR /app/src
RUN python onetime.py

ENV TERM=xterm-256color

CMD ["python", "app.py"]
