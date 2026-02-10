from pydantic import BaseModel
from typing import Any

from src.common.const import ResponseStatus

class Response(BaseModel):
    status: str
    message: str
    data: Any
    
def response(status: ResponseStatus, message: str, status_code: int, data: Any = None):
    rsp = Response(
                status = status,
                message = str(message),
                data = data
            )
    return rsp.model_dump(mode='json'), status_code

def unauthorized_response(msg='Not authenticated'):
    rsp = Response(
                status = ResponseStatus.Error,
                message = str(msg),
                data=None
            )
    return rsp.model_dump(mode='json', exclude={'data'}), 401

def internal_server_error(msg: str = 'Internal Server Error'):
    rsp = Response(
                status = ResponseStatus.Error,
                message = str(msg),
                data = None
            )
    return rsp.model_dump(mode='json', exclude={'data'}), 500

def bad_request_error(msg : str = 'Missing required parameter'):
    rsp = Response(
                status = ResponseStatus.Error,
                message = str(msg),
                data = None
            )
    return rsp.model_dump(mode='json', exclude={'data'}), 400

def ok(message: str = ResponseStatus.Success.name, 
       data: Any = None):
    rsp = Response(
                status = ResponseStatus.Success,
                message = str(message),
                data = data
            )
    return rsp.model_dump(mode='json'), 200