# To build this Dockerfile, we have to run: docker build -t subgroups .
# To generate and run a container from the image, we have to run: docker run -it subgroups

FROM python:3.8.5

WORKDIR /home/subgroups

RUN apt-get update \
        && apt-get -y dist-upgrade \
        && apt-get -y install --no-install-recommends apt-utils dialog \
        && apt-get -y install git iproute2 procps iproute2 lsb-release \
        # Clean.
        && apt-get -y autoremove \
        && apt-get -y clean \
        && rm -rf /var/lib/apt/lists/*
RUN pip install pip --upgrade
RUN pip install subgroups

CMD ["/bin/bash"]
