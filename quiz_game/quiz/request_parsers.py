import json

from rest_framework.parsers import BaseParser


class PlainTextParser(BaseParser):
    """
    Plain text parser to JSON format.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        try:
            data = stream.read()
            return json.loads(data)
        except Exception:
            return stream.read()
