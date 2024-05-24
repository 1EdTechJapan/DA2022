# coding: utf-8
from dataclasses import dataclass

from app.entities.user_dn import UserDn


@dataclass
class User(UserDn):
    """
    LDAP対応エンティティ（OpeadminやTeacherはこのエンティティを継承したものを使用）
    """
    # pythonでは型の制御が困難（strで宣言しても、intも入る）なので、下記は期待する型。
    sur_name_en: str = None
    sur_name: str = None
    sur_name_kana: str = None
    # LDAPで必須となっているが、使用されない属性
    cn: str = None
    given_name_en: str = None
    given_name: str = None
    given_name_kana: str = None
    # LDAPで必須となっているが、使用されない属性
    jasn: str = None
    display_name_en: str = None
    display_name: str = None
    password: str = None
    user_password: str = None
    password_flg: int = None
    opaque_id: str = None
    persistent_uid: str = None
    mail: str = None
    person_affiliation_code: str = None
    role: str = None
    title_code: list = None
    upd_date: str = None
    # opaque_id生成用、LDAPには登録されない
    year: str = None
    enable_flag: int = None
    fiscal_year: int = None
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    grade_code: str = None
    relationgg: int = 0
    relationwin: int = 0
    additional_post_code: list = None
    # DBではbool型
    delete_flag: str = None
    subject_code: list = None
    class_code: str = None
    gender: str = None
    student_number: str = None
    mextUid: str = None
	# ↑ここまで
