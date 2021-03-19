import numpy as np
# crc computation as defined in https://www.w3.org/TR/2003/REC-PNG-20031110/#D-CRCAppendix

CRC_TABLE = np.ndarray([256], dtype=np.uint32)

for n in range(256):
    c = np.uint32(n)
    for k in range(8):
        if np.bitwise_and(c, 1):
            c = np.bitwise_xor(np.uint32(0xedb88320), np.right_shift(c, 1))
        else:
            c = np.right_shift(c, 1)
    CRC_TABLE[n] = c
