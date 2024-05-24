# coding: utf-8
"""
request-lambda間mappingルール
"""
reception_mappings = {
    "/opeadmin/create": {
        "module": "app.handler_opeadmin",
        "handler": "reception_insert_opeadmin_handler",
    },
    "/opeadmin/update": {
        "module": "app.handler_opeadmin",
        "handler": "reception_update_opeadmin_handler",
    },
    # 　新規追加（案件８．OPE管理者の削除）　START
    "/opeadmin/delete": {
        "module": "app.handler_opeadmin",
        "handler": "reception_delete_opeadmin_handler",
    },
    # 　新規追加（案件８．OPE管理者の削除）　END
    "/opeadmin/password_update": {
        "module": "app.handler_opeadmin",
        "handler": "update_password_opeadmin_handler",
    },
    "/teacher/create": {
        "module": "app.handler_teacher",
        "handler": "reception_insert_teacher_handler",
    },
    "/teacher/update": {
        "module": "app.handler_teacher",
        "handler": "reception_update_teacher_handler",
    },
    "/teacher/delete": {
        "module": "app.handler_teacher",
        "handler": "reception_delete_teacher_handler",
    },
    "/teacher/recreate/create": {
        "module": "app.handler_teacher",
        "handler": "reception_recreate_teacher_handler",
    },
    "/teacher/bulk/create": {
        "module": "app.handler_bulk_teacher",
        "handler": "reception_bulk_insert_teacher_handler",
    },
    "/teacher/bulk/update": {
        "module": "app.handler_bulk_teacher",
        "handler": "reception_bulk_update_teacher_handler",
    },
    # 　新規追加 START
    "/teacher/bulk/transfer": {
        "module": "app.handler_bulk_teacher",
        "handler": "reception_bulk_transfer_teacher_handler",
    },
    "/teacher/bulk/delete": {
        "module": "app.handler_bulk_teacher",
        "handler": "reception_bulk_delete_teacher_handler",
    },
    "/teacher/batch_bulk/create": {
        "module": "app.handler_bulk_teacher_batch",
        "handler": "reception_bulk_insert_teacher_batch_handler",
    },
    "/teacher/batch_bulk/update": {
        "module": "app.handler_bulk_teacher_batch",
        "handler": "reception_bulk_update_teacher_batch_handler",
    },
    # 　新規追加 END
    "/student/create": {
        "module": "app.handler_student",
        "handler": "reception_insert_student_handler",
    },
    "/student/update": {
        "module": "app.handler_student",
        "handler": "reception_update_student_handler",
    },
    "/student/delete": {
        "module": "app.handler_student",
        "handler": "reception_delete_student_handler",
    },
    "/student/recreate/create": {
        "module": "app.handler_student",
        "handler": "reception_recreate_student_handler",
    },
    "/student/bulk/create": {
        "module": "app.handler_bulk_student",
        "handler": "reception_bulk_insert_student_handler",
    },
    "/student/bulk/update": {
        "module": "app.handler_bulk_student",
        "handler": "reception_bulk_update_student_handler",
    },
    "/student/bulk/delete": {
        "module": "app.handler_bulk_student",
        "handler": "reception_bulk_delete_student_handler",
    },
    "/student/bulk/transfer": {
        "module": "app.handler_bulk_student",
        "handler": "reception_bulk_transfer_student_handler",
    },
    "/school/bulk/create": {
        "module": "app.handler_master_bulk_reception",
        "handler": "reception_bulk_insert_school_handler",
    },
    "/auto_generator": {
        "module": "app.handler_auto_generator",
        "handler": "reception_auto_generator_handler",
    },
}
api_resource_mappings = {
    "/school/create": {
        "module": "app.handler_master_school",
        "handler": "school_create_handler",
    },
    "/school/update": {
        "module": "app.handler_master_school",
        "handler": "school_update_handler",
    },
    "/school/list": {
        "module": "app.handler_master_school",
        "handler": "school_search_handler",
    },
    "/school/delete": {
        "module": "app.handler_master_school",
        "handler": "school_delete_handler",
    },
    "/class/create": {
        "module": "app.handler_master_class",
        "handler": "class_create_handler",
    },
    "/class/list": {
        "module": "app.handler_master_class",
        "handler": "class_search_handler",
    },
    "/class/delete": {
        "module": "app.handler_master_class",
        "handler": "class_delete_handler",
    },
    "/class/update": {
        "module": "app.handler_master_class",
        "handler": "class_update_handler",
    },
    "/grade/list": {
        "module": "app.handler_master_grade",
        "handler": "grade_search_handler",
    },
    "/grade/create": {
        "module": "app.handler_master_grade",
        "handler": "grade_create_handler",
    },
    "/grade/delete": {
        "module": "app.handler_master_grade",
        "handler": "grade_delete_handler",
    },
    "/grade/update": {
        "module": "app.handler_master_grade",
        "handler": "grade_update_handler",
    },
    "/subject/create": {
        "module": "app.handler_master_subject",
        "handler": "subject_create_handler",
    },
    "/subject/list": {
        "module": "app.handler_master_subject",
        "handler": "subject_search_handler",
    },
    "/subject/delete": {
        "module": "app.handler_master_subject",
        "handler": "subject_delete_handler",
    },
    "/subject/update": {
        "module": "app.handler_master_subject",
        "handler": "subject_update_handler",
    },
    "/student/recreate/list": {
        "module": "app.handler_student",
        "handler": "student_recreate_search_handler",
    },
    "/teacher/recreate/list": {
        "module": "app.handler_teacher",
        "handler": "teacher_recreate_search_handler",
    },
}
api_mappings = {
    "admin01": {
        "module": "app.handler_opeadmin",
        "handler": "insert_opeadmin_handler",
    },
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "admin11": {
        "module": "app.handler_opeadmin",
        "handler": "insert_opeadmin_handler",
    },
	# ↑ここまで
    "admin02": {
        "module": "app.handler_opeadmin",
        "handler": "update_opeadmin_handler",
    },
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "admin12": {
        "module": "app.handler_opeadmin",
        "handler": "update_opeadmin_handler",
    },
	# ↑ここまで
    # 　新規追加（案件８．OPE管理者の削除）　START
    "admin03": {
        "module": "app.handler_opeadmin",
        "handler": "delete_opeadmin_handler",
    },
    # 　新規追加（案件８．OPE管理者の削除）　END
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "admin13": {
        "module": "app.handler_opeadmin",
        "handler": "delete_opeadmin_handler",
    },
	# ↑ここまで
    "teacher01": {
        "module": "app.handler_teacher",
        "handler": "insert_teacher_handler",
    },
    "teacher11": {
        "module": "app.handler_teacher",
        "handler": "insert_teacher_handler",
    },
    "teacher02": {
        "module": "app.handler_teacher",
        "handler": "update_teacher_handler",
    },
    "teacher12": {
        "module": "app.handler_teacher",
        "handler": "update_teacher_handler",
    },
    # 　新規追加 START
    "teacher13": {
        "module": "app.handler_teacher",
        "handler": "delete_teacher_handler",
    },
    "teacher14": {
        "module": "app.handler_teacher",
        "handler": "update_teacher_handler",
    },
    "teacher15": {
        "module": "app.handler_teacher",
        "handler": "insert_teacher_handler",
    },
    "teacher16": {
        "module": "app.handler_teacher",
        "handler": "update_teacher_handler",
    },
    # 　新規追加 END
    "teacher03": {
        "module": "app.handler_teacher",
        "handler": "delete_teacher_handler",
    },
    "teacher04": {
        "module": "app.handler_teacher",
        "handler": "recreate_teacher_handler",
    },
    "teacher05": {
        "module": "app.handler_teacher",
        "handler": "update_teacher_handler",
    },
    "student01": {
        "module": "app.handler_student",
        "handler": "insert_student_handler",
    },
    "student02": {
        "module": "app.handler_student",
        "handler": "update_student_handler",
    },
    "student03": {
        "module": "app.handler_student",
        "handler": "delete_student_handler",
    },
    "student04": {
        "module": "app.handler_student",
        "handler": "recreate_student_handler",
    },
    "student05": {
        "module": "app.handler_student",
        "handler": "update_student_handler",
    },
    "student11": {
        "module": "app.handler_student",
        "handler": "insert_student_handler",
    },
    "student12": {
        "module": "app.handler_student",
        "handler": "update_student_handler",
    },
    "student13": {
        "module": "app.handler_student",
        "handler": "delete_student_handler",
    },
    "student14": {
        "module": "app.handler_student",
        "handler": "update_student_handler",
    },
}
register_mappings = {
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "admin11": {
        "module": "app.handler_bulk_register_opeadmin",
        "handler": "register_bulk_insert_admin_handler",
    },
    "admin12": {
        "module": "app.handler_bulk_register_opeadmin",
        "handler": "register_bulk_update_admin_handler",
    },
    "admin13": {
        "module": "app.handler_bulk_register_opeadmin",
        "handler": "register_bulk_delete_admin_handler",
    },
	# ↑ここまで
    "teacher11": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_insert_teacher_handler",
    },
    "teacher12": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_update_teacher_handler",
    },
    # 　新規追加 START
    "teacher13": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_delete_teacher_handler",
    },
    "teacher14": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_transfer_teacher_handler",
    },
    "teacher15": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_insert_teacher_handler",
    },
    "teacher16": {
        "module": "app.handler_bulk_register_teacher",
        "handler": "register_bulk_update_teacher_handler",
    },
    # 　新規追加 END
    "student11": {
        "module": "app.handler_bulk_register_student",
        "handler": "register_bulk_insert_student_handler",
    },
    "student12": {
        "module": "app.handler_bulk_register_student",
        "handler": "register_bulk_update_student_handler",
    },
    "student13": {
        "module": "app.handler_bulk_register_student",
        "handler": "register_bulk_delete_student_handler",
    },
    "student14": {
        "module": "app.handler_bulk_register_student",
        "handler": "register_bulk_transfer_student_handler",
    },
    "school11": {
        "module": "app.handler_master_school",
        "handler": "school_bulk_insert_handler",
    },
}
