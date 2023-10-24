# Dockerfile to build BYOD to use on Anyscale Services:
#
# Build docker image:
# docker build . -t my-registry/my-image:tag

# Use Anyscale base image
FROM anyscale/ray:2.7.0-py310

# Install dependencies
RUN pip install --upgrade pip && pip install -U torch==2.0.1 torchvision==0.15.2

WORKDIR /home/ray

# Copy protobuf and deployment definitions into the docker image
COPY user_defined_protos.proto /home/ray/user_defined_protos.proto
COPY deployment.py /home/ray/deployment.py

# Add working directory into python path so they are importable
ENV PYTHONPATH=/home/ray

# Build python code from .proto file
RUN python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. ./user_defined_protos.proto
