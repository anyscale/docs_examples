# Running gRPC Services on Anyscale

In this example, we will deploy gRPC Services on Anyscale using [Anyscale Production Services](https://docs.anyscale.com/user-guide/run-and-monitor/production-services)

## Preparing your local shell environment
Start by making sure anyscale is properly setup on your local machine. You only need to do it once.

```bash
pip install -U anyscale
anyscale auth set
```

The configuration required is in a GitHub repo, let's clone it.

```bash
git clone https://github.com/anyscale/docs_examples.git
cd docs_examples/grpc_services
```

Anyscale services is a managed Ray Cluster running on your infrastructure. To run it, we need the following setup:
* A Docker image that contains the code for your protobuf and deployment files. You can learn more about it [here](https://docs.anyscale.com/user-guide/configure/dependency-management/bring-your-own-docker).
* A cluster environment describing the container image and Python dependencies. You can learn more about it [here](https://docs.anyscale.com/user-guide/configure/dependency-management/anyscale-environments).
* A service spec describing the configuration for the size of cluster (number of nodes) and the entrypoint to your code. You can learn more about it [here](https://docs.anyscale.com/user-guide/run-and-monitor/production-services).
* The code that host the model. The code is written to [Ray Serve](https://rayserve.org) framework to enable seamless scaling for your ML model in production.


## Building Services Docker image
To build a Docker image we need to first write a `Dockerfile`. There is an example
`Dockerfile` in this directory already written for you. You can build it with the
following command:

```bash
# build the docker image
docker build . -t my-registry/my-image:tag

# push the docker image to your registry
docker push my-registry/my-image:tag
```

The only thing specific to the gRPC service is that we need to include the python code
artifact complied from `.proto` file. And make sure it is importable by Python when
starting Ray Serve. 

For convenience, we also copied `deployment.py` into the image so we don't need to pull
from a separate repo later on.

Pushing the image to a registry requires you to have access to a registry. The easiest
way is to create a Docker Hub account and push to your own repo. See
[here](https://docs.anyscale.com/configure/dependency-management/bring-your-own-docker#step-2-push-your-image) for more options.


## Building the cluster environment
To build a cluster environment, we need to write a `cluster.yaml` file. There is an
example `cluster.yaml` in this directory already written for you. You can build it with the following command:

```bash
anyscale cluster-env build cluster_env.yaml --name grpc-cluster-env
```

Make sure you change the `docker_image` to your registry and image name. If your docker
image is based off a different version of Ray, you should also change the `ray_version`
to match it.


## Deploying the service
Once the environment is built, you can run the following command to deploy a running service on Anyscale.

```bash
anyscale service rollout -f service.yaml
```

This will create a service with the name `grpc-service` using `grpc-cluster-env:1`
cluster environment created in the previous step. The only thing to note is that we need
to ensure the grpc protocol is enabled by setting `config.protocols.grpc.enabled` to true.
`config.protocols.grpc.service_names` should also be defined and matching with the
services in your `.proto` file.

## Invoking the service
When the application is running, we will be able to find the token and domain name in
the Anyscale UI by clicking on the `Query` button in the upper right corner. 

you can invoke it using the following code in Python:

```python
import grpc
from user_defined_protos_pb2_grpc import ImageClassificationServiceStub
from user_defined_protos_pb2 import ImageData


url = "grpc-service-bxauk.cld-kvedzwag2qa8i5bj.s.anyscaleuserdata.com"
token = "jo3BeJW9FkLPZt1w_byWPYQdNz7QcDFpkXIne2ehOpA"

credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(url, credentials)
stub = ImageClassificationServiceStub(channel)
test_in = ImageData(
    url="https://github.com/pytorch/hub/raw/master/images/dog.jpg",
)
auth_token_metadata = ("authorization", f"bearer {token}")
metadata = (
    ("application", "app4"),
    auth_token_metadata,
)
response, call = stub.Predict.with_call(request=test_in, metadata=metadata)
print(call.trailing_metadata())  # Request id is returned in the trailing metadata
print("Output type:", type(response))  # Response is a type of ImageClass
print("Full output:", response)
print("Output classes field:", response.classes)
print("Output probabilities field:", response.probabilities)

```

Few things to note:
- the gRPC call to the service has to use a secured channel
- the url does not contain the protocol prefix or any suffix, just the domain name
- the auth token is optional, but if you want to use it, you need to pass it in the metadata
- the rest should work just like any other gRPC services you have used before

We also include a little script `test_client.py` to call on all the endpoints defined in
the `.proto` file. You can run it with the following command:

```bash
python test_client.py --url <grpc-service-xyz...anyscaleuserdata.com> --token="your_service_token"
```
