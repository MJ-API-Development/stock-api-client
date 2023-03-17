from werkzeug.exceptions import HTTPException


class InvalidSignatureError(HTTPException):
    code = 400
    description = 'The signature is invalid.'


class ServerInternalError(HTTPException):
    code = 500
    description = 'An internal server error occurred.'


class UnresponsiveServer(HTTPException):
    code = 503
    description = 'The server is currently unavailable and cannot process requests.'
