from rest_framework.parsers import MultiPartParser


class SingleValuesMultiPartParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        data = super().parse(stream, media_type, parser_context)
        data.data = data.data.dict()
        for key, value in list(data.data.items()):
            if value == "null":
                data.data[key] = None
        return data
