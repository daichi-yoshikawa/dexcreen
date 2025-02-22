import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv


load_dotenv()

@dataclass(frozen=True)
class _Constants:
  DB_TYPE: str = 'sqlite'
  CREDENTIAL_DELIMITER: str = ' '

CONSTANTS = _Constants()


@dataclass(frozen=True)
class _DexcomConstant:
  SENSOR_MAX_NUM: int = 4
  TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S'

DEXCOM = _DexcomConstant()


@dataclass(frozen=True)
class _MonitorConstant:
  MANUFACTURES: List[str] = field(default_factory=lambda: ['waveshare'])
  MODULES: List[str] = field(default_factory=lambda: [
    'epd7in5_V2',
  ])

MONITOR = _MonitorConstant()
