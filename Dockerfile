FROM python:3.12.4-slim

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
    --reinstall build-essential && \
    rm --recursive --force /var/lib/apt/lists/*

RUN mkdir -p /agent/app
COPY --chown=agent:agnet  ./app /agent/app
COPY --chown=agent:agnet  ./setup_env.py /agent/
COPY --chown=agent:agnet  ./run_multiturns.sh /agent/
COPY --chown=agent:agnet  ./requirements/fastapi.txt /agent/requirements.txt

WORKDIR /agent
RUN chmod a+x run_multiturns.sh
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["./run_multiturns.sh"]
