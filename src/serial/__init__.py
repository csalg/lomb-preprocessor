import os

from serial._serializers.TxtSerializer import TxtSerializer
from serial._serializers.VttSerializer import VttSerializer

extensions_to_serializers = {
    'vtt': VttSerializer,
    'srt': VttSerializer.from_srt,
    'txt': TxtSerializer,
    'epub': TxtSerializer.from_epub,
    'html': TxtSerializer.from_html
}


def create_constructor(filename):
    _, extension = os.path.splitext(filename)
    extension = extension[1:]
    if extension in extensions_to_serializers:
        constructor = extensions_to_serializers[extension]
    elif filename[0:4] == 'http':
        constructor = TxtSerializer.from_website
    else:
        raise Exception(f'Serializer not found for {filename}')
    return constructor


is_recognized_extension = \
    lambda extension : extension in extensions_to_serializers.keys()