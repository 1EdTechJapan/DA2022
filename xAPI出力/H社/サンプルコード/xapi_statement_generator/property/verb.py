from typing import Optional
from property.common import IRI, LanguageMap

# verb template
class Verb:
    def __init__(self, verb_id: IRI, display: Optional[LanguageMap] = None) -> None:
        verb = {"id": verb_id()}

        if display is not None:
            verb["display"] = display()

        self.__verb = verb

    def __call__(self) -> dict:
        return self.__verb