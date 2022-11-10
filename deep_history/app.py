import datetime
import json
import os
from pathlib import Path
from typing import Any

from bottle import static_file  # type: ignore
from bottle import Bottle, request, response  # type: ignore
from erdpy_network.errors import GenericError

from deep_history.services import Services

FOLDER = Path(__file__).parent
FOLDER_STATIC = FOLDER / "static"


class RequestError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MyBottle(Bottle):
    def default_error_handler(self, res: Any):
        response.content_type = "application/json"

        if isinstance(res.exception, RequestError):
            return json.dumps(dict(error=str(res.exception), status_code=400))
        elif isinstance(res.exception, GenericError):
            return json.dumps(dict(error=str(res.exception), status_code=500))
        return json.dumps(dict(error=str(res.exception), status_code=res.status_code))


services = Services(
    os.environ.get("MAINNET_GATEWAY", ""),
    os.environ.get("DEVNET_GATEWAY", "")
)

app: Any = MyBottle()


@app.route('/')
def index():
    return static_file("index.html", root=FOLDER)


@app.route('/static/<filename:path>')
def send_static(filename: Path):
    return static_file(filename, root=FOLDER_STATIC)


@app.route("/api/<network>/accounts/<address>/native")
def get_native_state(network: str, address: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_native_state_of_account(address, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/token/<token>")
def get_token_state(network: str, address: str, token: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_token_state_of_account(address, token, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/pairs")
def get_pairs(network: str, address: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_pairs_of_account(address, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/pairs/<key>")
def get_pair(network: str, address: str, key: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_pair_of_account(address, key, time, block_nonce)
    return response.to_dictionary()


def parse_query_parameters():
    query: Any = request.query
    timestamp: str = query.timestamp
    block_nonce: int = query.blockNonce

    if timestamp and block_nonce:
        raise RequestError("only one of the following can be specified: 'timestamp', 'blockNonce'")

    try:
        timestamp_parsed = parse_time(timestamp) if timestamp else None
        block_nonce_parsed = int(block_nonce) if block_nonce else None
    except:
        raise RequestError("cannot parse query parameters: 'timestamp', 'blockNonce'")

    return timestamp_parsed, block_nonce_parsed


def parse_time(timestamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
