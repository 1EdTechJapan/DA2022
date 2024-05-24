set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(classSourcedId) AS classSourcedId
    ,one.ufnAddQuate(schoolSourcedId) AS schoolSourcedId
    ,one.ufnAddQuate(userSourcedId) AS userSourcedId
    ,one.ufnAddQuate(role) AS role
    ,one.ufnAddQuate([primary]) AS [primary]
    ,one.ufnAddQuate(beginDate) AS beginDate
    ,one.ufnAddQuate(endDate) AS endDate
    ,one.ufnAddQuate(metadata_jp_ShussekiNo) AS [metadata.jp.ShussekiNo]
    ,one.ufnAddQuate(metadata_jp_PublicFlg) AS [metadata.jp.PublicFlg]
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,LOWER(CONVERT(varchar(36), classSourcedId)) AS classSourcedId
       ,LOWER(CONVERT(varchar(36), schoolSourcedId)) AS schoolSourcedId
       ,LOWER(CONVERT(varchar(36), userSourcedId)) AS userSourcedId
       ,role
       ,CASE [primary] WHEN 1 then 'true' ELSE 'false' END AS [primary]
       ,CONVERT(varchar(10), beginDate) AS beginDate
       ,CONVERT(varchar(10), endDate) AS endDate
       ,CONVERT(varchar(10), metadata_jp_ShussekiNo) AS metadata_jp_ShussekiNo
       ,CASE metadata_jp_PublicFlg WHEN 1 then 'true' ELSE 'false' END AS metadata_jp_PublicFlg
       ,2 AS ord
    FROM one.enrollments
    --Users.metadata.jp.homeClassがブランクのレコードはテストコンソールで弾かれるため、metadata.jp.homeClass未設定のレコードは除外する
    --  2023/2/24テストコンソールが修正されたため、暫定対応として記載していたWHERE句はコメントアウト
    -- WHERE
    --     EXISTS(SELECT * FROM one.Users U WHERE U.metadata_jp_homeClass IS NOT NULL AND U.sourcedId = userSourcedId)
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'classSourcedId', 'schoolSourcedId', 'userSourcedId', 'role', 'primary', 'beginDate', 'endDate', 'metadata.jp.ShussekiNo', 'metadata.jp.PublicFlg', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


