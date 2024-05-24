# coding: utf-8
from enum import Enum

"""
スタティックコード記述モジュール
"""
PASSWORD_FLAG_ON = 1
PASSWORD_FLAG_OFF = 0

# LDAPコード集
LDAP_SUCCESS = 0
LDAP_OPERATIONS_ERROR = 1
LDAP_PROTOCOL_ERROR = 2
LDAP_TIMELIMIT_EXCEEDED = 3
LDAP_SIZELIMIT_EXCEEDED = 4
LDAP_COMPARE_FALSE = 5
LDAP_COMPARE_TRUE = 6
LDAP_STRONG_AUTH_NOT_SUPPORTED = 7
LDAP_STRONG_AUTH_REQUIRED = 8
LDAP_PARTIAL_RESULTS = 9
LDAP_REFERRAL = 10
LDAP_ADMINLIMIT_EXCEEDED = 11
LDAP_UNAVAILABLE_CRITICAL_EXTENSION = 12
LDAP_CONFIDENTIALITY_REQUIRED = 13
LDAP_SASL_BIND_IN_PROGRESS = 14
LDAP_NO_SUCH_ATTRIBUTE = 16
LDAP_UNDEFINED_TYPE = 17
LDAP_INAPPROPRIATE_MATCHING = 18
LDAP_CONSTRAINT_VIOLATION = 19
LDAP_TYPE_OR_VALUE_EXISTS = 20
LDAP_INVALID_SYNTAX = 21
LDAP_NO_SUCH_OBJECT = 32
LDAP_ALIAS_PROBLEM = 33
LDAP_INVALID_DN_SYNTAX = 34
LDAP_IS_LEAF = 35
LDAP_ALIAS_DEREF_PROBLEM = 36
LDAP_INAPPROPRIATE_AUTH = 48
LDAP_INVALID_CREDENTIALS = 49
LDAP_INSUFFICIENT_ACCESS = 50
LDAP_BUSY = 51
LDAP_UNAVAILABLE = 52
LDAP_UNWILLING_TO_PERFORM = 53
LDAP_LOOP_DETECT = 54
LDAP_NAMING_VIOLATION = 64
LDAP_OBJECT_CLASS_VIOLATION = 65
LDAP_NOT_ALLOWED_ON_NONLEAF = 66
LDAP_NOT_ALLOWED_ON_RDN = 67
LDAP_ALREADY_EXISTS = 68
LDAP_NO_OBJECT_CLASS_MODS = 69
LDAP_RESULTS_TOO_LARGE = 70
LDAP_AFFECTS_MULTIPLE_DSAS = 71
LDAP_OTHER = 80
LDAP_SERVER_DOWN = 81
LDAP_LOCAL_ERROR = 82
LDAP_ENCODING_ERROR = 83
LDAP_DECODING_ERROR = 84
LDAP_TIMEOUT = 85
LDAP_AUTH_UNKNOWN = 86
LDAP_FILTER_ERROR = 87
LDAP_USER_CANCELLED = 88
LDAP_PARAM_ERROR = 89
LDAP_NO_MEMORY = 90
LDAP_CONNECT_ERROR = 91
LDAP_NOT_SUPPORTED = 92
LDAP_CONTROL_NOT_FOUND = 93
LDAP_NO_RESULTS_RETURNED = 94
LDAP_MORE_RESULTS_TO_RETURN = 95
LDAP_CLIENT_LOOP = 96
LDAP_REFERRAL_LIMIT_EXCEEDED = 97


# LDAPの検索タイプ（タイプ別に取得属性値を制御するため）
class LDAP_SEARCH_TYPE(Enum):
    OPEADMIN_LIST = 1
    UNIQUE_CHECK = 2
    TEACHER_LIST = 3
    STUDENT_LIST = 4
    USER_LIST = 5
    USER_ALL_LIST = 6
    STUDENT_LIST_DELETE = 7
    TEACHER_LIST_DELETE = 8
    WINDOWS_RELATION_LIST = 9
	# 　新規追加（案件８．OPE管理者の削除）　START
    OPEADMIN_LIST_DELETE = 10
	# 　新規追加（案件８．OPE管理者の削除）　END


