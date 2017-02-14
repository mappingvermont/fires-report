from hyp.marshmallow import Responder
from firesreport.schemas import ErrorSchema


class ErrorResponder(Responder):
    TYPE = 'errors'
    SERIALIZER = ErrorSchema
