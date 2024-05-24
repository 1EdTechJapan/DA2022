import json
from typing import Union, Tuple
from pathlib import Path
from copy import deepcopy
from uuid import UUID
from property import *
from learning_experience import LearningExperience
from config import Config

# verbs
ATTEMPTED = Verb(
    verb_id=IRI("http://adlnet.gov/expapi/verbs/attempted"),
    display=LanguageMap(languages="en-US", definitions="attempted")
)

COMPLETED = Verb(
    verb_id=IRI("http://adlnet.gov/expapi/verbs/completed"),
    display=LanguageMap(languages="en-US", definitions="completed")
)

ANSWERED = Verb(
    verb_id=IRI("http://adlnet.gov/expapi/verbs/answered"),
    display=LanguageMap(languages="en-US", definitions="answered")
)

def load_feedback(overall_cefr_level: Cefr, resources_path: Path) -> str:
    with open(resources_path / "cefr_result_description.json", "r") as f:
        cefr_result_description = json.load(f)
        
    return cefr_result_description["levelDescription"][CEFR_INT_2_STR[overall_cefr_level]]

def load_cefr_overall_description(strengh_category: str, weakness_category: str, resources_path: Path) -> Tuple[LanguageMap, LanguageMap]:
    with open(resources_path / "cefr_result_description.json", "r") as f:
        cefr_result_description = json.load(f)

    strength = LanguageMap(languages="ja", definitions=cefr_result_description["strength"][strengh_category])
    weakness = LanguageMap(languages="ja", definitions=cefr_result_description["weakness"][weakness_category])

    return strength, weakness

def load_cefr_subcategory_description(category: str, cefr_level: Cefr, resources_path: Path) -> Tuple[LanguageMap, LanguageMap]:
    if category == "overall":
        raise ValueError(f"To load overall description, use load_cefr_overall_description()")

    with open(resources_path / "cefr_result_description.json", "r") as f:
        cefr_result_description = json.load(f)

    strength_dict = cefr_result_description["categoryDescription"][category][CEFR_INT_2_STR[cefr_level]]
    weakness_dict = cefr_result_description["categoryDescription"][category][CEFR_INT_2_STR[cefr_level]]

    strength = LanguageMap(
        languages=["ja", "en"], 
        definitions=[strength_dict["ja"], strength_dict["en"]]
    )
    weakness = LanguageMap(
        languages=["ja", "en"], 
        definitions=[weakness_dict["ja"], weakness_dict["en"]]
    )

    return strength, weakness

def generate_cefr_score(
        category: str, 
        cefr_level: Union[int, str, Cefr], 
        cefr_score: float, 
        resource_path: Path,
        strengh_category: Optional[str] = None,
        weakness_category: Optional[str] = None
    ) -> CefrScore:
    if cefr_level in CEFR_INT_2_STR:
        cefr_id = CEFR_INT_2_STR.index(cefr_level)
        cefr_level = Cefr(cefr_id)
    else:
        cefr_level = Cefr(cefr_level)

    if category == "overall":
        strength, weakness = load_cefr_overall_description(
            strengh_category, weakness_category, resource_path
        )
    else:
        strength, weakness = load_cefr_subcategory_description(
            category, cefr_level, resource_path
        )

    cefr_score = CefrScore(
        category=category,
        cefr_level=cefr_level,
        score=cefr_score,
        strength=strength,
        weakness=weakness
    )

    return cefr_score


