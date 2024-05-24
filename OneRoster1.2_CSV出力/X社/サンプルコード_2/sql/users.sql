SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
    , CONCAT('"', enabledUser,'"')            AS enabledUser
    , username                                AS username
    , userIds                                 AS userIds
    , givenName                               AS givenName
    , familyName                              AS familyName
    , middleName                              AS middleName
    , identifier                              AS identifier
    , email                                   AS email
    , CONCAT('"', sms,'"')                    AS sms
    , CONCAT('"', phone,'"')                  AS phone
    , CONCAT('"', agentSourcedIds,'"')        AS agentSourcedIds
    , CONCAT('"', grades,'"')                 AS grades
    , password                                AS password
    , userMasterIdentifier                    AS userMasterIdentifier
    ,'""'                                     AS resourceSourcedIds
    , preferredFirstName                      AS preferredGivenName
    , preferredMiddleName                     AS preferredMiddleName
    , preferredLastName                       AS preferredFamilyName
    , CONCAT('"', orgSourcedIds,'"')          AS primaryOrgSourcedId
    ,'""'                                     AS pronouns
    , [metadata.jp.kanaGivenName]             AS [metadata.jp.kanaGivenName]
    , [metadata.jp.kanaFamilyName]            AS [metadata.jp.kanaFamilyName]
    , [metadata.jp.kanaMiddleName]            AS [metadata.jp.kanaMiddleName]
    , CONCAT('"',[metadata.jp.homeClass],'"') AS [metadata.jp.homeClass]
