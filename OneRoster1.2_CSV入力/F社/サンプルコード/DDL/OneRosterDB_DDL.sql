CREATE DATABASE 【データベース名を記入】;

CREATE TABLE `orgs_import` (
  `sourcedId` varchar(255) NOT NULL,
  `status` text,
  `dateLastModified` text,
  `name` text,
  `type` text,
  `identifier` text,
  `parentSourcedId` text,
  `city_name` varchar(255) DEFAULT NULL,
  `orgs_managementid` varchar(255) DEFAULT NULL,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`sourcedId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `classes_import` (
  `sourcedId` varchar(255) NOT NULL,
  `status` text,
  `dateLastModified` text,
  `title` text,
  `grades` text,
  `courseSourcedId` text,
  `classCode` text,
  `classType` text,
  `location` text,
  `schoolSourcedId` text,
  `termSourcedIds` text,
  `subjects` text,
  `subjectCodes` text,
  `periods` text,
  `metadata_jp_specialNeeds` text,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`sourcedId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `users_import` (
  `sourcedId` varchar(255) NOT NULL,
  `status` text,
  `dateLastModified` text,
  `enabledUser` text,
  `username` text,
  `userIds` text,
  `givenName` text,
  `familyName` text,
  `middleName` text,
  `identifier` text,
  `email` text,
  `sms` text,
  `phone` text,
  `agentSourcedIds` text,
  `grades` text,
  `password` text,
  `userMasterIdentifier` text,
  `resourceSourcedIds` text,
  `preferredGivenName` text,
  `preferredMiddleName` text,
  `preferredFamilyName` text,
  `primaryOrgSourcedId` text,
  `pronouns` text,
  `metadata_jp_kanaGivenName` text,
  `metadata_jp_kanaFamilyName` text,
  `metadata_jp_kanaMiddleName` text,
  `metadata_jp_homeClass` text,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`sourcedId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `enrollments_import` (
  `sourcedId` varchar(255) NOT NULL,
  `status` text,
  `dateLastModified` text,
  `classSourcedId` text,
  `schoolSourcedId` text,
  `userSourcedId` text,
  `role` text,
  `csv_primary` text,
  `beginDate` text,
  `endDate` text,
  `metadata_jp_ShussekiNo` text,
  `metadata_jp_PublicFlg` text,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`sourcedId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `users_export` (
  `sourcedId` varchar(255) NOT NULL,
  `school_code` varchar(255) NOT NULL,
  `userSourcedId` varchar(255) NOT NULL,
  `account_id` varchar(255) NOT NULL,
  `password` varchar(6) NOT NULL,
  `classSourcedId` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `school_year` varchar(255) DEFAULT NULL,
  `class` varchar(255) DEFAULT NULL,
  `ShussekiNo` varchar(255) DEFAULT NULL,
  `student_number` varchar(255) DEFAULT NULL,
  `expire_date` varchar(10) NOT NULL DEFAULT '2100-03-31',
  `role` varchar(1) NOT NULL,
  `trial` varchar(4) NOT NULL DEFAULT 'COMP',
  `nickname` varchar(100) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`sourcedId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `csv_import` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `dir_name` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `imported_at` timestamp DEFAULT NULL,
  `status` tinyint(1) DEFAULT 0,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `csv_export` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `exported_at` timestamp DEFAULT NULL,
  `status` tinyint(1) DEFAULT 0,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `not_export_schools` (
  `school_code` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`school_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `db_register` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `registered_at` timestamp DEFAULT NULL,
  `status` tinyint(1) DEFAULT 0,
  `created_at` timestamp DEFAULT NULL,
  `updated_at` timestamp DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
