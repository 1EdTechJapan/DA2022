SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
    , name                                    AS [name]
    , CONCAT('"', [type],'"')                 AS [type]
    , identifier                              AS identifier
    , CONCAT('"', parentSourcedId,'"')        AS parentSourcedId
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
		WHEN Name IS NULL THEN '""'
		WHEN Name LIKE '%"%' THEN '"'+ REPLACE(REPLACE(REPLACE(Name,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10)),'"','""""') + '"'
		WHEN Name LIKE '%'+NCHAR(10)+'%' OR Name LIKE '%'+NCHAR(13)+'%' THEN '"' + REPLACE(REPLACE(Name,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10)) + '"'
		ELSE '"' + Name + '"'
		END
		AS name,
	Type AS type,
	CASE 
		WHEN Identifier IS NULL THEN '""'
		WHEN Identifier LIKE '%"%' THEN '"'+ REPLACE(CONVERT(nvarchar(255), REPLACE(REPLACE(Identifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))),'"','""""') + '"'
		WHEN Identifier LIKE '%'+NCHAR(10)+'%' OR Identifier LIKE '%'+NCHAR(13)+'%' THEN '"' + CONVERT(nvarchar(255), REPLACE(REPLACE(Identifier,NCHAR(13)+NCHAR(10),NCHAR(10)),NCHAR(13),NCHAR(10))) + '"'
		ELSE '"' + CONVERT(nvarchar(255), Identifier) + '"'
		END
		AS identifier,
	CASE 
		WHEN Parent IS NULL THEN ''
		ELSE CONVERT(nvarchar(255), Parent)
		END AS parentSourcedId,
	DantaiId AS DantaiId
FROM OR_Org
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
    ,identifier