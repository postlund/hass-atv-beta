FROM python:3.10

ARG USER=postlund
ARG UID=1000
ARG GID=1000
ARG PW=ha

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libudev-dev \
        libavformat-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        libavfilter-dev \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#WORKDIR /

RUN useradd -m ${USER} --uid=${UID} && echo "${USER}:${PW}" | \
      chpasswd
USER ${UID}:${GID}

# TODO: Should clone specific commit here
#RUN git clone --depth 1 https://github.com/home-assistant/home-assistant ha
WORKDIR /ha

#RUN ./script/setup
#RUN python3 setup.py develop
#RUN pip3 install -r requirements_test_all.txt -c homeassistant/package_constraints.txt

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
