from hyp.marshmallow import Responder
from fires_report.schemas import ErrorSchema


class ErrorResponder(Responder):
    TYPE = 'errors'
    SERIALIZER = ErrorSchema
