import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv


load_dotenv()

@dataclass(frozen=True)
class _Constants:
  CREDENTIAL_DELIMITER: str = ' '

CONSTANTS = _Constants()


@dataclass(frozen=True)
class _DexcomConstant:
  SENSOR_MAX_NUM: int = 4
  TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S'

DEXCOM = _DexcomConstant()
