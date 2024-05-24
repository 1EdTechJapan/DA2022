# LANGX xAPI statement generator
---

## 1. Overall
### 1.1 xapi_statement_generator
- ``property``: codes of xAPI statement property
- ``resources``: store data or setting files to execute program
- ``config.py``: program setting
- ``learning_experinece.py``: learning experience statement template
- ``learning_experience_generator.py``: statement generator for LANGX Speaking

## 2. System requirements

- Python version
```
Python v3.9.6
```

- Modules
```
language-tags==1.2.0
pandas==1.4.3
```

## 3. Project setup

1. Set "*config.py*"
2. Put ``cefr_result_description.json`` to "*xapi_statement_generator/resources*"
3. Import LANGXSpeakingLearningExperienceGenerator from "*learning_experiece_generator.py*" <br><br>
    ```python
    from learning_experience_generator import LANGXSpeakingLearningExperienceGenerator

    generator = LANGXSpeakingLearningExperienceGenerator(
        learner_accout_name, # learner's account name (str)
        dialog_id, # unique id for each dialog (uuid)
        interview_id # unique id for each interview scenario (str)
    )
    ```
4. Generate learning experiment object for each activity<br><br>
    - interview start
        ```Python
        interview_start = generator.start()
        ```

    - interview complete
        ```Python
        interview_complete = generator.complete(
            overall_score, # CEFR overall score (CefrScore)
            range_score, # CEFR range score (CefrScore)
            accuracy_score, # CEFR accuracy score (CefrScore)
            phonology_score, # CEFR phonology score (CefrScore)
            fluency_score, # CEFR fluency score (CefrScore)
            coherence_score, # CEFR coherence score (CefrScore)
            interaction_score, # CEFR interaction score (CefrScore)
            feedback # feedback (str)
        )
        ```
    
    - topic_start
        ```Python
        topic_start = generator.topic_start(
            topic_id, # unique id for each topic of the current interview (int)
            topic_name, # topic name (str)
            topic_difficulty # topic difficulty (int | str | Cefr)
        )
        ```

    - topic_complete / topic_complete_level_up / topic_complete_level_down
        ```Python
        topic_complete = generator.topic_complete(
            topic_id,
            topic_name,
            topic_difficulty
        )

        topic_complete_level_up = generator.topic_complete(
            topic_id,
            topic_name,
            topic_difficulty,
            level_up=True # True if next topic difficulty is increased
        )

        topic_complete_level_up = generator.topic_complete(
            topic_id,
            topic_name,
            topic_difficulty,
            level_up=False # True if next topic difficulty is decreased
        )
        ```

    - question_answered
        ```Python
        question_answered = generator.question_answered(
            topic_id,
            question_id, # unique id for each question of the current topic (int)
            question, # dialog system's question (str)
            response, # learner's response (str)
            raw_features # automatically annotated raw features if exist (List[Tier])
        )
        ```
