class ChunkResources:
    def __init__(self):
        self._chunk_name_to_chunk = dict()

    def get(self):
        return self._chunk_name_to_chunk

    def register(self, target, name=None):
        if name:
            self._chunk_name_to_chunk[name] = target
        else:
            self._chunk_name_to_chunk[target.chunk_name] = target
