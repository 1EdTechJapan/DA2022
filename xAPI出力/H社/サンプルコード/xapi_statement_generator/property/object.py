from typing import Optional, Union, List
from copy import deepcopy
from property.common import IRI, LanguageMap, Extensions

# interaction component properties
class InteractionComponent:
    def __init__(
            self,
            item_id: str,
            description: Optional[LanguageMap] = None
        ) -> None:
        interaction_component = {"id": item_id}
        
        if description is not None:
            interaction_component["description"] = description()

        self.__interaction_component = interaction_component

    def __call__(self) -> dict:
        return self.__interaction_component

# performance interaction proeprties
class PerformanceInteraction:
    def __init__(
            self, 
            correct_responses_pattern: Optional[List[str]] = None,
            steps: Optional[List[InteractionComponent]] = None
        ) -> None:
        performance = {"interactionType": "performance"}

        if steps is not None:
            performance["steps"] = [step() for step in steps]
        
        if correct_responses_pattern is not None:
            if len(steps) != len(correct_responses_pattern):
                raise ValueError(f"length of correct_response_pattern does not match length of steps")

            pattern = []
            for correct_response, step in zip(correct_responses_pattern, steps):
                item_id = step()["id"]
                pattern.append(f"{item_id}[.]{correct_response}")
            
            performance["correctResponsesPattern"] = "[,]".join(pattern)

        self.__performance = performance

    def __call__(self) -> dict:
        return self.__performance

# other interaction properties
class OtherInteraction:
    def __init__(
            self,
            correct_responses_pattern: Optional[str] = None
        ) -> None:
        other = {"interactionType": "other"}

        if correct_responses_pattern is not None:
            other["correctResponsesPattern"] = correct_responses_pattern

        self.__other = other

    def __call__(self) -> dict:
        return self.__other

# activity defininition properties
class ActivityDefinition:
    def __init__(
            self, 
            name: Optional[LanguageMap] = None,
            description: Optional[LanguageMap] = None,
            type: Optional[IRI] = None,
            moreinfo: Optional[IRI] = None,
            interaction_properties: Optional[Union[PerformanceInteraction, OtherInteraction]] = None,
            extensions: Optional[Extensions] = None
        ) -> None:
        if interaction_properties is not None:
            activity = deepcopy(interaction_properties())
        else:
            activity = {}
        
        if name is not None:
            activity["name"] = name()
        if description is not None:
            activity["description"] = description()
        if type is not None:
            activity["type"] = type()
        if moreinfo is not None:
            activity["moreinfo"] = moreinfo()
        if extensions is not None:
            activity["extensions"] = extensions()

        self.__activity = activity

    def __call__(self) -> dict:
        return self.__activity

# activity template
class ActivityObject:
    def __init__(
            self,
            object_id: IRI,
            object_type: Optional[str] = "Activity",
            definition: Optional[ActivityDefinition] = None
        ) -> None:
        activity_object = {"id": object_id()}

        if object_type is not None:
            activity_object["objectType"] = object_type     

        if definition is not None:
            activity_object["definition"] = definition()

        self.__activity_object = activity_object

    def __call__(self) -> dict:
        return self.__activity_object