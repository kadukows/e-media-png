from dataclasses import dataclass
from typing import List
import numpy as np
from .chunk_resources import ChunkResources
from .crc.crc import crc as calc_crc

resources = ChunkResources()
BigEndian_uint32 = np.dtype('>u4')
BigEndian_uint16 = np.dtype('>u2')

class Chunk:
    def to_bytes(self) -> bytes:
        chunk_name = self.chunk_name.encode('ascii')
        chunk_bytes = self.data.tobytes()

        result = (
            np.array([self.data.nbytes], dtype=BigEndian_uint32).tobytes()
            + chunk_name
            + chunk_bytes
            + np.array([calc_crc(chunk_name + chunk_bytes)], dtype=BigEndian_uint32).tobytes()
        )

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

    def __str__(self):
        result = "IHDR chunk: \n"
        for name in self.Data.names:
            result += f"{name}: {self.data[name]}\n"
        return result


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

    _chunk_bytes = b'\x00\x00\x00\x00IEND' + np.array([calc_crc(b'IEND')], dtype=BigEndian_uint32).tobytes()
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

    def __str__(self):
        return f"sRGB Chunk Data:\n\trendering intent: {self.data['rendering_intent']}"



@resources.register
class Chunk_tIME(Chunk):
    Data = np.dtype([
        ('Year', BigEndian_uint16),
        ('Month', np.uint8),
        ('Day', np.uint8),
        ('Hour', np.uint8),
        ('Minute', np.uint8),
        ('Second', np.uint8),
    ])

    chunk_name = 'tIME'

    def __str__(self):
     return "tIME Chunk Data: " + '\n' + \
            "Year: " + str(self.data["Year"]) + '\n' \
            "Month: " + str(self.data["Month"]) + '\n' \
            "Day: " + str(self.data["Day"]) + '\n' \
            "Hour: " + str(self.data["Hour"]) + '\n' \
            "Minute: " + str(self.data["Minute"]) + '\n' \
            "Second: " + str(self.data["Second"]) + '\n' \


    def __init__(self, chunks, b):
        assert len(b) == self.Data.itemsize
        self.data = np.frombuffer(b, dtype=self.Data)



@resources.register
class Chunk_tEXt(Chunk):
    chunk_name = 'tEXt'

    def __str__(self):
     return "tEXt Chunk Data: " + '\n' + \
            "Keyword: " + self.Keyword + '\n' + \
            "Text: " + self.Text + '\n'

    def __init__(self, chunks, b):
        self.data = b
        [self.Keyword, self.Text ] = self.data.decode('iso-8859-1').split('\0')
        assert len(b) == len(bytes(self.Keyword + self.Text + '\0', 'iso-8859-1'))


@resources.register
class Chunk_gAMA(Chunk):
    Data = np.dtype([
        ('Gamma', np.uint32),
    ])

    chunk_name = 'gAMA'

    def __str__(self):
        #get data and replace square brackets
        gamma_divisor = self.data["Gamma"][0] #int(str(self.data["Gamma"]).replace('[', "").replace(']',""))
        return "gAMA Chunk Data: " + '\n' + \
               str(1) + "/" + str(1000/gamma_divisor) + '\n'

    def __init__(self, chunks, b):
        assert len(b) == self.Data.itemsize
        self.data = np.frombuffer(b, dtype=self.Data)

@resources.register
class Chunk_bKGD(Chunk):
    DataColorTypes04 = np.dtype([
        ('Greyscale', np.uint16),
    ])

    DataColorTypes26 = np.dtype([
        ('Red', np.uint16),
        ('Green', np.uint16),
        ('Blue', np.uint16),
    ])

    DataColorTypes3 = np.dtype([
        ('PalleteIndex', np.uint8),
    ])

    chunk_name = 'bKGD'

    def __str__(self):
        result = "bKGD Chunk Data: \n"
        if self.Data == self.DataColorTypes04:
            result += "Greyscale: " + str(self.data["Greyscale"])
        elif self.Data == self.DataColorTypes26:
            result += "Red: " + str(self.data["Red"]) + '\n' + \
                      "Green: " + str(self.data["Green"]) + '\n' + \
                      "Blue: " + str(self.data["Blue"]) + '\n'
        elif self.Data == self.DataColorTypes3:
            result += "Pallete Index: " + str(self.data["PalleteIndex"])

        return result



    def __init__(self, chunks, b):
        ihdr_chunk = next((chunk for chunk in chunks if chunk.chunk_name == 'IHDR'), None)
        if not ihdr_chunk:
            raise RuntimeError('Trying to load bKGD chunk without IHDR chunk')

        color_type=ihdr_chunk.data["color_type"][0]

        if color_type == 0 or color_type == 4:
            self.Data = self.DataColorTypes04
        elif color_type == 2 or color_type == 6:
            self.Data = self.DataColorTypes26
        elif color_type == 3:
            self.Data = self.DataColorTypes3
        else:
            raise RuntimeError('IHDR chunk contains not recognised color type!')

        self.data = np.frombuffer(b, dtype=self.Data)
        assert len(b) == self.Data.itemsize


@resources.register
class Chunk_cHRM(Chunk):
    Data = np.dtype([
        ('white_point_x', np.uint32),
        ('white_point_y', np.uint32),
        ('red_x', np.uint32),
        ('red_y', np.uint32),
        ('green_x', np.uint32),
        ('green_y', np.uint32),
        ('blue_x', np.uint32),
        ('blue_y', np.uint32),
    ])

    chunk_name = 'cHRM'

    def __str__(self):
        return "cHRM  Chunk Data: " + '\n' + \
               "White point x: " + str(self.data["white_point_x"][0] / 100000) + '\n' + \
               "White point y: " + str(self.data["white_point_y"][0] / 100000) + '\n' + \
               "Red x: " + str(self.data["red_x"][0] / 100000) + '\n' + \
               "Red y: " + str(self.data["red_y"][0] / 100000) + '\n' + \
               "Green x: " + str(self.data["green_x"][0] / 100000) + '\n' + \
               "Green y: " + str(self.data["green_y"][0] / 100000) + '\n' + \
               "Blue x: " + str(self.data["blue_x"][0] / 100000) + '\n' + \
               "Blue y: " + str(self.data["blue_y"][0] / 100000) + '\n'

    def __init__(self, chunks, b):
        assert len(b) == self.Data.itemsize
        self.data = np.frombuffer(b, dtype=self.Data)
