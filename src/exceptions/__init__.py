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


class UnAuthenticatedError(HTTPException):
    code = 401
    description = 'Unauthorized: Authentication is required to access this resource.'


class BadResponseError(HTTPException):
    code = 400
    description = "Bad Response: server responding with unreadable data please inform admins"