FROM (
SELECT OR_User.SourcedId AS sourcedId,
	CASE 
		WHEN $(ReferenceDateTime) LIKE '' THEN ''
		ELSE OR_User.Status
		END
		AS status,
	CASE
		WHEN $(ReferenceDateTime) LIKE '' THEN ''
		ELSE FORMAT(OR_User.DateLastModified,'yyyy-MM-ddTHH:mm:ss.fffZ')
		END
		AS dateLastModified,
	(CASE OR_User.EnabledUser
			WHEN 1 THEN CONVERT(nvarchar(255), 'true')
			WHEN 0 THEN CONVERT(nvarchar(255), 'false')
			END) AS enabledUser,
	CASE
	WHEN OR_UserOrg.Org IS NULL THEN ''
	WHEN 
	SUBSTRING(
	(SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')),1,
	LEN((SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')))-1
	) 
	LIKE '%,%' THEN
	'"'+
	SUBSTRING(
	(SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')),	1,
	LEN((SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')))-1
	)+
	'"'
	ELSE 
	SUBSTRING(
	(SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')),	1,
	LEN((SELECT CONVERT(nvarchar(255),OR_UserOrg.Org) + ','
	FROM OR_UserOrg
	WHERE OR_User.SourcedId = OR_UserOrg.[User]
	FOR XML PATH('')))-1
	)
	END
	 AS orgSourcedIds,
	OR_User.Role AS role,
	CASE 
		WHEN OR_User.UserName IS NULL THEN '""'
		WHEN OR_User.UserName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.UserName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.UserName LIKE '%'+NCHAR(10)+'%' OR OR_User.UserName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.UserName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.UserName) + '"'
		END
		AS username,
	CASE 
		WHEN OR_User.UserIds  IS NULL OR $(USER_IDS_TYPE_LABEL) IS NULL THEN '""'
		WHEN '{'+ $(USER_IDS_TYPE_LABEL) + ':'+OR_User.UserIds+'}' LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE('{'+$(USER_IDS_TYPE_LABEL)+':'+OR_User.UserIds+'}',NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN '{'+ $(USER_IDS_TYPE_LABEL) + ':'+OR_User.UserIds+'}' LIKE '%'+NCHAR(10)+'%' OR '{'+$(USER_IDS_TYPE_LABEL)+':'+OR_User.UserIds+'}' LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE('{'+$(USER_IDS_TYPE_LABEL)+':'+OR_User.UserIds+'}',NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), '{'+$(USER_IDS_TYPE_LABEL)+':'+OR_User.UserIds+'}') + '"'
		END
		AS userIds,
	CASE 
		WHEN OR_User.GivenName IS NULL THEN '""'
		WHEN OR_User.GivenName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.GivenName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.GivenName LIKE '%'+NCHAR(10)+'%' OR OR_User.GivenName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.GivenName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.GivenName) + '"'
		END
		AS givenName,
	CASE 
		WHEN OR_User.FamilyName IS NULL THEN '""'
		WHEN OR_User.FamilyName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.FamilyName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.FamilyName LIKE '%'+NCHAR(10)+'%' OR OR_User.FamilyName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.FamilyName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.FamilyName) + '"'
		END
		AS familyName,
	CASE 
		WHEN OR_User.MiddleName IS NULL THEN '""'
		WHEN OR_User.MiddleName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.MiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.MiddleName LIKE '%'+NCHAR(10)+'%' OR OR_User.MiddleName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.MiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.MiddleName) + '"'
		END
		AS middleName,
	CASE 
		WHEN OR_User.preferredFirstName IS NULL THEN '""'
		WHEN OR_User.preferredFirstName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredFirstName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.preferredFirstName LIKE '%'+NCHAR(10)+'%' OR OR_User.preferredFirstName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredFirstName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.preferredFirstName) + '"'
		END
		AS preferredFirstName,
	CASE 
		WHEN OR_User.preferredLastName IS NULL THEN '""'
		WHEN OR_User.preferredLastName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredLastName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.preferredLastName LIKE '%'+NCHAR(10)+'%' OR OR_User.preferredLastName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredLastName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.preferredLastName) + '"'
		END
		AS preferredLastName,
	CASE 
		WHEN OR_User.preferredMiddleName IS NULL THEN '""'
		WHEN OR_User.preferredMiddleName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.preferredMiddleName LIKE '%'+NCHAR(10)+'%' OR OR_User.preferredMiddleName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.preferredMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.preferredMiddleName) + '"'
		END
		AS preferredMiddleName,
	CASE 
		WHEN OR_User.Identifier IS NULL THEN '""'
		WHEN OR_User.Identifier LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Identifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.Identifier LIKE '%'+NCHAR(10)+'%' OR OR_User.Identifier LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Identifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.Identifier) + '"'
		END
		AS identifier,
	CASE 
		WHEN OR_User.userMasterIdentifier IS NULL THEN '""'
		WHEN OR_User.userMasterIdentifier LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.userMasterIdentifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.userMasterIdentifier LIKE '%'+NCHAR(10)+'%' OR OR_User.userMasterIdentifier LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.userMasterIdentifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.userMasterIdentifier) + '"'
		END
		AS userMasterIdentifier,
	CASE 
		WHEN OR_User.Email IS NULL THEN '""'
		WHEN OR_User.Email LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Email,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.Email LIKE '%'+NCHAR(10)+'%' OR OR_User.Email LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Email,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.Email) + '"'
		END
		AS email,
	(CASE 
			WHEN OR_User.Sms IS NULL THEN ''
			ELSE CONVERT(varchar(255), OR_User.Sms)
			END) AS sms,
	(CASE 
			WHEN Phone IS NULL THEN ''
			ELSE CONVERT(varchar(255), Phone)
			END) AS phone,
	(CASE 
			WHEN OR_User.Agents IS NULL THEN ''
			ELSE CONVERT(varchar(255), OR_User.Agents)
			END) AS agentSourcedIds,
	(CASE 
			WHEN OR_User.Grades IS NULL THEN ''
			ELSE CONVERT(varchar(255), OR_User.Grades)
			END) AS grades,
	CASE 
		WHEN OR_User.Password IS NULL THEN '""'
		WHEN OR_User.Password LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Password,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.Password LIKE '%'+NCHAR(10)+'%' OR OR_User.Password LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.Password,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.Password) + '"'
		END
		AS password,
	CASE 
		WHEN OR_User.KanaGivenName IS NULL THEN '""'
		WHEN OR_User.KanaGivenName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaGivenName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanaGivenName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanaGivenName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaGivenName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanaGivenName) + '"'
		END
		AS [metadata.digitalKoumu.kanaGivenName],
	CASE 
		WHEN OR_User.KanaFamilyName IS NULL THEN '""'
		WHEN OR_User.KanaFamilyName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaFamilyName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanaFamilyName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanaFamilyName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaFamilyName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanaFamilyName) + '"'
		END
		AS [metadata.digitalKoumu.kanaFamilyName],
	CASE 
		WHEN OR_User.KanaMiddleName IS NULL THEN '""'
		WHEN OR_User.KanaMiddleName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanaMiddleName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanaMiddleName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanaMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanaMiddleName) + '"'
		END
		AS [metadata.digitalKoumu.kanaMiddleName],

	CASE 
		WHEN OR_User.userProfiles IS NULL THEN '""'
		WHEN OR_User.userProfiles LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.userProfiles,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.userProfiles LIKE '%'+NCHAR(10)+'%' OR OR_User.userProfiles LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.userProfiles,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.userProfiles) + '"'
		END
		AS userProfiles,
	CASE 
		WHEN OR_User.KanapreferredFirstName IS NULL THEN '""'
		WHEN OR_User.KanapreferredFirstName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredFirstName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanapreferredFirstName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanapreferredFirstName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredFirstName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanapreferredFirstName) + '"'
		END
		AS [metadata.jp.kanaGivenName],
	CASE 
		WHEN OR_User.KanapreferredLastName IS NULL THEN '""'
		WHEN OR_User.KanapreferredLastName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredLastName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanapreferredLastName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanapreferredLastName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredLastName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanapreferredLastName) + '"'
		END
		AS [metadata.jp.kanaFamilyName],
	CASE 
		WHEN OR_User.KanapreferredMiddleName IS NULL THEN '""'
		WHEN OR_User.KanapreferredMiddleName LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN OR_User.KanapreferredMiddleName LIKE '%'+NCHAR(10)+'%' OR OR_User.KanapreferredMiddleName LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(OR_User.KanapreferredMiddleName,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), OR_User.KanapreferredMiddleName) + '"'
		END
		AS [metadata.jp.kanaMiddleName],
	ore.Class AS [metadata.jp.homeClass]
