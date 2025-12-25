
from .types import Bit, Int64
from typing import cast

class Conversion:

    @staticmethod
    def int64_to_bit_list(value: Int64) -> list[Bit]:
        """Convert an integer to a list of 64 bits."""
        L: list[Bit] = []
        for i in range(63, 0 - 1, -1):
            bit = cast(Bit, (value >> i) & 1)
            L.append(bit)
        return L

    @staticmethod
    def bit_list_to_int64(bits: list[Bit]) -> Int64:
        """Convert a list of 64 bits to a 64-bit integer."""
        if len(bits) != 64:
            raise ValueError("The bit list must contain exactly 64 bits.")
        value: Int64 = cast(Int64, 0)
        for i in range(64):
            bit = bits[i]
            value |= cast(Int64, bit << (63 - i))
        return value

    @staticmethod
    def bytes_to_bit_list(s: bytes) -> list[Bit]:
        """Convert a string expressed as bytes to a list of bits."""
        L: list[Bit] = []
        for byte in s:
            L = L + cast(list[Bit], [(byte >> i) & 1 for i in range(7, -1, -1)])
        return L

    @staticmethod
    def bit_list_to_bytes(bits: list[Bit]) -> bytes:
        """Convert a list of bits to a string."""
        if len(bits) % 8 != 0:
            raise ValueError("The length of the bit list must be a multiple of 8.")

        bytes_list: list[int] = []
        for i in range(0, len(bits), 8):
            group = bits[i:i+8]
            byte = 0
            for bit in group:
                byte = (byte << 1) | bit
            bytes_list.append(byte)
        return bytes(bytes_list)
