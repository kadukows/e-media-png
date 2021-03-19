from dataclasses import dataclass
from typing import List
import numpy as np
from libs.chunk_resources import ChunkResources
from libs.helpers import from_bytes_dataclass

resources = ChunkResources()

class Chunk:
    pass

class AbstractSingleDataChunk(Chunk):
    def __repr__(self):
        return self.data.__repr__()




@resources.register
class IHDR(AbstractSingleDataChunk):
    @dataclass(frozen=True)
    class Data:
        width: np.uint32
        height: np.uint32
        bit_depth: np.uint8
        color_type: np.uint8
        compression_method: np.uint8
        filter_method: np.uint8
        interlace_method: np.uint8

    chunk_name = 'IHDR'

    def __init__(self, chunks, b):
        self.data = from_bytes_dataclass(self.Data, b)
