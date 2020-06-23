from src.jobs.TranslationJobABC import TranslationJob


class RemoteTranslationJob(TranslationJob):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        pass
