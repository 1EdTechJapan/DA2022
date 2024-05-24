SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
    , title                                   AS title
    , CONCAT('"', grades,'"')                 AS grades
    , CONCAT('"', courseSourcedId,'"')        AS courseSourcedId
    , CONCAT('"', classCode,'"')              AS classCode
    , CONCAT('"', classType,'"')              AS classType
    , location                                AS location
    , CONCAT('"', schoolSourcedId,'"')        AS schoolSourcedId
    , CONCAT('"', termSourcedIds,'"')         AS termSourcedIds
    , subjects                                AS subjects
    , CONCAT('"', subjectCodes,'"')           AS subjectCodes
    , CONCAT('"', periods,'"')                AS periods
    , CONCAT('"', [metadata.jp.specialNeeds],'"')   AS [metadata.jp.specialNeeds]
FROM (
SELECT SourcedId AS sourcedId,
	CASE 
		WHEN $(ReferenceDateTime) LIKE '' THEN ''
		ELSE Status
		END
		AS status,
	CASE
		WHEN $(ReferenceDateTime) LIKE '' THEN ''
		ELSE FORMAT(DateLastModified,'yyyy-MM-ddTHH:mm:ss.fffZ')
		END
		AS dateLastModified,
	CASE 
		WHEN Title IS NULL THEN '""'
		WHEN Title LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(Title,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
				WHEN Title LIKE '%'+NCHAR(10)+'%' OR Title LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(Title,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), Title) + '"'
		END
		AS title,
	CASE 
	WHEN	(
	        CASE Taisho1Flg WHEN 1 THEN 'P1,' ELSE '' END +
			CASE Taisho2Flg WHEN 1 THEN 'P2,' ELSE '' END +
			CASE Taisho3Flg WHEN 1 THEN 'P3,' ELSE '' END +
			CASE Taisho4Flg WHEN 1 THEN 'P4,' ELSE '' END +
			CASE Taisho5Flg WHEN 1 THEN 'P5,' ELSE '' END +
			CASE Taisho6Flg WHEN 1 THEN 'P6,' ELSE '' END +
			CASE Taisho7Flg WHEN 1 THEN 'J1,' ELSE '' END +
			CASE Taisho8Flg WHEN 1 THEN 'J2,' ELSE '' END +
			CASE Taisho9Flg WHEN 1 THEN 'J3,' ELSE '' END ) LIKE '%,%,'
	THEN	
	SUBSTRING(
			(
			CASE Taisho1Flg WHEN 1 THEN 'P1,' ELSE '' END +
			CASE Taisho2Flg WHEN 1 THEN 'P2,' ELSE '' END +
			CASE Taisho3Flg WHEN 1 THEN 'P3,' ELSE '' END +
			CASE Taisho4Flg WHEN 1 THEN 'P4,' ELSE '' END +
			CASE Taisho5Flg WHEN 1 THEN 'P5,' ELSE '' END +
			CASE Taisho6Flg WHEN 1 THEN 'P6,' ELSE '' END +
			CASE Taisho7Flg WHEN 1 THEN 'J1,' ELSE '' END +
			CASE Taisho8Flg WHEN 1 THEN 'J2,' ELSE '' END +
			CASE Taisho9Flg WHEN 1 THEN 'J3,' ELSE '' END ) 
			,1,
			(LEN(
			CASE Taisho1Flg WHEN 1 THEN 'P1,' ELSE '' END +
			CASE Taisho2Flg WHEN 1 THEN 'P2,' ELSE '' END +
			CASE Taisho3Flg WHEN 1 THEN 'P3,' ELSE '' END +
			CASE Taisho4Flg WHEN 1 THEN 'P4,' ELSE '' END +
			CASE Taisho5Flg WHEN 1 THEN 'P5,' ELSE '' END +
			CASE Taisho6Flg WHEN 1 THEN 'P6,' ELSE '' END +
			CASE Taisho7Flg WHEN 1 THEN 'J1,' ELSE '' END +
			CASE Taisho8Flg WHEN 1 THEN 'J2,' ELSE '' END +
			CASE Taisho9Flg WHEN 1 THEN 'J3,' ELSE '' END )
			)-1
			)
		ELSE 
			(
			CASE Taisho1Flg WHEN 1 THEN 'P1' ELSE '' END +
			CASE Taisho2Flg WHEN 1 THEN 'P2' ELSE '' END +
			CASE Taisho3Flg WHEN 1 THEN 'P3' ELSE '' END +
			CASE Taisho4Flg WHEN 1 THEN 'P4' ELSE '' END +
			CASE Taisho5Flg WHEN 1 THEN 'P5' ELSE '' END +
			CASE Taisho6Flg WHEN 1 THEN 'P6' ELSE '' END +
			CASE Taisho7Flg WHEN 1 THEN 'J1' ELSE '' END +
			CASE Taisho8Flg WHEN 1 THEN 'J2' ELSE '' END +
			CASE Taisho9Flg WHEN 1 THEN 'J3' ELSE '' END ) 
		END
			AS grades,
	Course AS courseSourcedId,
	(CASE 
			WHEN ClassCode IS NULL THEN ''
			ELSE CONVERT(nvarchar(255), ClassCode)
			END) AS classCode,
	ClassType AS classType,
	CASE 
		WHEN Location IS NULL THEN '""'
		WHEN Location LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(Location,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
				WHEN Location LIKE '%'+NCHAR(10)+'%' OR Location LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(Location,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), Location) + '"'
		END
		AS location,
	School AS schoolSourcedId,
	SchoolYear AS termSourcedIds,
	CASE 
		WHEN Subjects IS NULL THEN '""'
		WHEN Subjects LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(Subjects,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN Subjects LIKE '%'+NCHAR(10)+'%' OR Subjects LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(Subjects,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), Subjects) + '"'
		END
		AS subjects,
	(CASE 
			WHEN SubjectCodes IS NULL THEN ''
			WHEN SubjectCodes ='0'    THEN ''
			ELSE CONVERT(nvarchar(255), SubjectCodes)
			END) AS subjectCodes,
	(CASE 
			WHEN Periods IS NULL THEN ''
			ELSE CONVERT(nvarchar(255), Periods)
			END) AS periods,
	(CASE 
			WHEN SpecialNeedsFlg = 1 THEN 'true'
			WHEN SpecialNeedsFlg = 0 THEN 'false'
			END) AS [metadata.jp.specialNeeds]
FROM OR_Class
WHERE Status = 
	CASE 
		WHEN $(ReferenceDateTime) LIKE '' THEN 'active'
		ELSE Status
		END
AND TenantId = $(TenantId)
AND 1 = 
	CASE
		WHEN $(ReferenceDateTime) LIKE '' THEN 1 -- bulkの時出力
		WHEN DateLastModified >= $(ReferenceDateTime) THEN 1 -- deltaでDateLastModified >= $(ReferenceDateTime)のとき出力
		ELSE 0 -- deltaでDateLastModified < $(ReferenceDateTime)のとき出力しない
		END
AND deleteFlg != 'TRUE'
) a
ORDER BY 
    CASE [status]
        WHEN 'active'      THEN 1 
        WHEN 'tobedeleted' THEN 2 
        ELSE 3 
    END
    ,termSourcedIds
    ,schoolSourcedId
    ,classType
    ,subjectCodes
    ,grades
    ,[Title]