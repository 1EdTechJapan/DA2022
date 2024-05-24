from typing import Optional, Tuple
from property.common import Extensions, Duration

# score property
class Score:
    def __init__(
            self,
            scaled: Optional[float] = None,
            raw: Optional[float] = None,
            min_max: Optional[Tuple[float, float]] = None,
        ) -> None:
        score = {}

        if self.validate_scaled(scaled):
            if scaled is not None:
                score["scaled"] = scaled
        else:
            raise ValueError(f"scaled must be between -1 and 1, but {scaled}")

        if raw is not None:
            score["raw"] = raw

        if self.validate_min_max(min_max):
            if min_max is not None:
                score["min"] = min_max[0]
                score["max"] = min_max[1]
        else:
            raise ValueError(f"min score is larger than max score ({min_max})")

        self.__score = score

    def __call__(self) -> dict:
        return self.__score

    def validate_scaled(self, scaled: float) -> bool:
        if scaled is None:
            return True
        
        if -1 <= scaled and scaled <= 1:
            return True
        return False
    
    def validate_min_max(self, min_max: Tuple[float, float]) -> bool:
        if min_max is None:
            return True

        min_score = min_max[0]
        max_score = min_max[1]

        if min_score > max_score:
            return False
        
        return True

# result template
class Result:
    def __init__(
            self,
            score: Optional[Score] = None,
            success: Optional[bool] = None,
            completion: Optional[bool] = None,
            response: Optional[str] = None,
            duration: Optional[Duration] = None,
            extensions: Optional[Extensions] = None
        ) -> None:
        result = {}

        if score is not None:
            result["score"] = score()
        
        if success is not None:
            result["success"] = success
        
        if completion is not None:
            result["completion"] = completion

        if response is not None:
            result["response"] = response

        if duration is not None:
            result["duration"] = duration()

        if extensions is not None:
            result["extensions"] = extensions()

        self.__result = result

    def __call__(self) -> dict:
        return self.__result