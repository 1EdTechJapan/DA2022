set nocount on

DECLARE @T_Data TABLE(prop varchar(100), val varchar(100), itemOrd tinyint)
INSERT @T_Data
VALUES
    ('manifest.version','1.0', 1)
   ,('oneroster.version','1.2', 2)
   ,('file.academicSessions','bulk', 3)
   ,('file.categories','absent', 4)
   ,('file.classes','bulk', 5)
   ,('file.classResources','absent', 6)
   ,('file.courses','bulk', 7)
   ,('file.courseResources','absent', 8)
   ,('file.demographics','absent', 9)
   ,('file.enrollments','bulk', 10)
   ,('file.lineItemLearningObjectiveIds','absent', 11)
   ,('file.lineItems','absent', 12)
   ,('file.lineItemScoreScales','absent', 13)
   ,('file.orgs','bulk', 14)
   ,('file.resources','absent', 15)
   ,('file.resultLearningObjectiveIds','absent', 16)
   ,('file.results','absent', 17)
   ,('file.resultScoreScales','absent', 18)
   ,('file.roles','bulk', 19)
   ,('file.scoreScales','absent', 20)
   ,('file.userProfiles','absent', 21)
--    ,('file.userProfiles','bulk', 21) --テストコンソールの不具合により、暫定的にbulkとする [2023/2/24]テストコンソールが修正されたためabsentに戻る
   ,('file.userResources','absent', 22)
   ,('file.users','bulk', 23)

SELECT
     prop AS sourcedId
    ,val AS status
FROM
   (
    --出力データ
    SELECT
        one.ufnAddQuate(prop) AS prop
       ,one.ufnAddQuate(val) AS val
       ,2 AS ord
       ,itemOrd
    FROM
       @T_Data
    UNION ALL
    --CSVヘッダ用
    SELECT
        col1, col2, ord, itemOrd
    FROM
       (VALUES(
            'propertyName', 'value', 1, 0
            )
        ) Header (col1, col2, ord, itemOrd)
    ) Bas
ORDER BY
    ord, itemOrd

set nocount off;
GO
