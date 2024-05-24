# coding: utf-8
from common import base_validation as bv

"""
cerberus 教員情報登録APIバリデーションスキーマ
"""
# 教員情報登録APIバリデーションスキーマ
teacher_create_request = {
    "user_id": bv.user_id_insert_update,
    "persistent_uid": bv.persistent_uid_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update,
    "gender": bv.gender_insert_update,
    "role": bv.role_teacher_insert_update,
    "title_code": bv.title_code_insert_update_list,
    "additional_post_code": bv.additional_post_code_insert_update,
    "subject_code": bv.subject_code_insert_update,
    "grade_code": bv.grade_code_insert_update,
    "class_code": bv.class_code_insert_update,
    "mail": bv.mail_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
    "fiscal_year": bv.fiscal_year_insert_update,
}
# 教員一括登録API行ごとバリデーションスキーマ
teacher_bulk_create_row_request = {
    **teacher_create_request,
}

# 教員情報一括更新APIバリデーションスキーマ
teacher_bulk_update_body_request = {
    "user_id": bv.user_id_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update_allow_required,
    "gender": bv.gender_insert_update,
    "role": bv.role_teacher_insert_update,
    "title_code": bv.title_code_insert_update_list,
    "additional_post_code": bv.additional_post_code_insert_update,
    "subject_code": bv.subject_code_insert_update,
    "grade_code": bv.grade_code_insert_update,
    "class_code": bv.class_code_insert_update,
    "mail": bv.mail_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
    "fiscal_year": bv.fiscal_year_insert_update,
}
# 教員一括更新API行ごとバリデーションスキーマ
teacher_bulk_update_row_request = {
    **teacher_bulk_update_body_request,
}

# 教員情報一括異動APIバリデーションスキーマ
teacher_bulk_transfer_body_request = {
    "before_organization_code": bv.organization_code_insert_update,
    "user_id": bv.user_id_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update_allow_required,
    "gender": bv.gender_insert_update,
    "role": bv.role_teacher_insert_update,
    "title_code": bv.title_code_insert_update_list,
    "additional_post_code": bv.additional_post_code_insert_update,
    "subject_code": bv.subject_code_insert_update,
    "grade_code": bv.grade_code_insert_update,
    "class_code": bv.class_code_insert_update,
    "mail": bv.mail_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
    "fiscal_year": bv.fiscal_year_insert_update,
}
# 教員情報一括異動API行ごとバリデーションスキーマ
teacher_bulk_transfer_row_request = {
    **teacher_bulk_transfer_body_request,
}

# 児童生徒情報登録・更新・異動APIバリデーションスキーマ
student_create_request = {
    "user_id": bv.user_id_insert_update,
    "persistent_uid": bv.persistent_uid_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update,
    "gender": bv.gender_insert_update,
    "grade_code": bv.grade_code_insert_update_not_empty,
    "class_code": bv.class_code_insert_update,
    "student_number": bv.student_number_insert_update,
    "mail": bv.mail_insert_update,
    "organization_code": bv.organization_code_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "fiscal_year": bv.fiscal_year_insert_update,
}
# 児童生徒情報一括登録API行ごとバリデーションスキーマ
student_bulk_create_row_request = {
    **student_create_request,
}

# 児童生徒情報一括更新APIバリデーションスキーマ
student_bulk_update_body_request = {
    "before_user_id": bv.user_id_insert_update,
    "before_grade_code": bv.grade_code_insert_update_not_empty,
    "fiscal_year": bv.fiscal_year_insert_update,
    "user_id": bv.user_id_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update_allow_required,
    "gender": bv.gender_insert_update,
    "mail": bv.mail_insert_update,
    "grade_code": bv.grade_code_insert_update_not_empty,
    "class_code": bv.class_code_insert_update,
    "student_number": bv.student_number_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
}
# 児童生徒情報一括更新API行ごとバリデーションスキーマ
student_bulk_update_row_request = {
    **student_bulk_update_body_request,
}

# 児童生徒情報進学APIバリデーションスキーマ
student_bulk_transfer_body_request = {
    "before_organization_code": bv.organization_code_insert_update,
    "before_user_id_transfer": bv.user_id_insert_update,
    "before_grade_code_transfer": bv.grade_code_insert_update_not_empty,
    "user_id": bv.user_id_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "sur_name_kana": bv.sur_name_kana_insert_update,
    "given_name_kana": bv.given_name_kana_insert_update,
    "password": bv.user_password_insert_update_allow_required,
    "gender": bv.gender_insert_update,
    "mail": bv.mail_insert_update,
    "grade_code": bv.grade_code_insert_update_not_empty,
    "class_code": bv.class_code_insert_update,
    "student_number": bv.student_number_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
    "fiscal_year": bv.fiscal_year_insert_update,
}
# 児童生徒情報進学API行ごとバリデーションスキーマ
student_bulk_transfer_row_request = {
    **student_bulk_transfer_body_request,
}
# 児童・生徒情報削除API用バリデーションスキーマ
student_delete_request = {
    "user_id": bv.user_id_insert_update,
    "organization_code": bv.organization_code_insert_update,
    "grade_code": bv.grade_code_insert_update_not_empty,
}
# 教員差分削除用のバリエーション
teacher_delete_request = {
    "user_id": bv.user_id_insert_update,
    "organization_code": bv.organization_code_insert_update
}
# OPE管理者差分削除用のバリエーション
admin_delete_request = {
    "user_id": bv.user_id_insert_update,
    "organization_code": bv.organization_code_insert_update
}
# OPE管理者登録用のバリエーション
opeadmin_create_request = {
    "user_id": bv.user_id_insert_update,
    "persistent_uid": bv.persistent_uid_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "gender": bv.gender_insert_update,
    "role": bv.role_insert_update,
    "mail": bv.mail_opeadmin_insert_update,
    "password": bv.user_password_insert_update,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
}
# OPE管理者更新用のバリエーション
opeadmin_update_request = {
    "user_id": bv.user_id_insert_update,
    "sur_name": bv.sur_name_insert_update,
    "given_name": bv.given_name_insert_update,
    "gender": bv.gender_insert_update,
    "role": bv.role_insert_update,
    "mail": bv.mail_opeadmin_insert_update,
    "password": bv.user_password_insert_update_allow_required,
    "relationgg": bv.relationgg,
    "relationwin": bv.relationwin,
    "organization_code": bv.organization_code_insert_update,
}
