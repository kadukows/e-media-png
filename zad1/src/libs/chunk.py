from dataclasses import dataclass
from typing import List
import numpy as np
from libs.chunk_resources import ChunkResources
from libs.crc.crc import crc as calc_crc

resources = ChunkResources()
BigEndian_uint32 = np.dtype('>u4')

class Chunk:
    def to_bytes(self) -> bytes:
        chunk_name = self.chunk_name.encode('ascii')
        chunk_bytes = self.data.tobytes()

        result = (
            np.array([self.data.nbytes], dtype=BigEndian_uint32).tobytes()
            + chunk_name
            + chunk_bytes
            + calc_crc(chunk_name + chunk_bytes).astype(BigEndian_uint32).tobytes()
        )
        print(len(result))
        return result


@resources.register
class Chunk_IHDR(Chunk):
    Data = np.dtype([
        ('width', BigEndian_uint32),
        ('height', BigEndian_uint32),
        ('bit_depth', np.uint8),
        ('color_type', np.uint8),
        ('compression_method', np.uint8),
        ('filter_method', np.uint8),
        ('interlace_method', np.uint8)
    ])

    chunk_name = 'IHDR'

    def __init__(self, chunks, b):
        assert len(b) == self.Data.itemsize
        self.data = np.frombuffer(b, dtype=self.Data)

@resources.register
class Chunk_PLTE(Chunk):
    Data = np.dtype([
        ('red', np.uint8),
        ('green', np.uint8),
        ('blue', np.uint8)
    ])

    chunk_name = 'PLTE'

    def __init__(self, chunks, b):
        assert len(b) % self.Data.itemsize == 0

        ihdr_chunk = next((chunk for chunk in chunks if chunk.chunk_name == 'IHDR'), None)
        if not ihdr_chunk:
            raise RuntimeError('Trying to load PLTE chunk without IHDR chunk')

        self.data = np.frombuffer(b, dtype=self.Data)

@resources.register
class Chunk_IDAT(Chunk):
    chunk_name = 'IDAT'

    def __init__(self, chunks, b):
        self.data = np.frombuffer(b, dtype=np.uint8)

@resources.register
class Chunk_IEND(Chunk):
    chunk_name = 'IEND'

    _chunk_bytes = b'\x00\x00\x00\x00IEND'
    _crc = calc_crc(b'IEND')

    def __init__(self, chunks, b):
        assert len(b) == 0

    def to_bytes(self) -> bytes:
        return self._chunk_bytes

@resources.register
class Chunk_sRGB(Chunk):
    Data = np.dtype([
        ('rendering_intent', np.uint8)
    ])

    chunk_name = 'sRGB'

    def __init__(self, chunks, b):
        assert len(b) == self.Data.itemsize
        self.data = np.frombuffer(b, dtype=self.Data)
