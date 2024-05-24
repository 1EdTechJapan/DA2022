from typing import Optional, List
from enum import IntEnum
import pandas as pd
from property.common import LanguageMap

# These are our original properties

CEFR_INT_2_STR = ["A1", "A2", "B1", "B2", "C1", "C2"]

class Cefr(IntEnum):
    A1 = 0
    A2 = 1
    B1 = 2
    B2 = 3
    C1 = 4
    C2 = 5

# CefrScore property
class CefrScore:
    def __init__(
            self,
            category: str,
            cefr_level: Cefr,
            score: float,
            strength: LanguageMap,
            weakness: LanguageMap
        ) -> None:

        self.__cefr_score = {
            "category": category,
            "cefrLevel": CEFR_INT_2_STR[cefr_level],
            "score": score,
            "strength": strength(),
            "weakness": weakness()
        }

    def __call__(self) -> dict:
        return self.__cefr_score

# Interval type
class Interval:
    def __init__(
            self,
            interval_id: str,
            start_time_sec: float,
            end_time_sec: float,
            text: str
        ) -> None:
        self._interval_id = interval_id
        self._start_time_sec = start_time_sec
        self._end_time_sec = end_time_sec
        self._text = text

    @property
    def interval_id(self) -> str:
        return self._interval_id
    
    @property
    def start_time_sec(self) -> float:
        return self._start_time_sec

    @property
    def end_time_sec(self) -> float:
        return self._end_time_sec
    
    @property
    def text(self) -> str:
        return self._text

    def __call__(self) -> dict:
        interval = {
            "id": self._interval_id, 
            "start": self._start_time_sec, 
            "end": self._end_time_sec, 
            "text": self._text
        }
        return interval

# Tier type for raw features extracted during dialog
class Tier:
    def __init__(
            self,
            tier_name: str,
            intervals: List[Interval]
        ) -> None:
        self._tier_name = tier_name
        self._intervals = intervals

    @property
    def tier_name(self) -> str:
        return self._tier_name
    
    @property
    def intervals(self) -> List[Interval]:
        return self._intervals
    
    def __call__(self) -> dict:
        tier = {
            "tierName": self._tier_name,
            "intervals": [interval() for interval in self._intervals]
        }
        return tier
    
    @classmethod
    def from_pandas(
        cls, 
        tier_name: str, 
        interval_dataframe: pd.DataFrame,
        id_column: Optional[str] = "id",
        start_column: Optional[str] = "start",
        end_column: Optional[str] = "end",
        text_column: Optional[str] = "text"
    ):
        intervals = []
        for idx in interval_dataframe.index:
            interval = Interval(
                interval_id=interval_dataframe.at[idx, id_column],
                start_time_sec=interval_dataframe.at[idx, start_column],
                end_time_sec=interval_dataframe.at[idx, end_column],
                text=interval_dataframe.at[idx, text_column]
            )
            intervals.append(interval)

        return cls(tier_name, intervals)