class BaseFileType:
    extensions = []
    indexer_key = ''

    @classmethod
    def matches_extension(cls, extension: str) -> bool:
        return extension.lower() in cls.extensions

class DocumentFile(BaseFileType):
    extensions = ['.txt', '.md']
    indexer_key = 'document'

class ImageFile(BaseFileType):
    extensions = []
    indexer_key = 'image'

