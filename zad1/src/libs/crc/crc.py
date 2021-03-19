import numpy as np

from libs.crc import CRC_TABLE

# crc computation as defined in https://www.w3.org/TR/2003/REC-PNG-20031110/#D-CRCAppendix

def _update_crc(crc: np.uint32, buf: bytes) -> np.uint32:
    c = np.uint32(crc)
    for n in range(len(buf)):
        c = np.bitwise_xor(CRC_TABLE[ np.bitwise_and(np.bitwise_xor(c, buf[n]), 0xff) ], np.right_shift(c, 8))
    return c


def crc(buf: bytes) -> np.uint32:
    return np.bitwise_xor(_update_crc(np.uint32(0xffffffff), buf), 0xffffffff)
