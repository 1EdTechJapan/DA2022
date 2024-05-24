set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(title) AS title
    ,one.ufnAddQuate(grades) AS grades
    ,one.ufnAddQuate(courseSourcedId) AS courseSourcedId
    ,one.ufnAddQuate(classCode) AS classCode
    ,one.ufnAddQuate(classType) AS classType
    ,one.ufnAddQuate(location) AS location
    ,one.ufnAddQuate(schoolSourcedId) AS schoolSourcedId
    ,one.ufnAddQuate(termSourcedIds) AS termSourcedIds
    ,one.ufnAddQuate(subjects) AS subjects
    ,one.ufnAddQuate(subjectCodes) AS subjectCodes
    ,one.ufnAddQuate(periods) AS periods
    ,one.ufnAddQuate(metadata_jp_specialNeeds) AS metadata_jp_specialNeeds
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,title
       ,grades
       ,LOWER(CONVERT(varchar(36), courseSourcedId)) AS courseSourcedId
       ,classCode
       ,classType
       ,location
       ,LOWER(CONVERT(varchar(36), schoolSourcedId)) AS schoolSourcedId
       ,LOWER(CONVERT(varchar(36), termSourcedIds)) AS termSourcedIds
       ,subjects
       ,subjectCodes
       ,periods
       ,CASE metadata_jp_specialNeeds WHEN 1 THEN 'true' ELSE 'false' END AS metadata_jp_specialNeeds
       ,2 AS ord
    FROM one.classes
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'title', 'grades', 'courseSourcedId', 'classCode', 'classType',
            'location', 'schoolSourcedId', 'termSourcedIds', 'subjects', 'subjectCodes', 'periods', 'metadata.jp.specialNeeds', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


