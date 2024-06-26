from ray import serve
from user_defined_protos_pb2 import UserDefinedMessage, UserDefinedResponse


@serve.deployment
class GrpcDeployment:
    def __call__(self, user_message: UserDefinedMessage) -> UserDefinedResponse:
        greeting = f"Hello {user_message.name}!"
        user_response = UserDefinedResponse(greeting=greeting)
        return user_response


grpc_app = GrpcDeployment.options(name="grpc-deployment").bind()
