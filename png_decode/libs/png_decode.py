from typing import List
import numpy as np
from . import png_chunk as chunk
from .crc.crc import crc as calc_crc

PNG_HEADER = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

def decode(binary_file) -> List[chunk.Chunk]:
    head = binary_file.read(8)
    if head != PNG_HEADER:
        return []

    result = []
    chunk_name = ''

    while not binary_file.closed and chunk_name != 'IEND':
        length_bytes = binary_file.read(4)
        length = np.frombuffer(length_bytes, dtype='>u4')
        if len(length) == 1:
            length = length[0]
            chunk_name_bytes = binary_file.read(4)
            chunk_name = chunk_name_bytes.decode('ascii')
            if chunk_name in chunk.resources.get():
                chunk_bytes = binary_file.read(length)
                crc_bytes = binary_file.read(4)
                crc = np.frombuffer(crc_bytes, dtype='>u4')
                if len(crc) == 1:
                    crc = crc[0]
                    calculated_crc = calc_crc(chunk_name.encode('ascii') + chunk_bytes)
                    assert crc == calculated_crc, 'CRC is wrong in decoded file, chunk_name: {}, {:b}'.format(chunk_name, crc & calculated_crc)
                    result.append(chunk.resources.get()[chunk_name](result, chunk_bytes))

            else:
                binary_file.seek(length + 4, 1)


    return result
