from src.trainer.date.description import isSerial


assert isSerial("16-1001-078")
assert not isSerial("1917.04.02")