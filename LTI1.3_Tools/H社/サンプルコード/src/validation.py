from typing import List
from uuid import UUID
from pylti1p3.exception import LtiException

SYSTEM_ROLE_URI = "http://purl.imsglobal.org/vocab/lis/v2/system/person"
INSTITUTION_ROLE_URI = "http://purl.imsglobal.org/vocab/lis/v2/institution/person"
CONTEXT_ROLE_URI = "http://purl.imsglobal.org/vocab/lis/v2/membership"

VALID_SYSTEM_ROLE = [
    "Administrator",
    "None",
    "AccountAdmin",
    "Creator",
    "SysAdmin",
    "SysSupport",
    "User",
]

VALID_INSTITUTION_ROLE = [
    "Administrator",
    "Faculty",
    "Guest",
    "None",
    "Other",
    "Staff",
    "Student",
    "Alumni",
    "Instructor",
    "Learner",
    "Member",
    "Mentor",
    "Observer",
    "ProspectiveStudent"
]

VALID_CONTEXT_ROLE = [
    "Administrator",
    "ContentDeveloper",
    "Instructor",
    "Learner",
    "Mentor",
    "Manager",
    "Member",
    "Officer"
]

VALID_GRADE_CODE = [
    "P1", "P2", "P3", 
    "P4", "P5", "P6",
    "J1", "J2", "J3",
    "H1", "H2", "H3",
    "E1", "E2", "E3"
]

def is_valid_uuid4(uuid: str) -> bool:
        try:
            val = UUID(uuid, version=4)
        except: # valud is invalid uuid format
            return False

        return str(val) == uuid

def validate_sub(sub: str) -> None:
    if is_valid_uuid4(sub):
        return

    if sub is None:
        print(f"Anonymous user")
        return
    
    raise LtiException("Invalid uuid4")

def validate_role(roles: List[str]) -> None:
    if len(roles) == 0:
        raise LtiException("\"roles\" is empty")
    
    for role in roles:
        uri, role = role.split("#")

        if uri == SYSTEM_ROLE_URI:
            if role in VALID_SYSTEM_ROLE:
                continue
        elif uri == INSTITUTION_ROLE_URI:
            if role in VALID_INSTITUTION_ROLE:
                continue
        elif uri == CONTEXT_ROLE_URI:
            if role in VALID_CONTEXT_ROLE:
                continue

        raise LtiException("Invalid role")
    
def validate_context(context: dict) -> None:
    if context["id"] == "":
        raise LtiException("\"context id\" is empty")

def validate_target_link_uri(target_link_uri: str) -> None:
    if target_link_uri == "":
        raise LtiException("\"target_link_uri\" is empty")

def validate_tool_platform(tool_platform: dict) -> None:
    if "guid" not in tool_platform:
        raise LtiException("\"guid\" is empty")
    
    guid = tool_platform["guid"]

    if guid is None:
        raise LtiException("\"guid\" is empty")
    
    if is_valid_uuid4(guid):
        return
    
    raise LtiException("Invalid uuid4")

def validate_grade(grade: str) -> None:
    if grade not in VALID_GRADE_CODE:
        raise LtiException("Invalid grade")

def validate_custom(custom: dict) -> None:
    if "grade" in custom:
        validate_grade(custom["grade"])
    

def validate_token_id(token_id: dict) -> None:
    # validate sub
    validate_sub(token_id["sub"])

    # validate role
    validate_role(token_id["https://purl.imsglobal.org/spec/lti/claim/roles"])

    # validate context
    validate_context(token_id["https://purl.imsglobal.org/spec/lti/claim/context"])
    
    # validate target link uri
    validate_target_link_uri(token_id["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"])

    # validate tool_platform if it exists
    if "https://purl.imsglobal.org/spec/lti/claim/tool_platform" in token_id:
        validate_tool_platform(token_id["https://purl.imsglobal.org/spec/lti/claim/tool_platform"])

    # validate custom if it exists
    if "https://purl.imsglobal.org/spec/lti/claim/custom" in token_id:
        validate_custom(token_id["https://purl.imsglobal.org/spec/lti/claim/custom"])