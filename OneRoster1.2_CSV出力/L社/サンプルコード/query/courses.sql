set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(schoolYearSourcedId) AS schoolYearSourcedId
    ,one.ufnAddQuate(title) AS title
    ,one.ufnAddQuate(courseCode) AS courseCode
    ,one.ufnAddQuate(grades) AS grades
    ,one.ufnAddQuate(orgSourcedId) AS orgSourcedId
    ,one.ufnAddQuate(subjects) AS subjects
    ,one.ufnAddQuate(subjectCodes) AS subjectCodes
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,LOWER(CONVERT(varchar(36), schoolYearSourcedId)) AS schoolYearSourcedId
       ,title
       ,courseCode
       ,grades
       ,LOWER(CONVERT(varchar(36), orgSourcedId)) AS orgSourcedId
       ,subjects
       ,subjectCodes
       ,2 AS ord
    FROM one.courses
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'schoolYearSourcedId', 'title', 'courseCode', 'grades', 'orgSourcedId', 'subjects', 'subjectCodes', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