# 　改修（DB構成変更対応）　START
# 　改修（マルチテナント化対応）　START
# RDSのテーブル一覧
# .valueで情報を取得することができます
class RDS_TABLE(Enum):
    # 　改修（DB構成変更対応）　END
    # DB操作受付情報テーブル
    APPLY_INFO = {
        "table_name": "t_apply_info",
        "primary_key": ["message_id"],
        "default_order": "entry_date_time ASC",
    }
    # DB操作受付情報テーブル
    APPLY_INFO_WITH_SCHOOL = {
        "table_name": "t_apply_info LEFT OUTER JOIN t_school_master ON"
                      " t_apply_info.target_system_organization_code=t_school_master.system_organization_code AND "
                      " t_apply_info.target_organization_code=t_school_master.school_code",
        "primary_key": ["message_id"],
        "default_order": "t_apply_info.entry_date_time ASC",
    }
    # DB操作受付情報テーブル
    APPLY_INFO_NEW = {
        "table_name": "t_apply_info",
        "primary_key": ["message_id"],
        "default_order": "update_date_time DESC LIMIT 1",
    }
    # 組織マスタテーブル
    ORGANIZATION_MASTER = {
        "table_name": "t_organization_master",
        "primary_key": ["system_organization_code"],
        "default_order": "show_no ASC, system_organization_code ASC",
    }
    # 学校マスタテーブル
    SCHOOL_MASTER = {
        "table_name": "t_school_master",
        "primary_key": ["system_organization_code", "school_code"],
        "default_order": "show_no ASC, school_code ASC",
    }
    #  新規追加(マルチテナント化対応) START
    # 学校マスタテーブル+組織マスタテーブル
    SCHOOL_MASTER_WITH_ORGANIZATION = {
        "table_name": "t_school_master INNER JOIN t_organization_master ON "
                      "t_school_master.system_organization_code=t_organization_master.system_organization_code",
        "primary_key": ["system_organization_code", "school_code"],
        "default_order": "t_school_master.show_no ASC, t_school_master.school_code ASC",
    }
    # 環境情報テーブル
    ENVIRONMENT = {
        "table_name": "t_environment",
        "primary_key": ["system_organization_code", "application_id", "environment_name"],
        "default_order": "system_organization_code ASC, application_id ASC, environment_name ASC",
    }
    #  新規追加(マルチテナント化対応) END
    # 　新規追加（文科省標準の学校コード追加）　START
    # 学校マスタテーブル
    SCHOOL_MASTER_MEXTOUCODE = {
        "table_name": "t_school_master",
        "primary_key": ["system_organization_code", "school_code"],
        "default_order": "mextOuCode DESC LIMIT 1",
    }
    # 　新規追加（文科省標準の学校コード追加）　END
    # 学年マスタテーブル
    GRADE_MASTER = {
        "table_name": "t_grade_master",
        "primary_key": ["system_organization_code", "school_code", "grade_code"],
        "default_order": "system_organization_code ASC, school_code ASC, show_no ASC, grade_code ASC",
    }
    # 学年マスタテーブル+学校マスタテーブル
    GRADE_MASTER_WITH_SCHOOL = {
        "table_name": "t_grade_master LEFT OUTER JOIN t_school_master"
                      " ON t_grade_master.system_organization_code=t_school_master.system_organization_code AND "
                      " t_grade_master.school_code=t_school_master.school_code",
        "primary_key": ["system_organization_code", "school_code", "grade_code"],
        "default_order": " t_grade_master.system_organization_code ASC, "
                         " t_grade_master.school_code ASC,"
                         " t_grade_master.show_no ASC,"
                         " t_grade_master.grade_code ASC",
    }
    #  新規追加(マルチテナント化対応) START
    # 学年マスタテーブル+組織マスタテーブル
    GRADE_MASTER_WITH_ORGANIZATION = {
        "table_name": "t_grade_master INNER JOIN t_organization_master ON "
                      "t_grade_master.system_organization_code=t_organization_master.system_organization_code",
        "primary_key": ["system_organization_code", "school_code", "grade_code"],
        "default_order": "t_grade_master.system_organization_code ASC, t_grade_master.school_code ASC,"
                         " t_grade_master.show_no ASC, t_grade_master.grade_code ASC",
    }
    #  新規追加(マルチテナント化対応) END
    # 組マスタテーブル
    CLASS_MASTER = {
        "table_name": "t_class_master",
        "primary_key": ["system_organization_code", "school_code", "class_code"],
        "default_order": "system_organization_code ASC, school_code ASC, show_no ASC, class_code ASC",
    }
    # 組マスタテーブル+学校マスタテーブル
    CLASS_MASTER_WITH_SCHOOL = {
        "table_name": "t_class_master LEFT OUTER JOIN t_school_master "
                      "ON t_class_master.system_organization_code=t_school_master.system_organization_code AND "
                      " t_class_master.school_code=t_school_master.school_code",
        "primary_key": ["system_organization_code", "school_code", "class_code"],
        "default_order": " t_class_master.system_organization_code ASC, "
                         " t_class_master.school_code ASC,"
                         " t_class_master.show_no ASC,"
                         " t_class_master.class_code ASC",
    }
    #  新規追加(マルチテナント化対応) START
    # 組マスタテーブル+組織マスタテーブル
    CLASS_MASTER_WITH_ORGANIZATION = {
        "table_name": "t_class_master INNER JOIN t_organization_master "
                      "ON t_class_master.system_organization_code=t_organization_master.system_organization_code",
        "primary_key": ["system_organization_code", "school_code", "class_code"],
        "default_order": " t_class_master.system_organization_code ASC, "
                         " t_class_master.school_code ASC,"
                         " t_class_master.show_no ASC,"
                         " t_class_master.class_code ASC",
    }
    #  新規追加(マルチテナント化対応) END
    # 組織タイプマスタテーブル
    ORGANIZATION_TYPE_MASTER = {
        "table_name": "t_organization_type_master",
        "primary_key": ["organization_type_code"],
        "default_order": "organization_type_code ASC",
    }
    # 職位マスタテーブル
    PERSON_AFFILIATION_MASTER = {
        "table_name": "t_person_affiliation_master",
        "primary_key": ["person_affiliation_code"],
        "default_order": None,
    }
    # 職階マスタテーブル
    TITLE_MASTER = {
        "table_name": "t_title_master",
        "primary_key": ["title_code"],
        "default_order": "show_no ASC, title_code ASC",
    }
    # 兼務マスタテーブル
    ADDITIONAL_POST_MASTER = {
        "table_name": "t_additional_post_master",
        "primary_key": ["additional_post_code"],
        "default_order": "show_no ASC, additional_post_code ASC",
    }
    # 教科マスタテーブル
    SUBJECT_MASTER = {
        "table_name": "t_subject_master",
        "primary_key": ["system_organization_code", "school_code", "subject_code"],
        "default_order": "system_organization_code ASC, school_code ASC, show_no ASC, subject_code ASC",
    }
    # 教科マスタテーブル+学校マスタテーブル
    SUBJECT_MASTER_WITH_SCHOOL = {
        "table_name": "t_subject_master LEFT OUTER JOIN t_school_master "
                      "ON t_subject_master.system_organization_code=t_school_master.system_organization_code AND "
                      " t_subject_master.school_code=t_school_master.school_code",
        "primary_key": ["system_organization_code", "school_code", "subject_code"],
        "default_order": " t_subject_master.system_organization_code ASC, "
                         " t_subject_master.school_code ASC,"
                         " t_subject_master.show_no ASC,"
                         " t_subject_master.subject_code ASC",
    }
    #  新規追加(マルチテナント化対応) START
    # 教科マスタテーブル+組織マスタテーブル
    SUBJECT_MASTER_WITH_ORGANIZATION = {
        "table_name": "t_subject_master INNER JOIN t_organization_master "
                      "ON t_subject_master.system_organization_code=t_organization_master.system_organization_code ",
        "primary_key": ["system_organization_code", "school_code", "subject_code"],
        "default_order": " t_subject_master.system_organization_code ASC, "
                         " t_subject_master.school_code ASC,"
                         " t_subject_master.show_no ASC,"
                         " t_subject_master.subject_code ASC",
    }
    #  新規追加(マルチテナント化対応) END
    # ユーザ削除テーブル
    DELETE_USER = {
        "table_name": "t_delete_user",
        "primary_key": ["id"],
        "default_order": None,
    }
