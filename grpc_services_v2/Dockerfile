# Dockerfile to build image to use on Anyscale Services:
#
# Build docker image:
# docker build . -t my-registry/my-image:tag
#
# Push the docker image to your registry:
# docker push my-registry/my-image:tag

# Use Anyscale base image
FROM anyscale/ray:2.30.0-py310

WORKDIR /home/ray

# Copy protobuf and deployment definitions into the docker image
COPY user_defined_protos.proto /home/ray/user_defined_protos.proto
COPY deployment.py /home/ray/deployment.py

# Add working directory into python path so they are importable
ENV PYTHONPATH=/home/ray

# Build python code from .proto file
RUN python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. ./user_defined_protos.proto
