from krpc.connection import Connection
from krpc.client import Client
from krpc.encoder import Encoder
from krpc.error import ConnectionError
from krpc.decoder import Decoder
from krpc.schema.KRPC import ConnectionRequest, ConnectionResponse

from krpc.version import __version__

DEFAULT_ADDRESS = '127.0.0.1'
DEFAULT_RPC_PORT = 50000
DEFAULT_STREAM_PORT = 50001


def connect(address=DEFAULT_ADDRESS, rpc_port=DEFAULT_RPC_PORT, stream_port=DEFAULT_STREAM_PORT, name=None):
    """
    Connect to a kRPC server on the specified IP address and port numbers. If
    stream_port is None, does not connect to the stream server.
    Optionally give the kRPC server the supplied name to identify the client (up
    to 32 bytes of UTF-8 encoded text).
    """
    assert rpc_port != stream_port

    # Connect to RPC server
    rpc_connection = Connection(address, rpc_port)
    rpc_connection.connect()
    rpc_connection.send(Encoder.RPC_HELLO_MESSAGE)
    request = ConnectionRequest()
    request.client_name = name
    rpc_connection.send_message(request)
    response = rpc_connection.receive_message(ConnectionResponse)
    if response.status != ConnectionResponse.OK:
        raise ConnectionError(response.message)
    client_identifier = response.client_identifier

    # Connect to Stream server
    if stream_port is not None:
        stream_connection = Connection(address, stream_port)
        stream_connection.connect()
        stream_connection.send(Encoder.STREAM_HELLO_MESSAGE)
        request = ConnectionRequest()
        request.client_identifier = client_identifier
        stream_connection.send_message(request)
        response = stream_connection.receive_message(ConnectionResponse)
        if response.status != ConnectionResponse.OK:
            raise ConnectionError(response.message)
    else:
        stream_connection = None

    return Client(rpc_connection, stream_connection)
