from typing import List
import numpy as np
import libs.chunk as chunk
from libs.crc.crc import crc as calc_crc

PNG_HEADER = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

def decode(binary_file) -> List[chunk.Chunk]:
    head = binary_file.read(8)
    if head != PNG_HEADER:
        return []

    result = []
    chunk_name = ''

    while not binary_file.closed and chunk_name != 'IEND':
        length = np.frombuffer(binary_file.read(4), dtype='>u4')
        if len(length) == 1:
            length = length[0]
            chunk_name = binary_file.read(4).decode('ascii')
            if chunk_name in chunk.resources.get():
                chunk_bytes = binary_file.read(length)
                crc = np.frombuffer(binary_file.read(4), dtype='>u4')
                if len(crc) == 1:
                    crc = crc[0]
                    assert crc == calc_crc(chunk_name.encode('ascii') + chunk_bytes), 'CRC is wrong in decoded file'
                    result.append(chunk.resources.get()[chunk_name](result, chunk_bytes))
            else:
                binary_file.seek(length + 4, 1)


    return result
