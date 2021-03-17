FROM python:3.9-slim-buster as config
RUN echo "deb http://deb.debian.org/debian/ buster-backports main" > /etc/apt/sources.list.d/buster-backports.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    jq \
    curl \
    wireguard-tools
COPY . /app
WORKDIR /app
ARG PIA_USER
ARG PIA_PASS
ARG PIA_REGION
RUN pip3 install -r requirements.txt && \
    echo "$PIA_USER $PIA_PASS $PIA_REGION" && \
    python3 generate-config.py -u "$PIA_USER" -p "$PIA_PASS" -r "$PIA_REGION" -o wg0.conf

FROM ghcr.io/linuxserver/wireguard
COPY --from=config /app/wg0.conf /config/wg0.conf
