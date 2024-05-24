SELECT 
      CONCAT('"', sourcedId,'"')              AS sourcedId
    , CONCAT('"', status,'"')                 AS status
    , CONCAT('"', dateLastModified,'"')       AS dateLastModified
     --
    , CONCAT('"', userSourcedId        ,'"')  AS userSourcedId        
    , CONCAT('"', roleType             ,'"')  AS roleType             
    , CONCAT('"', role                 ,'"')  AS role                 
    , CONCAT('"', beginDate            ,'"')  AS beginDate            
    , CONCAT('"', endDate              ,'"')  AS endDate              
    , CONCAT('"', orgSourcedId         ,'"')  AS orgSourcedId         
    , CONCAT('"', userProfileSourcedId ,'"')  AS userProfileSourcedId 
FROM(
SELECT
     [SourcedId] AS sourcedId

    ,CASE 
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE Status
     END AS status


    ,CASE
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE FORMAT(DateLastModified,'yyyy-MM-ddTHH:mm:ss.fffZ')
     END AS dateLastModified

    ,[User]                                   AS userSourcedId
    ,[roleType]                               AS roleType
    ,[role]                                   AS role
    ,FORMAT(StartDate,'yyyy-MM-dd')           AS beginDate
    ,FORMAT(EndDate,'yyyy-MM-dd')             AS endDate
    ,[Org]                                    AS orgSourcedId
    ,[UserProfiles]                           AS userProfileSourcedId
FROM OR_USERROLE

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


