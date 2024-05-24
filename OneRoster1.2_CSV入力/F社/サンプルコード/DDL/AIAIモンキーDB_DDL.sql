CREATE DATABASE 【データベース名を記入】;

CREATE TABLE `schools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL COMMENT '作成日',
  `modified` datetime NOT NULL COMMENT '更新日',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '学校名',
  `code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '学校コード',
  `max_student_num` int NOT NULL COMMENT '最大生徒数',
  `expiration_date` date NOT NULL COMMENT '有効期限',
  `school_type` enum('other','elementary','middle','high') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'other' COMMENT '学校種別',
  `status` enum('publish','draft') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'publish' COMMENT 'ステータス',
  `orgssourcedId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用',
  `identifier` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `classes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL COMMENT '作成日',
  `modified` datetime NOT NULL COMMENT '更新日',
  `school_id` int NOT NULL DEFAULT '0' COMMENT '学校ID',
  `grade_label` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `class_label` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `status` enum('publish','draft') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'publish' COMMENT 'ステータス',
  `classsourcedId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用',
  `identifier` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用',
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL COMMENT '作成日',
  `modified` datetime NOT NULL COMMENT '更新日',
  `logined_datetime` datetime DEFAULT NULL COMMENT '最終ログイン日',
  `school_id` int NOT NULL DEFAULT '0' COMMENT '学校ID',
  `class_id` int NOT NULL DEFAULT '0' COMMENT 'クラスID',
  `student_number` int NOT NULL DEFAULT '0' COMMENT '出席番号',
  `nickname` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT 'ニックネーム',
  `account_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'ログインID',
  `account_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'ログインPW',
  `role` enum('admin','school_admin','teacher','student') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '権限',
  `bk_provider` enum('none','manabi') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'none' COMMENT '_学びポケットか直接',
  `status` enum('publish','draft') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'publish' COMMENT 'ステータス',
  `userssourcedId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用	',
  `identifier` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '先方利用	',
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `user_owned_classes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL COMMENT '作成日',
  `modified` datetime NOT NULL COMMENT '更新日',
  `user_id` int NOT NULL,
  `class_id` int NOT NULL,
  `student_number` int NOT NULL DEFAULT '0' COMMENT '出席番号',
  `is_default` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `class_id` (`class_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
