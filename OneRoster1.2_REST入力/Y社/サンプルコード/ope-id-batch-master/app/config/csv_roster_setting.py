# coding: utf-8
"""
CSV
"""
# CSVの列情報
column = {
    "users_temp": [
    ]
}
# ↓OneRoster Rest Api連携時には以下は必須です
# CSVのヘッダ情報
header = {
    "academicSessions": [
        "sourcedId",
        "status",
        "dateLastModified",
        "title",
        "type",
        "startDate",
        "endDate",
        "parentSourcedId",
        "schoolYear"
    ],
    "classes": [
        "sourcedId",
        "status",
        "dateLastModified",
        "title",
        "grades",
        "courseSourcedId",
        "classCode",
        "classType",
        "location",
        "schoolSourcedId",
        "termSourcedIds",
        "subjects",
        "subjectCodes",
        "periods",
        "metadata.jp.specialNeeds"
    ],
    "demographics": [
        "sourcedId",
        "status",
        "dateLastModified",
        "birthDate",
        "sex",
        "americanIndianOrAlaskaNative",
        "asian",
        "blackOrAfricanAmerican",
        "nativeHawaiianOrOtherPacificIslander",
        "white",
        "demographicRaceTwoOrMoreRaces",
        "hispanicOrLatinoEthnicity",
        "countryOfBirthCode",
        "stateOfBirthAbbreviation",
        "cityOfBirth",
        "publicSchoolResidenceStatus"
    ],
    "enrollments": [
        "sourcedId",
        "status",
        "dateLastModified",
        "classSourcedId",
        "schoolSourcedId",
        "userSourcedId",
        "role",
        "primary",
        "beginDate",
        "endDate",
        "metadata.jp.ShussekiNo",
        "metadata.jp.PublicFlg"
    ],
    "orgs": [
        "sourcedId",
        "status",
        "dateLastModified",
        "name",
        "type",
        "identifier",
        "parentSourcedId"
    ],
    "users": [
        "sourcedId",
        "status",
        "dateLastModified",
        "enabledUser",
        "username",
        "userIds",
        "givenName",
        "familyName",
        "middleName",
        "identifier",
        "email",
        "sms",
        "phone",
        "agentSourcedIds",
        "grades",
        "password",
        "userMasterIdentifier",
        "resourceSourcedIds",
        "preferredGivenName",
        "preferredMiddleName",
        "preferredFamilyName",
        "primaryOrgSourcedId",
        "pronouns",
        "metadata.jp.kanaGivenName",
        "metadata.jp.kanaFamilyName",
        "metadata.jp.kanaMiddleName",
        "metadata.jp.homeClass"
    ],
    "roles": [
        "sourcedId",
        "status",
        "dateLastModified",
        "userSourcedId",
        "roleType",
        "role",
        "beginDate",
        "endDate",
        "orgSourcedId",
        "userProfileSourcedId"
    ],
    "manifest": [
        "propertyName",
        "value"
    ]
}
# ↑ここまで

TEMP_FILE_COLUMN = [
    "sourcedId",
    "status",
    "givenName",
    "familyName",
    "email",
    "grades",
    "password",
    "username",
    "userMasterIdentifier",
    "kanaGivenName",
    "kanaFamilyName",
    "schoolCode",
    "schoolYear",
    "role",
    "shussekiNo",
    "classCode",
    "subjectCodes",
    "sex"
]

ERROR_FILE_COLUMN = [
    "userMasterIdentifier",
    "detail"
]

# ↓OneRoster Rest Api連携時には以下は必須です
# manifest
CSV_FILE_NAME_MANIFEST = "manifest.csv"
# academicSessions
CSV_FILE_NAME_ACADEMIC_SESSIONS = "academicSessions.csv"
# Demographics
CSV_FILE_NAME_DEMOGRAPHICS = "demographics.csv"
# Enrollments
CSV_FILE_NAME_ENROLLMENTS = "enrollments.csv"
# Classes
CSV_FILE_NAME_CLASSES = "classes.csv"
# Orgs
CSV_FILE_NAME_ORGS = "orgs.csv"
# Roles
CSV_FILE_NAME_ROLES = "roles.csv"
# Users
CSV_FILE_NAME_USERS = "users.csv"
# ↑ここまで

user_search = [
    "persistent_uid",
    "user_id",
    "grade_code",
    "organization_code",
    "relationgg",
    "relationwin",
    "upd_date",
    "title_code",
    "additional_post_code",
    "organization_name",
    "sur_name_kana",
    "given_name_kana",
    "subject_code",
    "class_code",
    "gender",
    "mail",
    "student_number",
    "mextUid"
]

ldap_search = [
    "user_id",
    "opaque_id",
    "persistent_uid",
    "organization_name",
    "organization_name_ja",
    "organization_code",
    "organization_type",
    "given_name",
    "given_name_kana",
    "sur_name",
    "sur_name_kana",
    "gender",
    "fiscal_year",
    "person_affiliation_code",
    "role",
    "system_organization_type",
    "system_organization_name",
    "system_organization_name_ja",
    "system_organization_code",
    "title_code",
    "additional_post_code",
    "subject_code",
    "grade_code",
    "grade_name",
    "class_code",
    "class_name",
    "student_number",
    "mail",
    "relationgg",
    "relationwin",
    "reg_date",
    "from_organization_code",
    "transfer_school_date",
    "mextUid",
    "mextOuCode",
]