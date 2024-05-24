set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(title) AS title
    ,one.ufnAddQuate(type) AS type
    ,one.ufnAddQuate(startDate) AS startDate
    ,one.ufnAddQuate(endDate) AS endDate
    ,one.ufnAddQuate(parentSourcedId) AS parentSourcedId 
    ,one.ufnAddQuate(schoolYear) AS schoolYear
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,title
       ,type
       ,CAST(startDate AS varchar(10)) AS startDate
       ,CAST(endDate AS varchar(10)) AS endDate
       --,CONVERT(varchar(36), parentSourcedId) AS parentSourcedId
       ,'NULL' AS parentSourcedId --2023/2/17の右記のコンソール修正に追従 → 必須項目かつ、固定値でNULL（空文字ではなく、NULLという文字列）であるチェックに修正しました。
       ,schoolYear
       ,2 AS ord
    FROM one.academicSessions
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'title', 'type', 'startDate', 'endDate', 'parentSourcedId', 'schoolYear', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO
