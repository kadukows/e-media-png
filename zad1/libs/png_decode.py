from typing import List
import numpy as np
import libs.chunk as chunk


PNG_HEADER = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

def decode(binary_file) -> List[chunk.Chunk]:
    head = binary_file.read(8)
    if head != PNG_HEADER:
        return []

    result = []
    chunk_name = ''

    while not binary_file.closed:
        length = np.frombuffer(binary_file.read(4), dtype='>u4')
        if len(length) == 1:
            length = length[0]
            chunk_name = binary_file.read(4).decode('ascii')

            if chunk_name == 'IEND':
                break

            if chunk_name in chunk.resources.get():
                chunk_bytes = binary_file.read(length)
                crc = binary_file.read(4)
                result.append(chunk.resources.get()[chunk_name](result, chunk_bytes))
            else:
                binary_file.seek(length + 4, 1)

    return result
