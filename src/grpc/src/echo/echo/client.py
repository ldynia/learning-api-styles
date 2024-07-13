# tag::import_modules[]
import sys
import time

import grpc

import echo.proto.echo.v1.echo_pb2 as pb2
import echo.proto.echo.v1.echo_pb2_grpc as pb2_grpc
# end::import_modules[]


# tag::define_unary_rpc[]
def unary(stub):  # <1>
    request = pb2.DemoUnaryRequest(content="Hello")  # <2>
    request_serialized = request.SerializeToString()  # <3>
    print(f"Client request: {request.content}, "  # <4>
          f"Serialized message: {request_serialized.hex()}")
    response = stub.DemoUnary(request)  # <5>
    print(f"Server response: {response.content}")  # <6>
# end::define_unary_rpc[]


# tag::define_serverstreaming_rpc[]
def server_streaming(stub):
    request = pb2.DemoServerStreamingRequest(content="Hello")
    print(f"Client request: {request.content}")
    responses = stub.DemoServerStreaming(request)
    for response in responses:
        print(f"Server response: {response.content}")
# end::define_serverstreaming_rpc[]


# tag::define_clientstreaming_rpc[]
def client_streaming(stub):
    def requests():
        for content in "Hello":
            yield pb2.DemoClientStreamingRequest(content=content)
            print(f"Client request: {content}")
    response = stub.DemoClientStreaming(requests())
    print(f"Server response: {response.content}")
# end::define_clientstreaming_rpc[]


# tag::define_bidirectionalstreaming_rpc[]
def bidirectional_streaming(stub):
    def requests():
        for content in "Hello":
            yield pb2.DemoBidirectionalStreamingRequest(content=content)
            print(f"Client request: {content}")
            time.sleep(1)
    responses = stub.DemoBidirectionalStreaming(requests())
    for response in responses:
        print(f"Server response: {response.content}")
# end::define_bidirectionalstreaming_rpc[]


# tag::get_ssl_channel_credentials[]
def get_ssl_channel_credentials(use_custom_ca=True, use_mtls=True):
    root_certificates = open("src/ca.crt", "rb").read() if use_custom_ca else None
    private_key = open("src/client.key", "rb").read() if use_mtls else None
    certificate_chain = open("src/client.crt", "rb").read() if use_mtls else None
    return grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain)
# end::get_ssl_channel_credentials[]

# tag::define_rpc_map[]
RPC_MAP = {
    "unary": unary,
    "server_streaming": server_streaming,
    "client_streaming": client_streaming,
    "bidirectional_streaming": bidirectional_streaming,
}
# end::define_rpc_map[]


def help():
    return (
        f"Usage: python client.py <{'|'.join(RPC_MAP.keys())}> <insecure|mtls>"
    )


if len(sys.argv) != 3:
    print(help())
    sys.exit(1)
# tag::parse_arguments[]
if len(sys.argv) == 3:
    rpc = sys.argv[1]
    security = sys.argv[2]
# end::parse_arguments[]
if rpc not in RPC_MAP:
    print(help())
    sys.exit(1)
if security not in ["insecure", "mtls"]:
    print(help())
    sys.exit(1)

# tag::create_channel[]
if security == "insecure":
    channel = grpc.insecure_channel("server:50051")  # <7>
if security == "mtls":
    credentials = get_ssl_channel_credentials(use_mtls=True)
    channel = grpc.secure_channel("server:50051", credentials)  # <7>
# end::create_channel[]

# tag::create_client_stub[]
stub = pb2_grpc.EchoServiceStub(channel)  # <8>
# end::create_client_stub[]

# tag::run_client[]
try:
    RPC_MAP[rpc](stub)  # <9>
except grpc.RpcError as rpc_error:
    print(f"gRPC call error: {rpc_error}")
    raise
finally:
    channel.close()  # <10>
# end::run_client[]