# 　改修（マルチテナント化対応）　END

# 　改修（DB構成変更対応）　START
# 　改修（マルチテナント化対応）　START
# RDSの検索タイプ（タイプ別に取得列を制御するため）
# 数字は重複しなければなんでも良い
class RDS_SEARCH_TYPE(Enum):
    # 　改修（DB構成変更対応）　END
    # 受付情報テーブルから1行取得する（内部での命令キュー操作用）
    APPLY_INFO_QUE_COMMAND = 1
    # 受付情報テーブルを取得する（履歴取得）
    APPLY_INFO_SEARCH = 2
    # 受付情報テーブルを取得する（下部組織名称取得付き）
    APPLY_INFO_SEARCH_WITH_NAME = 3
    # 学校マスタ情報を取得する（画面用）
    SCHOOL_GET_MASTERS = 4
    # 学年マスタ情報を取得する（画面用）
    GRADE_GET_MASTERS = 5
    # 組マスタ情報を取得する（画面用）
    CLASS_GET_MASTERS = 6
    # 組織タイプマスタ情報を取得する（画面用）
    ORGANIZATION_TYPE_GET_MASTERS = 7
    # 職位マスタ情報を取得する（画面用）
    PERSON_AFFILIATION_GET_MASTERS = 8
    # 職階マスタ情報を取得する（画面用）
    TITLE_GET_MASTERS = 9
    # 兼務マスタ情報を取得する（画面用）
    ADDITIONAL_POST_GET_MASTERS = 10
    # 教科マスタ情報を取得する（画面用）
    SUBJECT_GET_MASTERS = 11
    # 学年マスタ情報を取得する
    GRADE_LIST_MASTERS = 12
    # 学校マスタ情報を取得する
    SCHOOL_LIST_MASTERS = 13
    # 学年マスタ情報を取得する(学校マスタ結合)
    GRADE_LIST_MASTERS_WITH_SCHOOL = 14
    # 組マスタ情報を取得する(学校マスタ結合)
    CLASS_LIST_MASTERS_WITH_SCHOOL = 15
    # 教科マスタ情報を取得する(学校マスタ結合)
    SUBJECT_LIST_MASTERS_WITH_SCHOOL = 16
    # 組マスタ情報を取得する
    CLASS_LIST_MASTERS = 17
    # 教科マスタ情報を取得する
    SUBJECT_LIST_MASTERS = 18
    # 削除ユーザ情報を取得する
    DELETE_USER_LIST = 19
    # 削除ユーザ情報を取得する(バッチ用)
    DELETE_USER_LIST_BATCH = 20
    # 教員削除ユーザ情報を取得する
    DELETE_TEACHER_USER_LIST = 21
    # 削除ユーザ情報を取得する(バッチ用)
    DELETE_USER_LIST_BATCH_WINDOWS = 22
    # 環境情報を取得する
    ENVIRONMENT_SEARCH = 23
    # 組織情報を取得する
    ORGANIZATION_SEARCH = 24
    #  新規追加(マルチテナント化対応) START
    # 学校マスタ情報を取得する(組織マスタ結合)
    SCHOOL_LIST_MASTERS_WITH_ORGANIZATION = 25
    # 学年マスタ情報を取得する(組織マスタ結合)
    GRADE_LIST_MASTERS_WITH_ORGANIZATION = 26
    # 組マスタ情報を取得する(組織マスタ結合)
    CLASS_LIST_MASTERS_WITH_ORGANIZATION = 27
    # 教科マスタ情報を取得する(組織マスタ結合)
    SUBJECT_LIST_MASTERS_WITH_ORGANIZATION = 28
    #  新規追加(マルチテナント化対応) END