FROM OR_User
	LEFT JOIN OR_UserOrg
	ON  OR_User.SourcedId = OR_UserOrg.[User]
	LEFT JOIN (
        SELECT OR_Enrollment.*
        FROM OR_Enrollment, OR_Class 
        WHERE OR_Enrollment.Class = OR_Class.SourcedId
        AND OR_Class.ClassType = 'homeroom' 
        AND OR_Class.Status    = 'active'
        AND OR_Class.ShozokuId > 0 	
	) ore
	ON  ore.[User] = OR_User.SourcedId
	AND ore.[Role] = OR_User.[Role]
	AND ore.[Role] = 'student' 
WHERE OR_User.Status = 
	CASE 
		WHEN $(ReferenceDateTime) LIKE '' THEN 'active'
		ELSE OR_User.Status
		END
AND OR_User.TenantId = $(TenantId)
AND 1 = 
	CASE
		WHEN $(ReferenceDateTime) LIKE '' THEN 1 -- bulkの時出力
		WHEN OR_User.DateLastModified >= $(ReferenceDateTime) THEN 1 -- deltaでDateLastModified >= $(ReferenceDateTime)のとき出力
		ELSE 0 -- deltaでDateLastModified < $(ReferenceDateTime)のとき出力しない
		END
AND OR_User.deleteFlg != 'TRUE'
) a
ORDER BY 
    CASE [status]
        WHEN 'active'      THEN 1 
        WHEN 'tobedeleted' THEN 2 
        ELSE 3 
    END
    ,orgSourcedIds
    ,CASE [Role] 
        WHEN  'administrator'  THEN 1 
        WHEN  'teacher'        THEN 2 
        WHEN  'student'        THEN 3 
        WHEN  'guardian'       THEN 4 
        ELSE 5 
     END