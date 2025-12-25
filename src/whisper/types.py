from typing import NewType, TypeVar

Bit = NewType('Bit', int) # a bit is either 0 or 1
Int64 = NewType('Int64', int)
Vector = list[Bit]
T = TypeVar("T")

