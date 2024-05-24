SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
    , title                                   AS title
    , CONCAT('"', [type],'"')                 AS [type]
    , CONCAT('"', startDate,'"')              AS startDate
    , CONCAT('"', endDate,'"')                AS endDate
    , CONCAT('"', parentSourcedId,'"')        AS parentSourcedId
    , CONCAT('"', schoolYear,'"')             AS schoolYear
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
		WHEN Title LIKE '%"%' THEN '"'+ REPLACE(REPLACE(REPLACE(Title,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10)),'"','""""') + '"'
		WHEN Title LIKE '%'+NCHAR(10)+'%' OR Title LIKE '%'+NCHAR(13)+'%' THEN '"' + REPLACE(REPLACE(Title,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10)) + '"'
		ELSE '"' + Title + '"'
		END
		 AS title,
		 Type AS type,
	FORMAT(StartDate,'yyyy-MM-dd') AS startDate,
	FORMAT(EndDate,'yyyy-MM-dd') AS endDate,
	(CASE 
			WHEN Parent IS NULL THEN 'NULL'
			ELSE CONVERT(nvarchar(255), Parent)
			END) AS parentSourcedId,
	SchoolYear AS schoolYear
FROM OR_AcademicSession
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
    ,[type]
    ,schoolYear
    ,startDate