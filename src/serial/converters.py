from pycaption import *

def detect_and_convert_captions(filename):
    with open(filename, 'rb') as file:
        caps = file.read().decode('utf-8')
        print(caps)
        converter = CaptionConverter()
        converter.read(caps, DFXPReader())
        print(converter.write(WebVTTWriter))

        assert False