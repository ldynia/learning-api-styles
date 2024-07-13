# tag::import_modules[]
import concurrent
import sys

import grpc
from grpc_reflection.v1alpha import reflection

import echo.proto.echo.v1.echo_pb2 as pb2
import echo.proto.echo.v1.echo_pb2_grpc as pb2_grpc
# end::import_modules[]


# tag::define_servicer_class[]
class EchoServiceServicer(pb2_grpc.EchoServiceServicer):  # <1>
# end::define_servicer_class[]
    # tag::define_unary_rpc[]
    def DemoUnary(self, request, context):  # <2>
        content = request.content  # <3>
        return pb2.DemoUnaryResponse(content=content)  # <4>
    # end::define_unary_rpc[]

    # tag::define_serverstreaming_rpc[]
    def DemoServerStreaming(self, request, context):
        for content in request.content:
            yield pb2.DemoServerStreamingResponse(content=content)
    # end::define_serverstreaming_rpc[]

    # tag::define_clientstreaming_rpc[]
    def DemoClientStreaming(self, request_iterator, context):
        content = ""
        for request in request_iterator:
            content += request.content
        return pb2.DemoClientStreamingResponse(content=content)
    # end::define_clientstreaming_rpc[]

    # tag::define_bidirectionalstreaming_rpc[]
    def DemoBidirectionalStreaming(self, request_iterator, context):
        for request in request_iterator:
            content = request.content
            yield pb2.DemoBidirectionalStreamingResponse(content=content)
    # end::define_bidirectionalstreaming_rpc[]


# tag::get_ssl_server_credentials[]
def get_ssl_server_credentials(use_custom_ca=True, use_mtls=True):
    private_key = open("src/server.key", "rb").read()
    certificate_chain = open("src/server.crt", "rb").read()
    root_certificates = open("src/ca.crt", "rb").read() if use_custom_ca else None
    return grpc.ssl_server_credentials(
        [(private_key, certificate_chain)],
        root_certificates=root_certificates,
        require_client_auth=use_mtls)
# end::get_ssl_server_credentials[]


def help():
    return f"Usage: python server.py <insecure|mtls>"


if len(sys.argv) != 2:
    print(help())
    sys.exit(1)
# tag::parse_arguments[]
if len(sys.argv) == 2:
    security = sys.argv[1]
# end::parse_arguments[]
if security not in ["insecure", "mtls"]:
    print(help())
    sys.exit(1)

# tag::define_server[]
server = grpc.server(concurrent.futures.ThreadPoolExecutor())  # <5>
pb2_grpc.add_EchoServiceServicer_to_server(  # <6>
    EchoServiceServicer(), server)

SERVICE_NAMES = (reflection.SERVICE_NAME,  # <7>
    pb2.DESCRIPTOR.services_by_name["EchoService"].full_name)
reflection.enable_server_reflection(SERVICE_NAMES, server)  # <7>
# end::define_server[]

# tag::add_server_port[]
if security == "insecure":
    server.add_insecure_port("0.0.0.0:50051")  # <8>
if security == "mtls":
    credentials = get_ssl_server_credentials(use_mtls=True)
    server.add_secure_port("0.0.0.0:50051", credentials)  # <8>
# end::add_server_port[]

# tag::run_server[]
server.start()  # <9>
server.wait_for_termination()  # <10>
# end::run_server[]