# RDSのアプリケーションID
class APPLICATION_ID(Enum):
    Common = "common"
    OpeidLambdaBatchExportUserHistory = "OpeidLambdaBatchExportUserHistory"
    # OpeidLambdaBatchExportUserHistory2 = "OpeidLambdaBatchExportUserHistory2"
    OpeidLambdaBatchExportMasterInfo = "OpeidLambdaBatchExportMasterInfo"
    # OpeidLambdaBatchExportMasterInfo2 = "OpeidLambdaBatchExportMasterInfo2"


# RDSの環境変数名
class ENVIRONMENT_NAME(Enum):
    GOOGLE_COOPERATION_FLAG = "GOOGLE_COOPERATION_FLAG"
    GSUITE_DOMAIN = "GSUITE_DOMAIN"
    WINDOWS_COOPERATION_FLAG = "WINDOWS_COOPERATION_FLAG"
    AZUREAD_DOMAIN = "AZUREAD_DOMAIN"
    IDP_ENTITYID = "IDP_ENTITYID"
    AZUREAD_SECRET_ARN = "AZUREAD_SECRET_ARN"
    ORGANIZATIONS_NAME = "ORGANIZATIONS_NAME"
    # ORGANIZATIONS_NAME_2 = "ORGANIZATIONS_NAME_2"
    # ORGANIZATIONS_NAME_FILE_PATH = "ORGANIZATIONS_NAME_FILE_PATH"
    USER_POOL_NAME = "USER_POOL_NAME"
    QUEUE_URL = "QUEUE_URL"
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    USER_DELETE_DAYS = "USER_DELETE_DAYS"
    ONEROSTER_API_HOST = "ONEROSTER_API_HOST"
	# ↑ここまで
# 　改修（マルチテナント化対応）　END
