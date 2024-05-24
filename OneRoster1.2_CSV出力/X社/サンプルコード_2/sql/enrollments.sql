SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
    , CONCAT('"', classSourcedId,'"')         AS classSourcedId
    , CONCAT('"', schoolSourcedId,'"')        AS schoolSourcedId
    , CONCAT('"', userSourcedId,'"')          AS userSourcedId
    , CONCAT('"', role,'"')                   AS role
    , CONCAT('"', [primary],'"')              AS [primary]
    , CONCAT('"', beginDate,'"')              AS beginDate
    , CONCAT('"', endDate,'"')                AS endDate
    , [metadata.jp.ShussekiNo]                AS  [metadata.jp.ShussekiNo]
    , CONCAT('"', [metadata.jp.PublicFlg],'"') AS  [metadata.jp.PublicFlg]
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
	Class AS classSourcedId,
	School AS schoolSourcedId,
	[User] AS userSourcedId,
	Role AS role,
	(CASE 
			WHEN [Primary] IS NULL THEN ''
			WHEN [Primary] = 1 THEN 'true'
			WHEN [Primary] = 0 THEN 'false'
			END) AS [primary],
	FORMAT(BeginDate,'yyyy-MM-dd') AS beginDate,
	(CASE 
			WHEN EndDate IS NULL THEN ''
			ELSE FORMAT(EndDate,'yyyy-MM-dd')
			END) AS endDate,
	CASE 
		WHEN StudentCode IS NULL THEN '""'
		WHEN StudentCode LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(StudentCode,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN StudentCode LIKE '%'+NCHAR(10)+'%' OR StudentCode LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(StudentCode,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		WHEN StudentCode LIKE '%,%' THEN '"' + CONVERT(nvarchar(255), StudentCode) + '"'
		ELSE '"' + CONVERT(nvarchar(255), StudentCode) + '"'
		END
		AS [metadata.jp.ShussekiNo],
	'true' AS [metadata.jp.PublicFlg]
FROM OR_Enrollment
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
    ,schoolSourcedId
    ,userSourcedId
    ,CASE [Role] 
        WHEN  'administrator'  THEN 1 
        WHEN  'teacher'        THEN 2 
        WHEN  'student'        THEN 3 
        WHEN  'guardian'       THEN 4 
        ELSE 5 
     END
    ,classSourcedId