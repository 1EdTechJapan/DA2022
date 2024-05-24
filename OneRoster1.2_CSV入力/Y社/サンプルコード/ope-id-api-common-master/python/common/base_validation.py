# coding: utf-8
"""
Cerberusバリデーション設定集
"""
user_id_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 256,
    # 制御コード、エスケープ記号以外のADCII文字
    # TODO:仕様決まり次第変更
    "regex": "^[!-\[\]-~]+$",
}
# 児童生徒の結合コード形式
student_id_insert_update = {**user_id_insert_update, "maxlength": 384}
user_id_select = {**user_id_insert_update, "required": False, "empty": True}
student_id_select = {**user_id_insert_update, "required": False, "empty": True, "maxlength": 384}
opaque_id_select = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64,
    "minlength": 64,
}
persistent_uid_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 256,
    "regex": "^[a-zA-Z0-9]+$",
}
persistent_uid_select = {
    **persistent_uid_insert_update,
    "required": False,
    "empty": True,
    "maxlength": 257,
}
sur_name_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 10,
    # 半角英数とすべての全角文字(半角カナ含む)
    "regex": "^[\w＝ー、．：；？＃＋＊／]+$",
}
sur_name_kana_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "maxlength": 20,
    # ひらがな、全角スペース、伸ばし棒、中点のみ
    "regex": "^[\u3041-\u3096　ー・]+$",
}
sur_name_select = {**sur_name_insert_update, "required": False, "empty": True}
sur_name_kana_select = {
    **sur_name_kana_insert_update
}
given_name_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 10,
    # 半角英数とすべての全角文字(半角カナ含む)
    "regex": "^[\w＝ー、．：；？＃＋＊／]+$",
}
given_name_kana_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "maxlength": 20,
    # ひらがな、全角スペース、伸ばし棒、中点のみ
    "regex": "^[\u3041-\u3096　ー・]+$",
}
given_name_select = {
    **given_name_insert_update,
    "required": False,
    "empty": True,
}
given_name_kana_select = {
    **given_name_kana_insert_update,
}
gender_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "allowed": ["", "1", "2"],
}
person_affiliation_code_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": [
        "admin",
        "operator",
        "teacher",
        "student",
        "parent",
        "company",
    ],
}
person_affiliation_code_select = {
    **person_affiliation_code_insert_update,
    "required": False,
    "empty": True,
}
person_affiliation_code_select_scim = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": ["teacher", "student", "admin", "all", "operator", "company"],
}
role_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": [
        "admin",
        "operator",
        "teacher",
        "student",
        "parent",
        "company",
    ],
}
role_teacher_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": ["operator", "teacher"],
}
role_company_teacher_insert_update = {
    **role_insert_update,
    "allowed": ["company"],
}
# 　新規追加 START
role_admin_teacher_insert_update = {
    **role_insert_update,
    "allowed": ["admin", "operator", "teacher"],
}
# 　新規追加 END
title_code_set = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]
title_code_opeadmin_insert_update = {
    "type": "list",
    "required": True,
    "empty": True,
    "schema": {"type": "string", "allowed": ["0", ""]},
}
title_code_insert_update = {
    "type": "list",
    "required": True,
    "empty": False,
    "schema": {"type": "string", "allowed": title_code_set},
}
title_code_insert_update_list = {**title_code_insert_update, "empty": True}
title_code_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "allowed": title_code_set,
}
title_code_select_list = {
    "type": "list",
    "required": False,
    "empty": True,
    "schema": {
        "required": False,
        "empty": True,
        "type": "string",
        "allowed": title_code_set,
    },
}
mail_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 256,
    "regex": "^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
}
mail_opeadmin_insert_update = {**mail_insert_update, "empty": False}
mail_select = {
    **mail_insert_update,
    "required": False,
    "regex": "^[a-zA-Z0-9_.\-@]+$",
}
password_flg_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [0, 1],
}
password_flg_password_update = {**password_flg_insert_update}
organization_name_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64,
    # 制御コード、エスケープ記号以外のADCII文字
    # TODO:仕様決まり次第変更
    "regex": "^[!-\[\]-~]+$",
}
organization_name_insert_update_allow_empty = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 64,
    # 制御コード、エスケープ記号以外のADCII文字
    # TODO:仕様決まり次第変更
    "regex": "^[!-\[\]-~]+$",
}
organization_name_select = {**organization_name_insert_update}
organization_name_ja_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
organization_name_ja_select = {
    **organization_name_ja_insert_update,
    "required": False,
    "empty": True,
}
# 　新規追加（マルチテナント化対応）　START
host = {
    "type": "string",
    "required": True,
    "empty": False,
}
system_organization_code = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 13,
    "regex": "^[a-zA-Z0-9]+$",
}
system_organization_name = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64
}
# 企業モードの学校タイプ
school_type_insert_update_kg = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [98],
}
# 　新規追加（マルチテナント化対応）　END
organization_type_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [1, 2, 3, 4, 5, 6, 7, 8, 9, 98, 99],
}
school_type_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [2, 3, 4, 5, 6, 7, 8],
}
organization_type_select = {
    **organization_type_insert_update,
    "required": False,
    "empty": True,
}
organization_code_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 16,
    "regex": "^[a-zA-Z0-9]+$",
}
organization_code_select = {
    **organization_code_insert_update,
    "required": False,
    "empty": True,
}
user_password_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "minlength": 4,
    "maxlength": 16,
    "regex": "^[0-9a-zA-Z!#$%&()]+$",
}
user_password_insert_update_allow_required = {
    **user_password_insert_update,
    "required": False,
    "empty": True,
}
user_password_win_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "minlength": 8,
    "maxlength": 16,
    "regex": "^[0-9a-zA-Z!#$%&()]+$",
}
user_password_win_insert_update_allow_required = {
    **user_password_win_insert_update,
    "required": False,
    "empty": True,
}
# 　新規追加（文科省標準の学校コード追加）　START
mextOuCode_prefix_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "allowed": ["S", "B", "P"],
}
mextOuCode_code_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "regex": "^[a-zA-Z0-9]+$",
}
mextOuCode_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "regex": "^[SBP]{1}_[0-9a-zA-Z]+$",
}
mextOuCode_select = {
    **mextOuCode_insert_update,
}
# 　新規追加（文科省標準の学校コード追加）　END
queryString = {"allowed": ["None"]}
limit = {"type": "integer", "required": True, "empty": True, "min": 1}
limit_with_all = {"type": "integer", "required": True, "empty": True, "min": 0}
startIndex = {"type": "integer", "required": False, "empty": True, "min": 1}
count = {"type": "integer", "required": False, "empty": True, "min": 1}
offset = {"type": "integer", "required": True, "empty": True, "min": 0}
offset_index = {"type": "integer", "required": False, "empty": True, "min": 1}
scope = {"type": "string", "required": False, "empty": True}
grade_code_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 2,
    "regex": "^[0-9a-zA-Z]+$",
}
grade_code_insert_update_not_empty = {
    **grade_code_insert_update,
    "empty": False,
}
grade_code_insert_update_required = {
    **grade_code_insert_update,
    "required": True,
    "empty": False,
}
grade_code_select = {**grade_code_insert_update, "required": False}
grade_name_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
grade_name_insert_update_not_empty = {
    **grade_name_insert_update,
    "empty": False,
}
grade_name_select = {**grade_name_insert_update, "required": False}
grade_name_ja_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
class_code_insert_update = {
    "type": "integer",
    # 任意項目のため設定しない場合考慮
    "required": False,
    "empty": False,
    "min": 0,
    "max": 999,
}
class_code_select = {**class_code_insert_update}
class_code_insert_update_required = {
    **class_code_insert_update,
    "required": True,
}
class_name_insert_update = {
    "type": "string",
    "required": False,
    "empty": True,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
class_name_select = {**class_name_insert_update}
class_name_ja_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
class_type_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [1, 2, 3],
}
class_type_select = {
    **class_type_insert_update,
    "required": False,
    "empty": True,
}
additional_post_code_insert_update = {
    "type": "list",
    "required": True,
    "empty": True,
    "schema": {"type": "string", "empty": True, "regex": "^([0-9]|1[0-5])$"},
}
additional_post_code_select = {
    **additional_post_code_insert_update,
    "required": False,
}
# 教科コードはLDAP上でカンマ区切り(=subject_code)なので、
# 教科マスタは(=subject_code_element)として区別する
subject_code_element_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 4,
    "regex": "^[0-9a-zA-Z]+$",
}
subject_code_insert_update = {
    "type": "list",
    "required": True,
    "empty": True,
    "schema": subject_code_element_insert_update,
}
subject_code_select = {**subject_code_insert_update, "required": False}
subject_code_element_select = {
    **subject_code_element_insert_update,
    "required": False,
    "empty": True,
}
subject_name_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
enable_flag = {
    "type": "integer",
    "required": False,
    "empty": False,
    "allowed": [0, 1],
}
enable_flag_required = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [0, 1],
}
operation_status_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "allowed": ["1", "2", "3", "4", "7", "8", "9"],
}
operation_type_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "allowed": [
        "admin01",
        "admin02",
        # 　新規追加（案件８．OPE管理者の削除）　START
        "admin03",
        # 　新規追加（案件８．OPE管理者の削除）　END
        # 　新規追加（OneRoster対応）　START
		# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
        "admin11",
        "admin12",
        "admin13",
		# ↑ここまで
        # 　新規追加（OneRoster対応）　END
        "teacher01",
        "teacher02",
        "teacher03",
        "teacher04",
        "teacher05",
        "teacher11",
        "teacher12",
        # 　新規追加 START
        "teacher13",
        "teacher14",
        "teacher15",
        "teacher16",
        # 　新規追加 END
        "student01",
        "student02",
        "student03",
        "student04",
        "student05",
        "student11",
        "student12",
        "student13",
        "student14",
        "school11",
        "autog11"
    ],
}
target_id_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "maxlength": 385,
    "regex": "^[0-9a-zA-Z]+$",
}
target_name_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "maxlength": 21,
    "regex": "^[0-9a-zA-Z一-龻ぁ-ゔゝゞ々ァ-ヺ０-９ａ-ｚＡ-Ｚ]+　"
             "[0-9a-zA-Z一-龻ぁ-ゔゝゞ々ァ-ヺ０-９ａ-ｚＡ-Ｚ]+$",
}
operator_id_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "minlength": 6,
    "maxlength": 16,
    "regex": "^[0-9a-zA-Z]+$",
}
date_select = {
    "type": "string",
    "required": False,
    "empty": True,
    "regex": "^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$",
}
student_number_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 3,
    "regex": "^[1-9]{1}[0-9]*$",
}
student_number_select = {**student_number_insert_update, "required": False}
export_term = {
    "type": "integer",
    "required": False,
    "empty": True,
    "maxlength": 3,
    "regex": "^[0-9]+$",
}
hours_ago = {
    "type": "integer",
    "required": False,
    "empty": True,
    "maxlength": 3,
    "regex": "^[0-9]+$",
}
export_type = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": ["all", "add", "diff"],
}
school_name_ja_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
school_kana_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64,
    "regex": "^[ァ-ヾ０-９　ー―－‐]+$",
}
school_nickname_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 32,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
district_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 256,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
zip_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "regex": "^[0-9]{3}-[0-9]{4}$",
}
address_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 256,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
address_kana_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 256,
    "regex": "^[ァ-ヾ０-９　ー―－‐]+$",
}
telnumber_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 17,
    "minlength": 12,
    "regex": "^[0-9]{2,5}-[0-9]{1,4}-[0-9]{4}$",
}
hp_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 2000,
    "regex": "^(http|https)://([\w-]+\.)+[\w-]+(/[\w\-./?%&=]*)?$",
}
remarks_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 2000,
    # 制御コード（改行\n除く）以外すべて許可
    "regex": "^[^\x00-\x09\x0b-\x1f\x7f]+$",
}
remarks_insert_update_csv = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 2000,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
show_no_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "min": 1,
    "max": 999,
}
with_applic_flag = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [0, 1],
}
update_mode = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [1, 2, 3],
}
auto_generator_no_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 3,
    "regex": "^[^0][0-9]*$",
}
auto_generator_organization_name_ja_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 64,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
auto_generator_school_nickname_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 10,
    # 制御コード以外すべて許可
    "regex": "^[^\x00-\x1f\x7f]+$",
}
auto_generator_school_nickname_kana_insert_update = {
    "type": "string",
    "required": True,
    "empty": False,
    "maxlength": 20,
    # ひらがな、全角スペース、半角スペース、伸ばし棒、中点のみ
    "regex": "^[\u3041-\u3096\s　ー―‐－・]+$",
}
google_account_insert_update = {
    "type": "string",
    "required": True,
    "empty": True,
    "maxlength": 256,
    "regex": "^[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
}
teacher_count_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "min": 1,
    "max": 3000,
}
class_count_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "min": 1,
    "max": 20,
}
student_count_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "min": 1,
    "max": 99,
}
exist_school_flg_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "allowed": [0, 1],
}
relationgg = {"type": "integer", "required": True, "allowed": [0, 1]}
relationwin = {"type": "integer", "required": True, "allowed": [0, 1, 2]}
csv_file = {"type": "string", "required": True, "empty": False}
filter_upd_date = {
    "type": "string",
    "required": False,
    "empty": True,
    "regex": (
        "^(?:"
        "[(]updDate ge [0-9]{8}(?: and updDate le [0-9]{8})?[)]"
        "|"
        "updDate ge [0-9]{8}(?: and updDate le [0-9]{8})?"
        ")$"
    ),
}
fiscal_year_insert_update = {
    "type": "integer",
    "required": True,
    "empty": False,
    "max": 9999,
    "min": 1000,
    "regex": "^[0-9]+$",
}
fiscal_year_select = {
    **fiscal_year_insert_update,
    "required": False,
    "empty": True
}
scim_attributes = {
    "type": "list",
    "required": False,
    "empty": True,
    "schema": {
        "empty": False,
        "type": "string",
        "allowed": [
            "emails",
            "roles",
            "jaDisplayName",
            "jasn",
            "jaGivenName",
            "jsFedKanaSn",
            "jsFedKanaGivenName",
            "gender",
            "eduPersonAffiliation",
            "jsFedGrade",
            "jsFedJaGradeName",
            "jsFedClass",
            "jsFedJaClassName",
            "jsFedSubject",
            "jsFedTitle",
            "jsFedAPost",
            "jsFedStudentNumber",
            "o",
            "jao",
            "jsFedO",
            "jsFedOType",
            "ou",
            "jaou",
            "jsFedOu",
            "jsFedOuType",
            "jsFedFiscalYear",
            # 　新規追加（文科省標準の学校コード追加）　START
            "mextUid",
            "mextOuCode",
            "jsFedTransferDate",
            "jsFedSourceOu",
            # 　新規追加（文科省標準の学校コード追加）　END
            # 　新規追加（案件１６．すらら連携項目追加の対応-ID管理RLS）　START
            "RegDate",
            # 　新規追加（案件１６．すらら連携項目追加の対応-ID管理RLS）　START
        ],
    },
}
scim_master_attributes = {
    "type": "list",
    "required": False,
    "empty": True,
    "schema": {
        "empty": False,
        "type": "string",
        "allowed": [
            # 　新規追加（マルチテナント化対応）　START
            "organizationCode",
            "organizationName",
            # 　新規追加（マルチテナント化対応）　END
            "schoolCode",
            "schoolName",
            "schoolNameJa",
            "schoolKana",
            "schoolNickName",
            "schoolType",
            "district",
            "zip",
            "address1",
            "address2",
            "address1Kana",
            "address2Kana",
            "telnumber",
            "faxnumber",
            "schoolMail",
            "schoolHp",
            "haikouFlag",
            "haikouDate",
            "haikousakiSchoolCode",
            "remarks",
            "gradeCode",
            "gradeNameJa",
            "classCode",
            "classNameJa",
            "classType",
            "subjectCode",
            "subjectName",
            "showNo",
            "noDeleteFlag",
            # 　新規追加（文科省標準の学校コード追加）　START
            "mextOuCode",
            # 　新規追加（文科省標準の学校コード追加）　END
        ],
    },
}
"""
正規表現チェックの名称
"""
regex_title = {
    "user_id": "は半角英数字で入力してください",
    "before_user_id": "は半角英数字で入力してください",
    "before_user_id_transfer": "は半角英数字で入力してください",
    "persistent_uid": "は半角英数字で入力してください",
    "sur_name": "に記号またはスペースを使用できません",
    "given_name": "に記号またはスペースを使用できません",
    "sur_name_kana": "はひらがな、伸ばし棒、スペース、「・」で入力してください",
    "given_name_kana": "はひらがな、伸ばし棒、スペース、「・」で入力してください",
    "gender": "は空または1～2を入力してください",
    "mail": "はメールアドレス形式で入力してださい",
    # 　新規追加（マルチテナント化対応）　START
    "system_organization_code": "は半角英数で入力してください",
    "system_organization_name": "は半角英数記号またはスペースで入力してください",
    # 　新規追加（マルチテナント化対応）　END
    "organization_name": "は半角英数記号で入力してください",
    "organization_name_ja": "にタブや改行は使用できません",
    "organization_code": "は半角英数で入力してください",
    "organization_type": "は2～6の間で入力してください",
    "user_password": "は半角英数字、記号で入力してください",
    "password": "は半角英数字、記号で入力してください",
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "grade_code": "は半角英数字で入力してください",
    "before_grade_code": "は半角英数字で入力してください",
    "before_grade_code_transfer": "は半角英数字で入力してください",
	# ↑ここまで
    "before_organization_code": "は半角英数字で入力してください",
    "grade_name_ja": "",
    "class_code": "は半角数字3文字以下で入力してください",
    "class_name_ja": "",
    "role": "は指定されたものを入力してください",
    "title_code": "は指定されたものを入力してください",
    "additional_post_code": "は指定されたものを入力してください",
    "subject_code": "は4桁までの半角英数(複数の場合はカンマ区切り)で入力してください",
    "subject_name": "",
    "target_id": "",
    "operator_id": "",
    "date": "",
    "student_number": "は1～999の間で入力してください",
    "relationgg": "は0または1を入力してください",
    "relationwin": "は0～2の間で入力してください",
    "export_term": "",
    "hours_ago": "",
    "school_code": "は半角英数記号で入力してください",
    "school_name": "は半角英数記号で入力してください",
    "school_name_ja": "にタブや改行を使用できません",
    "school_kana": "はカタカナで入力してください",
    "school_nickname": "にタブや改行を使用できません",
    "school_nickname_kana": "にタブや改行を使用できません",
    "school_type": "は2～8の間で入力してください",
    # 　新規追加（マルチテナント化対応）　START
    "school_type_kg": "は98で入力してください",
    # 　新規追加（マルチテナント化対応）　END
    "district": "にタブや改行を使用できません",
    "zip": "は「-」の付いた形式で入力してください",
    "address1": "にタブや改行を使用できません",
    "address1_kana": "にタブや改行を使用できません",
    "address2": "にタブや改行を使用できません",
    "address2_kana": "にタブや改行を使用できません",
    "telnumber": "は「-」の付いた形式で入力してください",
    "faxnumber": "は「-」の付いた形式で入力してください",
    "school_hp": "はURL形式で入力してください",
    "school_mail": "はメールアドレス形式で入力してください",
    "remarks": "にタブを使用できません",
    "with_applic_flag": "には0または1を入力してください",
    "teacher_count": "には1～3000を入力してください",
    "class_count": "には1～20を入力してください",
    "student_count": "には1～99を入力してください",
    "google_account": "はドメイン形式で入力してください",
    "no": "には1～999を入力してください",
    "show_no": "には1～999を入力してください",
    "fiscal_year": "には1000～9999を入力してください",
    "exist_school_flg": "は0または1を入力してください",
    # 　新規追加（文科省標準の学校コード追加）　START
    "mextOuCode_prefix": "は[S, B, P]の一つを入力してください",
    "mextOuCode_code": "は半角英数字で入力してください",
    "mextOuCode": "は接頭子：[S, B, P]の一つ、コード：半角英数字で入力してください",
    # 　新規追加（文科省標準の学校コード追加）　END
    # 　新規追加（年次更新の効率化_クラス情報一括登録バッチ）　START
    "class_type": "は[1, 2, 3]の一つを入力してください"
    # 　新規追加（年次更新の効率化_クラス情報一括登録バッチ）　END　
}
