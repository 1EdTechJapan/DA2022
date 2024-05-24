set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(name) AS name
    ,one.ufnAddQuate(type) AS type
    ,one.ufnAddQuate(identifier) AS identifier
    ,one.ufnAddQuate(parentSourcedId) AS parentSourcedId
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,name
       ,type
       ,identifier
       ,LOWER(CONVERT(varchar(36), parentSourcedId)) AS parentSourcedId
       ,2 AS ord
    FROM one.orgs
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'name', 'type', 'identifier', 'parentSourcedId', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


