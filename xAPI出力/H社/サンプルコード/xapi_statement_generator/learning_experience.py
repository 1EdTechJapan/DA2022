from typing import Optional, Union
from pathlib import Path
import uuid, json
from property import *

# learning experience template
class LearningExperience:
    def __init__(
            self,
            actor: Union[AgentActor, GroupActor],
            verb: Verb,
            object: ActivityObject,
            result: Optional[Result] = None,
            context: Optional[Context] = None,
            timestamp: Optional[Union[Timestamp, bool]] = None,
            authority: Optional[Union[AgentActor, GroupActor]] = None,
            version: Optional[Version] = None,
            attachment: Optional[Attachment] = None
        ) -> None:
        statement = {
            "id": str(uuid.uuid4()),
            "actor": actor(),
            "verb": verb(),
            "object": object()
        }

        if result is not None:
            statement["result"] = result()
        
        if context is not None:
            statement["context"] = context()
        
        if timestamp:
            if isinstance(timestamp, bool):
                timestamp = Timestamp.now()
            statement["timestamp"] = timestamp()

        if authority is not None:
            statement["authority"] = authority()

        if version is not None:
            statement["version"] = version()

        if attachment is not None:
            statement["attachment"] = attachment()

        self.__statement = statement

    def __call__(self) -> dict:
        return self.__statement
    
    # if you want to save statement as json, use this method
    def save_as_json(self, filepath: Union[str, Path], filename_preffix: Optional[str] = None) -> None:
        if isinstance(filepath, (str, Path)):
            filepath = Path(filepath)

        filename = f"{self.__statement['id']}"
        if filename_preffix is not None:
            filename = f"{filename_preffix}_{filename}"
        filename += ".json"
        
        with open(filepath / filename, "w") as f:
            json.dump(self.__statement, f, indent=4, ensure_ascii=False)