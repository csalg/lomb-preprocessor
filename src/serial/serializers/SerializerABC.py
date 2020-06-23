from abc import ABC, abstractmethod

class SerializerABC(ABC):
    
    @abstractmethod
    def __init__(self, filename, source_language, target_language):
        pass

    @abstractmethod
    def get_translation_dictionary(self):
       pass 

    @abstractmethod
    def set_translation_dictionary(self, new_dictionary):
       pass

    @abstractmethod
    def get_lemmas_dictionary(self):
        pass

    @abstractmethod
    def set_lemmas_dictionary(self, new_dictionary):
        pass

    @abstractmethod
    def save_to_file(self, output_filename):
        pass