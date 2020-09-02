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
}

def convert(filename):
    _, extension = os.path.splitext(filename)
    extension = extension[1:]
    converter = converters[extension]
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
