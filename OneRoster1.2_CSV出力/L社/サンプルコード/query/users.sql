set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(enabledUser) AS enabledUser
    ,one.ufnAddQuate(username) AS username
    ,one.ufnAddQuate(userIds) AS userIds
    ,one.ufnAddQuate(givenName) AS givenName
    ,one.ufnAddQuate(familyName) AS familyName
    ,one.ufnAddQuate(middleName) AS middleName
    ,one.ufnAddQuate(identifier) AS identifier
    ,one.ufnAddQuate(email) AS email
    ,one.ufnAddQuate(sms) AS sms
    ,one.ufnAddQuate(phone) AS phone
    ,one.ufnAddQuate(agentSourcedIds) AS agentSourcedIds
    ,one.ufnAddQuate(grades) AS grades
    ,one.ufnAddQuate(password) AS password
    ,one.ufnAddQuate(userMasterIdentifier) AS userMasterIdentifier
    ,one.ufnAddQuate(resourceSourcedIds) AS resourceSourcedIds
    ,one.ufnAddQuate(preferredGivenName) AS preferredGivenName
    ,one.ufnAddQuate(preferredMiddleName) AS preferredMiddleName
    ,one.ufnAddQuate(preferredFamilyName) AS preferredFamilyName
    ,one.ufnAddQuate(primaryOrgSourcedId) AS primaryOrgSourcedId
    ,one.ufnAddQuate(pronouns) AS pronouns
    ,one.ufnAddQuate(metadata_jp_kanaGivenName) AS metadata_jp_kanaGivenName
    ,one.ufnAddQuate(metadata_jp_kanaFamilyName) AS metadata_jp_kanaFamilyName
    ,one.ufnAddQuate(metadata_jp_kanaMiddleName) AS metadata_jp_kanaMiddleName
    ,one.ufnAddQuate(metadata_jp_homeClass) AS metadata_jp_homeClass
FROM
   (
    --出力データ
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,CASE enabledUser WHEN 1 THEN 'true' ELSE 'false' END AS enabledUser
       ,username
       ,userIds
       ,givenName
       ,familyName
       ,middleName
       ,identifier
       ,email
       ,sms
       ,phone
       ,LOWER(CONVERT(varchar(36), agentSourcedIds)) AS agentSourcedIds
       ,grades
       ,password
    --    ,CONVERT(varchar(36), userMasterIdentifier) AS userMasterIdentifier
       ,LOWER(NEWID()) AS userMasterIdentifier -- userMasterIdentifierは校務支援システムで生成されたUUID(v4)を用いる。
       ,resourceSourcedIds
       ,preferredGivenName
       ,preferredMiddleName
       ,preferredFamilyName
       ,LOWER(CONVERT(varchar(36), primaryOrgSourcedId)) AS primaryOrgSourcedId
       ,pronouns
       ,metadata_jp_kanaGivenName
       ,metadata_jp_kanaFamilyName
       ,metadata_jp_kanaMiddleName
       ,LOWER(CONVERT(varchar(36), metadata_jp_homeClass)) AS metadata_jp_homeClass
       ,2 AS ord
    FROM one.users
    --Users.metadata.jp.homeClassがブランクのレコードはテストコンソールで弾かれるため、metadata.jp.homeClass未設定のレコードは除外する
    --  2023/2/24テストコンソールが修正されたため、暫定対応として記載していたWHERE句はコメントアウト
    -- WHERE metadata_jp_homeClass IS NOT NULL
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
        col11, col12, col13, col14, col15, col16, col17, col18, col19, col20,
        col21, col22, col23, col24, col25, col26, col27, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'enabledUser', 'username', 'userIds', 'givenName', 'familyName', 'middleName', 'identifier',
            'email', 'sms', 'phone', 'agentSourcedIds', 'grades', 'password', 'userMasterIdentifier', 'resourceSourcedIds', 'preferredGivenName',
            'preferredMiddleName', 'preferredFamilyName', 'primaryOrgSourcedId', 'pronouns', 'metadata.jp.kanaGivenName',
            'metadata.jp.kanaFamilyName', 'metadata.jp.kanaMiddleName', 'metadata.jp.homeClass', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
                  col11, col12, col13, col14, col15, col16, col17, col18, col19, col20,
                  col21, col22, col23, col24, col25, col26, col27, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


