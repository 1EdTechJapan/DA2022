from typing import Optional, Union, List
from uuid import UUID
from property.common import Language, Extensions
from property.actor import AgentActor, GroupActor
from property.object import ActivityObject

# context activity properties
class ContextActivity:
    def __init__(
            self,
            parent: Optional[List[ActivityObject]] = None,
            grouping: Optional[List[ActivityObject]] = None,
            category: Optional[List[ActivityObject]] = None,
            other: Optional[List[ActivityObject]] = None
        ) -> None:
        context_activity = {}

        if parent is not None:
            context_activity["parent"] = [activity() for activity in parent]
        if grouping is not None:
            context_activity["grouping"] = [activity() for activity in grouping]
        if category is not None:
            context_activity["category"] = [activity() for activity in category]
        if other is not None:
            context_activity["other"] = [activity() for activity in other]
        
        self.__context_activity = context_activity

    def __call__(self) -> dict:
        return self.__context_activity

# statement reference properties
class StatementReference:
    def __init__(
            self,
            pre_existing_statement_uuid: UUID
        ) -> None:
        self.__statement_reference = {"objectType": "StatementRef", "id": str(pre_existing_statement_uuid)}

    def __call__(self) -> dict:
        return self.__statement_reference
    
# context template
class Context:
    def __init__(
            self,
            registration: Optional[UUID] = None,
            instructor: Optional[Union[AgentActor, GroupActor]] = None,
            team: Optional[GroupActor] = None,
            context_activities: Optional[ContextActivity] = None,
            revision: Optional[str] = None,
            platform: Optional[str] = None,
            language: Optional[Union[str, Language]] = None,
            statement: Optional[StatementReference] = None,
            extensions: Optional[Extensions] = None
        ) -> None:
        context = {}

        if registration is not None:
            context["registration"] = str(registration)
        
        if instructor is not None:
            context["instructor"] = instructor()

        if team is not None:
            context["team"] = team()

        if context_activities is not None:
            context["contextActivities"] = context_activities()

        if revision is not None:
            context["revision"] = revision

        if platform is not None:
            context["platform"] = platform

        if language is not None:
            if isinstance(language, str):
                language = Language(str)
            context["language"] = language

        if statement is not None:
            context["statement"] = statement()

        if extensions is not None:
            context["extensions"] = extensions()

        self.__context = context

    def __call__(self) -> dict:
        return self.__context