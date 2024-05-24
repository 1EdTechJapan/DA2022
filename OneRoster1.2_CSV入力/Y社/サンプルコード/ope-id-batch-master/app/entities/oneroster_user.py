# coding: utf-8
from dataclasses import dataclass
from app.entities.user_dn import UserDn

@dataclass
class Oneroster_user(UserDn):
    """
    LDAP対応エンティティ
    """
    user_id: str = None
    opaque_id: str = None
    persistent_uid: str = None
    organization_name: str = None
    organization_name_ja: str = None
    organization_code: str = None
    organization_type: str = None
    given_name: str = None
    given_name_kana: str = None
    sur_name: str = None
    sur_name_kana: str = None
    gender: str = None
    fiscal_year: int = None
    person_affiliation_code: str = None
    role: str = None
    system_organization_type: str = ""
    system_organization_name: str = ""
    system_organization_name_ja: str = ""
    system_organization_code: str = ""
    title_code: list = None
    additional_post_code: list = None
    subject_code: list = None
    grade_code: str = None
    grade_name: str = None
    class_code: str = None
    class_name: str = None
    student_number: str = None
    mail: str = None
    relationgg: int = 0
    relationwin: int = 0
    reg_date: str = None
    from_organization_code: str = None
    transfer_school_date: str = None
    mextUid: str = None
    mextOuCode: str = None
    entry_person: str = None
    # DBではTimestamp型
    entry_date_time: str = None
    update_person: str = None
    # DBではTimestamp型
    update_date_time: str = None
    # DBではbool型
    delete_flag: str = None

