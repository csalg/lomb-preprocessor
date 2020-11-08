import os
import webvtt

from serial.serializers.VttSerializer import VttSerializer
from serial.serializers.TxtSerializer import TxtSerializer
from serial.serializers.EpubSerializer import EpubSerializer

extensions_to_serializers = {
    'vtt': VttSerializer,
    'txt': TxtSerializer,
    # 'epub': EpubSerializer,
    'epub': TxtSerializer.from_epub,
    'html': TxtSerializer.from_epub,
}

def convert(filename):
    _, extension = os.path.splitext(filename)
    extension = extension[1:]
    if extension in extensions_to_serializers:
        converter = converters[extension]
    elif filename[0:4] == 'http':
        converter = TxtSerializer.from_website
    else:
        raise Exception(f'Serializer not found for {filename}')
    return converter(filename)

def create(extension):
    return extensions_to_serializers[extension]
    
def srt_to_vtt(filename):
    subs = webvtt.from_srt(filename)
    subs.save()
    title, _ = os.path.splitext(filename)
    return title + '.vtt'

converters = {
    'srt': srt_to_vtt
}


is_recognized_extension = \
    lambda extension : extension in extensions_to_serializers.keys() \
                        or extension in converters.keys()

requires_conversion = lambda extension : extension in converters.keys()
