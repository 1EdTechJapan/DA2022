SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
      -- 
    , CONCAT('"', userSourcedId  ,'"')        AS userSourcedId
    , CONCAT('"', profileType    ,'"')        AS profileType
    , CONCAT('"', vendorId       ,'"')        AS vendorId
    , CONCAT('"', applicationId  ,'"')        AS applicationId
    , CONCAT('"', description    ,'"')        AS description
    , CONCAT('"', credentialType ,'"')        AS credentialType
    , CONCAT('"', username       ,'"')        AS username
    , CONCAT('"', password       ,'"')        AS password
FROM(
SELECT
     OR_Userprofile.[SourcedId] AS sourcedId

    ,CASE 
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE Status
     END AS status


    ,CASE
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE FORMAT(DateLastModified,'yyyy-MM-ddTHH:mm:ss.fffZ')
     END AS dateLastModified

    ,OR_Userprofile.[User] AS userSourcedId
    ,OR_Userprofile.[ProfileType] AS profileType
    ,OR_Userprofile.[venderID] AS vendorId
    ,OR_Userprofile.[applicationId] AS applicationId
    ,OR_Userprofile.[description] AS description
    ,OR_Userprofile.[credentialType] AS credentialType
    ,OR_Userprofile.[username] AS username
    ,OR_Userprofile.[password] AS password
FROM OR_Userprofile

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

