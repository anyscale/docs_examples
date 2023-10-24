# Test script for calling the gRPC service.
#
# Usage:
# python test_client.py --url <grpc-service-xyz...anyscaleuserdata.com> --token="your_service_token"
# example:
# python test_client.py --url grpc-service-bxauk.cld-kvedzwag2qa8i5bj.s.anyscaleuserdata.com --token="jo3BeJW9FkLPZt1w_byWPYQdNz7QcDFpkXIne2ehOpA"

import argparse
import grpc
from user_defined_protos_pb2_grpc import UserDefinedServiceStub, ImageClassificationServiceStub
from user_defined_protos_pb2 import UserDefinedMessage, UserDefinedMessage2, ImageData
from ray.serve.generated.serve_pb2_grpc import RayServeAPIServiceStub
from ray.serve.generated.serve_pb2 import HealthzRequest, ListApplicationsRequest

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str)
parser.add_argument("--token", type=str)
args = parser.parse_args()

credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(args.url, credentials)
auth_token_metadata = ("authorization", f"bearer {args.token}")

stub = RayServeAPIServiceStub(channel)
metadata = (auth_token_metadata,)

print("\n\n____________test calling ListApplications ____________")
routes_request = ListApplicationsRequest()
response, call = stub.ListApplications.with_call(routes_request, metadata=metadata)
print("response code", call.code())
print("Output type:", type(response))  # Response is a type of ListApplicationsResponse
print("Full output:", response)


print("\n\n____________test calling Healthz ____________")
healthz_request = HealthzRequest()
response, call = stub.Healthz.with_call(healthz_request, metadata=metadata)
print("response code", call.code())
print("Output type:", type(response))  # Response is a type of HealthzResponse
print("Full output:", response)


# Setup the stub for the user defined service
stub = UserDefinedServiceStub(channel)


print("\n\n____________test calling __call__ ____________")
test_in = UserDefinedMessage(
    name="genesu",
    num=88,
    origin="bar",
)
metadata = (
    ("application", "grpc_app"),
    auth_token_metadata,
)
response, call = stub.__call__.with_call(request=test_in, metadata=metadata)
print(call.trailing_metadata())  # Request id is returned in the trailing metadata
print("Output type:", type(response))  # Response is a type of UserDefinedResponse
print("Full output:", response)
print("Output greeting field:", response.greeting)
print("Output num field:", response.num)


print("\n\n____________test calling Multiplexing ____________")
request = UserDefinedMessage2()
app_name = "grpc_app"
request_id = "123"
multiplexed_model_id = "999"
metadata = (
    ("application", app_name),
    ("request_id", request_id),
    ("multiplexed_model_id", multiplexed_model_id),
    auth_token_metadata,
)

response, call = stub.Multiplexing.with_call(request=request, metadata=metadata)
print(f"greeting: {response.greeting}")  # "Method2 called model, loading model: 999"
for key, value in call.trailing_metadata():
    print(f"trailing metadata key: {key}, value {value}")  # "request_id: 123"


print("\n\n____________test calling Streaming ____________")
test_in = UserDefinedMessage(
    name="genesu",
    num=88,
    origin="bar",
)
metadata = (
    ("application", "grpc_app"),
    auth_token_metadata,
)
responses = stub.Streaming(test_in, metadata=metadata)
for response in responses:
    print("Output type:", type(response))  # Response is a type of UserDefinedResponse
    print("Full output:", response)
    print("Output greeting field:", response.greeting)
    print("Output num field:", response.num)
print(responses.trailing_metadata())  # Request id is returned in the trailing metadata


print("\n\n____________test calling ImageClassification ____________")
stub = ImageClassificationServiceStub(channel)
test_in = ImageData(
    url="https://github.com/pytorch/hub/raw/master/images/dog.jpg",
)
metadata = (
    ("application", "grpc_image_classifier"),
    auth_token_metadata,
)
response, call = stub.Predict.with_call(request=test_in, metadata=metadata)
print(call.trailing_metadata())  # Request id is returned in the trailing metadata
print("Output type:", type(response))  # Response is a type of ImageClass
print("Full output:", response)
print("Output classes field:", response.classes)
print("Output probabilities field:", response.probabilities)
