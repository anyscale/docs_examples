# Test script for calling the gRPC service.
import grpc
from user_defined_protos_pb2_grpc import UserDefinedServiceStub
from user_defined_protos_pb2 import UserDefinedMessage


# Replace url and token with your own.
url = "grpc-service-bxauk.cld-kvedzwag2qa8i5bj.s.anyscaleuserdata.com"
token = "ABNM_uL1LdlNhqB-jy_h0Jmb5JmocVHPwfZOL7iyTe4"

credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(url, credentials)
stub = UserDefinedServiceStub(channel)
request = UserDefinedMessage(name="Ray")
auth_token_metadata = ("authorization", f"bearer {token}")
metadata = (
    ("application", "grpc_app"),
    auth_token_metadata,
)
response, call = stub.__call__.with_call(request=request, metadata=metadata)
print(call.trailing_metadata())  # Request id is returned in the trailing metadata
print("Output type:", type(response))  # Response is a type of UserDefinedMessage
print("Full output:", response)
