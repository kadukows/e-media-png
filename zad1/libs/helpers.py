from dataclasses import fields
import numpy as np
'''
def static_byte_size_dec(target):
    result = sum(int(np.dtype(field.type).itemsize) for field in fields(target))

    def func():
        return result

    target.byte_size = func
    return target
'''

def class_byte_size(target):
    return sum(int(np.dtype(field.type).itemsize) for field in fields(target))

def from_bytes_dataclass(result_class, b: bytes):
    assert len(b) % class_byte_size(result_class) == 0, 'Bytes have wrong size'

    b_idx = 0
    decoded_bytes = []

    for field in fields(result_class):
        dt = np.dtype(field.type)  # create custom datatype
        dt = dt.newbyteorder('>')  # set applicable byte order

        field_byte = b[b_idx : b_idx + dt.itemsize]  # bytes of that field
        decoded_bytes.append(np.frombuffer(field_byte, dt)[0])  # decode bytes with correct type

        b_idx += dt.itemsize  # keep track of byte position

    return result_class(*decoded_bytes)

def to_bytes_dataclass(data_class_instance):
    pass
