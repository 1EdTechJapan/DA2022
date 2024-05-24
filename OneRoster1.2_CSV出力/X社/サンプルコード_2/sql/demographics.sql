SELECT 
      CONCAT('"', sourcedId                             ,'"')     AS sourcedId
    , CONCAT('"', status                                ,'"')     AS status
    , CONCAT('"', dateLastModified                      ,'"')     AS dateLastModified
      -- 
    , CONCAT('"', birthDate                             ,'"')     AS birthDate
    , CONCAT('"', [sex]                                 ,'"')     AS [sex]
    , CONCAT('"', americanIndianOrAlaskaNative          ,'"')     AS americanIndianOrAlaskaNative         
    , CONCAT('"', asian                                 ,'"')     AS asian                                
    , CONCAT('"', blackOrAfricanAmerican                ,'"')     AS blackOrAfricanAmerican               
    , CONCAT('"', nativeHawaiianOrOtherPacificIslander  ,'"')     AS nativeHawaiianOrOtherPacificIslander 
    , CONCAT('"', white                                 ,'"')     AS white                                
    , CONCAT('"', demographicRaceTwoOrMoreRaces         ,'"')     AS demographicRaceTwoOrMoreRaces        
    , CONCAT('"', hispanicOrLatinoEthnicity             ,'"')     AS hispanicOrLatinoEthnicity            
    , CONCAT('"', countryOfBirthCode                    ,'"')     AS countryOfBirthCode                   
    , CONCAT('"', stateOfBirthAbbreviation              ,'"')     AS stateOfBirthAbbreviation             
    , CONCAT('"', cityOfBirth                           ,'"')     AS cityOfBirth                          
    , CONCAT('"', publicSchoolResidenceStatus           ,'"')     AS publicSchoolResidenceStatus          
FROM(
SELECT
     OR_Demographics.[User] AS [sourcedId]

    ,CASE 
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE Status
    END AS status


    ,CASE
        WHEN $(ReferenceDateTime) LIKE '' THEN ''
        ELSE FORMAT(DateLastModified,'yyyy-MM-ddTHH:mm:ss.fffZ')
     END AS dateLastModified

    ,FORMAT(OR_Demographics.BirthDate,'yyyy-MM-dd') AS birthDate
  
    ,CASE
        WHEN OR_Demographics.[Sex] = '1' THEN 'male'
        WHEN OR_Demographics.[Sex] = '2' THEN 'female'
        ELSE 'unspecified'
     END AS [sex]
    ,CASE americanIndianOrAlaskaNative             
        WHEN '0' THEN ''
        ELSE '1'
     END AS  americanIndianOrAlaskaNative
    ,CASE asian                                    
        WHEN '0' THEN ''
        ELSE '1'
     END AS  asian
    ,CASE blackOrAfricanAmerican                   
        WHEN '0' THEN ''
        ELSE '1'
     END AS  blackOrAfricanAmerican
    ,CASE nativeHawaiianOrOtherPacificIslander     
        WHEN '0' THEN ''
        ELSE '1'
     END AS  nativeHawaiianOrOtherPacificIslander
    ,CASE white                                    
        WHEN '0' THEN ''
        ELSE '1'
     END AS  white
    ,CASE demographicRaceTwoOrMoreRaces            
        WHEN '0' THEN ''
        ELSE '1'
     END AS  demographicRaceTwoOrMoreRaces
    ,CASE hispanicOrLatinoEthnicity                
        WHEN '0' THEN ''
        ELSE '1'
     END AS  hispanicOrLatinoEthnicity
    ,countryOfBirthCode                       
    ,stateOfBirthAbbreviation                 
    ,cityOfBirth                              
    ,publicSchoolResidenceStatus              
FROM OR_Demographics

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