class LANGXSpeakingLearningExperienceGenerator:
    def __init__(
            self,
            learner_accout_name: str,
            dialog_id: UUID,
            interview_id: str
        ) -> None:
        config = Config()

        self.__actor = AgentActor(
            ifi=InverseFunctionalIdentifier(
                account=Account(home_page=config.HOME_PAGE, name=learner_accout_name)
            )
        )

        self.__category = [
            ActivityObject(
                object_id=IRI(f"http://id.tincanapi.com/activity/lrp/{config.LEARNING_RECORD_PROVIDER}/{config.STATEMENT_VERSION}"),
                object_type=None,
                definition=ActivityDefinition(type=IRI(f"http://id.tincanapi.com/activitytype/source"))
            )
        ]

        self.__version = Version(version=config.STATEMENT_VERSION)

        self.__dialog_id = str(dialog_id)
        self.__interview_id = interview_id
        self.__config = config

        self.__topics = []
        self.__questions = []

    def clear_questions(self) -> None:
        self.__questions = []
        return

    def start(self) -> LearningExperience:
            verb = ATTEMPTED

            object = ActivityObject(
                object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}"),
                definition=ActivityDefinition(
                    name=LanguageMap(languages="en-US", definitions="interview"),
                    description=LanguageMap(languages="en-US", definitions="interview assessment in L2 English"),
                    type=IRI("http://adlnet.gov/expapi/activities/cmi.interaction"),
                    interaction_properties=PerformanceInteraction()
                ),
            )

            context = Context(
                context_activities=ContextActivity(
                    category=self.__category
                ),
                extensions=Extensions(
                    keys=IRI("http://id.tincanapi.com/extension/attempt-id"),
                    values=self.__dialog_id
                )
            )

            statement = LearningExperience(
                actor=self.__actor,
                verb=verb,
                object=object,
                context=context,
                timestamp=True,
                version=self.__version
            )

            return statement

    def complete(
            self,
            overall_score: CefrScore,
            range_score: CefrScore,
            accuracy_score: CefrScore,
            phonology_score: CefrScore,
            fluency_score: CefrScore,
            coherence_score: CefrScore,
            interaction_score: CefrScore,
            level_description: str
        ) -> LearningExperience:
        verb = COMPLETED

        object = ActivityObject(
            object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}"),
            definition=ActivityDefinition(
                name=LanguageMap(languages="en-US", definitions="interview"),
                description=LanguageMap(languages="en-US", definitions="interview assessment in L2 English"),
                type=IRI("http://adlnet.gov/expapi/activities/cmi.interaction"),
                interaction_properties=PerformanceInteraction(
                    steps=self.__topics
                )
            )
        )

        result = Result(
            extensions=Extensions(
                keys=IRI(f"{self.__config.IRI_BASE}/extension/cefr"),
                values=[
                    overall_score(), range_score(), accuracy_score(), phonology_score(),
                    fluency_score(), coherence_score(), interaction_score()
                ]
            )
        )

        context = Context(
            context_activities=ContextActivity(
                category=self.__category
            ),
            extensions=Extensions(
                keys=[
                    IRI("http://id.tincanapi.com/extension/attempt-id"),
                    IRI("http://id.tincanapi.com/extension/feedback")
                ],
                values=[
                    self.__dialog_id,
                    level_description
                ]
            )
        )

        statement = LearningExperience(
            actor=self.__actor,
            verb=verb,
            object=object,
            result=result,
            context=context,
            timestamp=True,
            version=self.__version
        )

        return statement

    def topic_start(
            self,
            topic_id: int,
            topic_name: str,
            difficulty: Union[Cefr, int, str]
        ):
        verb = ATTEMPTED

        object = ActivityObject(
            object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}/topic{topic_id}"),
            definition=ActivityDefinition(
                name=LanguageMap(languages="en-US", definitions="topic"),
                description=LanguageMap(languages="en-US", definitions=topic_name),
                type=IRI("http://adlnet.gov/expapi/activities/cmi.interaction"),
                interaction_properties=PerformanceInteraction()
            ),
        )

        if isinstance(difficulty, (Cefr, int)):
            difficulty = CEFR_INT_2_STR[difficulty]
        elif not(difficulty in CEFR_INT_2_STR):
            raise ValueError(f"Invalid difficulty {difficulty}")

        context = Context(
            context_activities=ContextActivity(
                category=self.__category,
                parent=[
                    ActivityObject(
                        object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}")
                    )
                ]
            ),
            extensions=Extensions(
                keys=[
                    IRI("http://id.tincanapi.com/extension/attempt-id"),
                    IRI("http://id.tincanapi.com/extension/tags")
                ],
                values=[
                    self.__dialog_id,
                    [difficulty]
                ]
            )
        )

        statement = LearningExperience(
            actor=self.__actor,
            verb=verb,
            object=object,
            context=context,
            timestamp=True,
            version=self.__version
        )

        self.__topics.append(
            InteractionComponent(
                item_id=f"topic{topic_id}",
                description=LanguageMap(
                    languages="en-US",
                    definitions=topic_name
                )
            )
        )

        return statement

    def topic_complete(
            self,
            topic_id: int,
            topic_name: str,
            difficulty: Union[Cefr, int, str],
            level_up: Optional[bool] = None
        ):
        verb = COMPLETED

        object = ActivityObject(
            object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}/topic{topic_id}"),
            definition=ActivityDefinition(
                name=LanguageMap(languages="en-US", definitions="topic"),
                description=LanguageMap(languages="en-US", definitions=topic_name),
                type=IRI("http://adlnet.gov/expapi/activities/cmi.interaction"),
                interaction_properties=PerformanceInteraction(
                    steps=deepcopy(self.__questions)
                )
            ),
        )

        if isinstance(difficulty, (Cefr, int)):
            difficulty = CEFR_INT_2_STR[difficulty]
        elif not(difficulty in CEFR_INT_2_STR):
            raise ValueError(f"Invalid difficulty {difficulty}")

        context = Context(
            context_activities=ContextActivity(
                category=self.__category,
                parent=[
                    ActivityObject(
                        object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}")
                    )
                ]
            ),
            extensions=Extensions(
                keys=[
                    IRI("http://id.tincanapi.com/extension/attempt-id"),
                    IRI("http://id.tincanapi.com/extension/tags")
                ],
                values=[
                    self.__dialog_id,
                    [difficulty]
                ]
            )
        )

        if level_up is not None:
            result = Result(
                success=level_up
            )
            statement = LearningExperience(
                actor=self.__actor,
                verb=verb,
                object=object,
                result=result,
                context=context,
                timestamp=True,
                version=self.__version
            )
        else:
            statement = LearningExperience(
                actor=self.__actor,
                verb=verb,
                object=object,
                context=context,
                timestamp=True,
                version=self.__version
            )

        self.clear_questions()

        return statement

    def question_answered(
            self,
            topic_id: int,
            question_id: int,
            question: str,
            response: str,
            raw_features: Optional[List[Tier]] = None
        ):
        verb = COMPLETED

        object = ActivityObject(
            object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}/topic{topic_id}/question{question_id}"),
            definition=ActivityDefinition(
                name=LanguageMap(languages="en-US", definitions="topic"),
                description=LanguageMap(languages="en-US", definitions=question),
                type=IRI("http://adlnet.gov/expapi/activities/cmi.interaction"),
                interaction_properties=OtherInteraction()
            ),
        )

        if raw_features is not None:
            extensions = Extensions(
                keys=IRI(f"{self.__config.IRI_BASE}/extension/raw_features"),
                values=[tier() for tier in raw_features]
            )

            result = Result(
                response=response,
                extensions=extensions
            )
        else:
            result = Result(
                response=response
            )

        context = Context(
            context_activities=ContextActivity(
                category=self.__category,
                parent=[
                    ActivityObject(
                        object_id=IRI(f"{self.__config.IRI_BASE}/activities/dialog/interview{self.__interview_id}/topic{topic_id}")
                    )
                ]
            ),
            extensions=Extensions(
                keys=IRI("http://id.tincanapi.com/extension/attempt-id"),
                values=self.__dialog_id
            )
        )

        statement = LearningExperience(
            actor=self.__actor,
            verb=verb,
            object=object,
            result=result,
            context=context,
            timestamp=True,
            version=self.__version
        )

        self.__questions.append(
            InteractionComponent(
                item_id=f"question{question_id}",
                description=LanguageMap(
                    languages="en-US",
                    definitions=question
                )
            )
        )

        return statement


