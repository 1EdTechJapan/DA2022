set nocount on

SELECT
     one.ufnAddQuate(sourcedId) AS sourcedId
    ,one.ufnAddQuate(status) AS status
    ,one.ufnAddQuate(dateLastModified) AS dateLastModified
    ,one.ufnAddQuate(userSourcedId) AS userSourcedId
    ,one.ufnAddQuate(roleType) AS roleType
    ,one.ufnAddQuate(role) AS role
    ,one.ufnAddQuate(beginDate) AS beginDate
    ,one.ufnAddQuate(endDate) AS endDate
    ,one.ufnAddQuate(orgSourcedId) AS orgSourcedId
    ,one.ufnAddQuate(userProfileSourcedId) AS userProfileSourcedId
FROM
   (
    --�o�̓f�[�^
    SELECT
        LOWER(CONVERT(varchar(36), sourcedId)) AS sourcedId
       ,status
       ,CONVERT(varchar(30), dateLastModified, 127) AS dateLastModified
       ,LOWER(CONVERT(varchar(36), userSourcedId)) AS userSourcedId
       ,roleType
       ,role
       ,CONVERT(varchar(10), beginDate) AS beginDate
       ,CONVERT(varchar(10), endDate) AS endDate
       ,LOWER(CONVERT(varchar(36), orgSourcedId)) AS orgSourcedId
       ,LOWER(CONVERT(varchar(36), userProfileSourcedId)) AS userProfileSourcedId
       ,2 AS ord
    FROM one.roles
    --Users.metadata.jp.homeClass���u�����N�̃��R�[�h�̓e�X�g�R���\�[���Œe����邽�߁Ametadata.jp.homeClass���ݒ�̃��R�[�h�͏��O����
    --  2023/2/24�e�X�g�R���\�[�����C�����ꂽ���߁A�b��Ή��Ƃ��ċL�ڂ��Ă���WHERE��̓R�����g�A�E�g
    -- WHERE
    --     EXISTS(SELECT * FROM one.Users U WHERE U.metadata_jp_homeClass IS NOT NULL AND U.sourcedId = userSourcedId)
    UNION ALL
    --CSV�w�b�_�p
    SELECT
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, ord
    FROM
       (VALUES(
            'sourcedId', 'status', 'dateLastModified', 'userSourcedId', 'roleType', 'role', 'beginDate', 'endDate', 'orgSourcedId', 'userProfileSourcedId', 1
            )
        ) Header (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, ord)
    ) Bas
ORDER BY
    ord

set nocount off;
GO


