"""
This type stub file was generated by pyright.
"""

from typing import Any, Dict

class ProxyNetworkProvider:
    def __init__(self, url: str) -> None:
        ...
    
    def do_get(self, url: str) -> GenericResponse:
        ...
    
    def do_post(self, url: str, payload: Any) -> GenericResponse:
        ...
    


class GenericResponse:
    def __init__(self, data: Any) -> None:
        ...
    
    def get(self, key: str, default: Any = ...) -> Any:
        ...
    
    def to_dictionary(self) -> Dict[str, Any]:
        ...
    


class GenericError(Exception):
    def __init__(self, url: str, data: Any) -> None:
        ...
    