if __name__ == "__main__":
    import uuid

    config = Config()

    generator = LANGXSpeakingLearningExperienceGenerator(
        learner_accout_name="SampleUser",
        dialog_id=uuid.uuid4(),
        interview_id="1"
    )

    start = generator.start()
    print(start())
    start.save_as_json(filepath=config.SAVE_PATH, filename_preffix="start")

    topic_start = generator.topic_start(1, "lunch", "A2")
    print(topic_start())
    topic_start.save_as_json(filepath=config.SAVE_PATH, filename_preffix="topic_start")

    tiers = [
        Tier(
            "pause", 
            [Interval("pause-1", 1.36, 1.4, "short")]
        ),
        Tier(
            "smile", 
            [Interval("smile-1", 1.36, 1.4, "laugh"), Interval("smile-1", 2.36, 2.52, "smile")]
        ),
    ]

    question_answered = generator.question_answered(
        1, 1, "Which do you like to eat for lunch: rice balls or sandwitchs?",
        response="I prefer rice ball.",
        raw_features=tiers
    )
    question_answered.save_as_json(filepath=config.SAVE_PATH, filename_preffix="question_answered")

    topic_complete = generator.topic_complete(1, "lunch", "A2")
    topic_complete.save_as_json(filepath=config.SAVE_PATH, filename_preffix="topic_complete")

    topic_complete_level_up = generator.topic_complete(1, "lunch", "A2", level_up=True)
    topic_complete_level_up.save_as_json(filepath=config.SAVE_PATH, filename_preffix="topic_complete_level_up")

    topic_complete_level_down = generator.topic_complete(1, "lunch", "A2", level_up=False)
    topic_complete_level_down.save_as_json(filepath=config.SAVE_PATH, filename_preffix="topic_complete_level_down")

    overall_score = generate_cefr_score(
        "overall", 2, 2.5, config.RESOURCE_PATH, "fluency", "interaction"
    )
    
    range_score = generate_cefr_score(
        "range", 2, 2.5, config.RESOURCE_PATH
    )

    accuracy_score = generate_cefr_score(
        "accuracy", 2, 2.5, config.RESOURCE_PATH
    )

    phonology_score = generate_cefr_score(
        "phonology", 2, 2.5, config.RESOURCE_PATH
    )

    fluency_score = generate_cefr_score(
        "fluency", 2, 2.5, config.RESOURCE_PATH
    )

    coherence_score = generate_cefr_score(
        "coherence", 2, 2.5, config.RESOURCE_PATH
    )

    interaction_score = generate_cefr_score(
        "interaction", 2, 2.5, config.RESOURCE_PATH
    )

    feedback = load_feedback(2, config.RESOURCE_PATH)

    complete = generator.complete(
        overall_score, range_score, accuracy_score, phonology_score,
        fluency_score, coherence_score, interaction_score, feedback
    )
    complete.save_as_json(filepath=config.SAVE_PATH, filename_preffix="complete")