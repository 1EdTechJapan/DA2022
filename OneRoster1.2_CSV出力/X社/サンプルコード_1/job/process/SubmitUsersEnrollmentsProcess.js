import moment from 'moment';
import { v4 as uuidv4 } from "uuid";
import config from "../../config/config.js";
import {db} from "../../models/index.js";
import lang from '../../i18n.js';
import redisClient from "../../redisClient.js";
import {
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PROCESSING,
    STATUS_WAITING,
    DEFAULT_USERS_STATUS,
    USER_DEFAULT_PASSWORD,
    CLASS_ATENDANCE_COLLATION,
    LOG_TYPE_SUBMIT_MATCHING
} from "../../constants/constans.js";
import e from 'cors';
import { excludeArrayValue, mappingQueryArrayReturn, convertNullToString, convertDateForInsert, filterUsersSubmitSetting, setPasswordRule } from '../../helpers/utility.js';
import LogHelper from "../../helpers/log.js";
const LOG = new LogHelper(CLASS_ATENDANCE_COLLATION);

const Op = db.Master.Sequelize.Op;

/**
 * Process to splits the inputArray into new array pieces
 * @constructor
 */
const arrayChunk = (inputArray,perChunk) => {
    return inputArray?.reduce((resultArray, item, index) => { 
        const chunkIndex = Math.floor(index/perChunk)
        
        if(!resultArray[chunkIndex]) {
            resultArray[chunkIndex] = [] // start a new chunk
        }
        
        resultArray[chunkIndex].push(item)
        
        return resultArray
    }, [])
}

/**
 * Suspend the process of a function
 * @constructor
 */
const sleep = (ms) => {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
} 

/**
 * Process to update field 'status' becomes 'tobedeleted' on enrollments table
 * @constructor
 */
const tobedeletedChild = async (user_ids, municipalId) => {
    await Promise.all(
        user_ids.map( async (user_id) => {

        await db[municipalId].enrollments.update({
          status : 'tobedeleted',
          dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
        },{
          where : {
            userSourcedId : user_id
          }
        })
    })
  )
}

const attr = [
    "id",
    "uuid",
    "sourcedId",
    "status",
    "dateLastModified",
    "enabledUser",
    "orgSourcedIds",
    "role",
    "username",
    "userIds",
    "givenName",
    "familyName",
    "middleName",
    "identifier",
    "email",
    "sms",
    "phone",
    "agentSourcedIds",
    "grades",
    "password",
    "municipalId",
    "yearId",
    "metadataJpKanaGivenName",
    "metadataJpKanaFamilyName",
    "metadataJpKanaMiddleName",
    "metadataJpHomeClass",
  ];

let step = ['import_table_update','update_tobedeleted','count_all_data_import','import_merge_data']
// let step = ['count_all_data_import']

/**
 * Processing bull job for submited data from submit user class enrollment import process
 * @constructor
 */
class SubmitUsersEnrollments {
    onProcess = async (job,done,initData = null,stepIndex=0, limit=100, offset=0) => {
        const param = job.data

        if(!initData){
            initData = {
                bulkDeleteCsv : [],
                data : [],
                importCsvDataAll : 0,
                progress : 0,
                percent : 0,
                logData : {},
                startInsertTime : moment(),
                insertTime : 0,
            }
        }

        let bulkDeleteCsv = [];
        let bulkDeleteEnrCsv = [];
        let bulkDeleteEnrLgate = [];
        let bulkDeleteEnrData = [];
        let data;
        let paramCsv = [];
        let importSubmited = [];
        let lgateSubmit = [];
        let rowstart = 0;
        let rowend = 0;

        let enrollmentRolesName = {
            administrator: "学校管理者",
            student: "児童生徒",
            teacher: "教員",
        };

        switch(step[stepIndex]){
            case 'import_table_update': 
            initData.startInsertTime = moment()
            
                let importData = param.data
                //cek enrollment user

                //insert enrollment for option add_from_lgate
                const importDataEnroll = [];
                const getUserSourcedId = [];
                const importUpdateData = importData.map((item) => {
                  if (getUserSourcedId.findIndex(val => val === item.sourcedId) < 0) {
                    getUserSourcedId.push(item.sourcedId);
                  }
                  let data = JSON.parse(JSON.stringify(item));

                  if (data.option == "skip_csv_to_lgate" && data.option_init === "add_from_lgate") {
                    data = JSON.parse(JSON.stringify({ ...item, ...item.lgate_data }));
                    data.option = "delete_add_from_lgate";
                  }
                  if (!data.option_init) {
                    data.option_init = data.optionInit;
                  }

                  data.submited = 0
                  data.isDelta = 0
                  data.password = item?.newPassword || data.password
                  data.username = item?.newUsername || data.username
                  if (data.option === 'add_from_lgate') {
                    importDataEnroll.push(data.userIdLgate);
                  }
                  return data;
                });

                //get enroll for user
                const getUserEnroll = await db[param.municipalId].importEnrollments.findAll({
                    where: {
                        userSourcedId: { [Op.in]: getUserSourcedId },
                    },
                }).then((item) => {
                    return item
                })

                //update import enrollment
                const updateUserEnroll = [];
                getUserEnroll.map((item,index) => {
                    const findIdxUserData = importUpdateData.findIndex((val) => val.sourcedId === item.userSourcedId && val.classSourcedId === item.classSourcedId);

                    if (findIdxUserData >= 0) {
                        const userOption = importUpdateData[findIdxUserData].option === 'skip_csv_to_lgate' || importUpdateData[findIdxUserData].option === 'delete_add_from_lgate' ? 'skip_csv_to_lgate' : 'update_csv_to_lgate';

                        if (userOption != item.option) {
                            updateUserEnroll.push({
                                sourcedId: item.sourcedId,
                                status: item.status,
                                dateLastModified: item.dateLastModified,
                                classSourcedId: item.classSourcedId,
                                schoolSourcedId: item.schoolSourcedId,
                                userSourcedId: item.userSourcedId,
                                role: item.role,
                                primary: item.primary,
                                beginDate: item.beginDate,
                                endDate: item.endDate,
                                metadataJpShussekiNo: item.metadataJpShussekiNo,
                                metadataJpPublicFlag: item.metadataJpPublicFlag,
                                municipalId: item.municipalId,
                                submited: 0,
                                isDelta: item.isDelta,
                                option: userOption
                            });
                            
                            getUserEnroll[index].option = userOption;
                        }
                    }
                })
                
                if (updateUserEnroll.length) {
                    await db[param.municipalId].importEnrollments.bulkCreate(updateUserEnroll, { updateOnDuplicate: ['option','submited'] })
                }

                getUserSourcedId.map(item => {
                    const totalActiveEnrollment = getUserEnroll.filter(val => val.userSourcedId === item && val.option != 'skip_csv_to_lgate');
                    importUpdateData.map((val, idx) => {
                        if (val.sourcedId === item && (val.option === 'skip_csv_to_lgate' || val.option === 'delete_add_from_lgate')) {
                            importUpdateData[idx].option = totalActiveEnrollment.length > 0 ? val.option_init : val.option;
                        }
                    });
                })

                //get enroll from master table
                if (importDataEnroll.length) {
                    const getDataEnrollQuery = `
                        SELECT 
                            enrollments.*,
                            GROUP_CONCAT(CONCAT_WS(":",rel_classes.importSourcedId, rel_classes.isTemp)) as importClassSourcedId,
                            rel_classes.importSchoolSourcedId as importSchoolSourcedId
                        FROM
                            enrollments
                            INNER JOIN rel_classes ON rel_classes.rosterSourcedId = enrollments.classSourcedId
                        WHERE
                            enrollments.userSourcedId IN ("${importDataEnroll.join('","')}")
                        GROUP BY enrollments.sourcedId
                    `;
                    const [getDataEnroll] = await db[param.municipalId].query(getDataEnrollQuery);
                    const insLgateEnroll = [];
                    getDataEnroll.map((item) => {
                        const expClassSourcedId = item.importClassSourcedId.split(',');
                        let enrClassSourcedId, expGetIsTemp;
                        if (expClassSourcedId.length > 1) {
                            expClassSourcedId.map((val) => {
                                expGetIsTemp = val.split(':');
                                if (expGetIsTemp.length > 1 && expGetIsTemp[1] === "1") {
                                    enrClassSourcedId = expGetIsTemp[0]
                                }
                            })
                        } else {
                            expGetIsTemp = expClassSourcedId[0].split(':');
                            enrClassSourcedId = expGetIsTemp[0];
                        }
                        insLgateEnroll.push({
                            sourcedId: item.sourcedId,
                            status: item.status,
                            dateLastModified: item.dateLastModified,
                            classSourcedId: enrClassSourcedId,
                            schoolSourcedId: item.importSchoolSourcedId,
                            userSourcedId: item.userSourcedId,
                            role: item.role,
                            primary: item.primary,
                            beginDate: item.beginDate,
                            endDate: item.endDate,
                            metadataJpShussekiNo: item.metadataJpShussekiNo,
                            metadataJpPublicFlag: item.metadataJpPublicFlag,
                            municipalId: item.municipalId,
                            submited: 0,
                            isDelta: 1,
                            option: 'update_csv_to_lgate'
                        });
                    });

                    if (insLgateEnroll.length) {
                        await db[param.municipalId].importEnrollments.bulkCreate(insLgateEnroll)
                    }
                }

                let attrImport = [];
                for (let key in importUpdateData[0]) {
                    attrImport.push(key);
                }

                let exclude = ["sourcedId","orgSourcedIds"]
                let attrUpdate = await excludeArrayValue(exclude,attrImport)
                await db[param.municipalId].importUsers.bulkCreate(importUpdateData, { updateOnDuplicate: attrUpdate });

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.csv_import_data_updated'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});

                ++stepIndex
            break;

            case 'import_merge_data':
                initData.startInsertTime = moment()
                let filter = param?.schoolSourcedId ? ` AND (rel_classes.rosterSchoolSourcedId = '${param?.schoolSourcedId}' OR rel_classes.importSchoolSourcedId = '${param?.schoolSourcedId}') ` : ``;

                if(param.classSourceId && param.classSourceId !== "undefined" && param.classSourceId !== ""){
                    filter = filter+`  AND (rel_classes.rosterSourcedId = '${param.classSourceId}' )`
                }
                // console.log({'160': filter })

                const query = `
                    SELECT 
                        import_users.*,
                        import_enrollments.sourcedId AS  'import_enrollments.sourcedId',
                        import_enrollments.status AS  'import_enrollments.status',
                        import_enrollments.dateLastModified AS  'import_enrollments.dateLastModified',
                        import_enrollments.classSourcedId AS  'import_enrollments.classSourcedId',
                        import_enrollments.schoolSourcedId AS  'import_enrollments.schoolSourcedId',
                        import_enrollments.userSourcedId AS  'import_enrollments.userSourcedId',
                        import_enrollments.role AS  'import_enrollments.role',
                        import_enrollments.primary AS  'import_enrollments.primary',
                        import_enrollments.beginDate AS  'import_enrollments.beginDate',
                        import_enrollments.endDate AS  'import_enrollments.endDate',
                        import_enrollments.metadataJpShussekiNo AS  'import_enrollments.metadataJpShussekiNo',
                        import_enrollments.metadataJpPublicFlag AS  'import_enrollments.metadataJpPublicFlag',
                        import_enrollments.municipalId AS  'import_enrollments.municipalId',
                        import_enrollments.submited AS  'import_enrollments.submited',
                        import_enrollments.option AS  'import_enrollments.option',
                        import_enrollments.isParentSkiped AS  'import_enrollments.isParentSkiped',
                        rel_classes.rosterSchoolSourcedId AS 'rel_classes.rosterSchoolSourcedId',
                        rel_classes.rosterTermSourcedIds AS 'rel_classes.rosterTermSourcedIds',
                        rel_classes.rosterSourcedId AS 'rel_classes.rosterSourcedId',
                        users.id AS 'users.id',
                        users.sourcedId AS 'users.sourcedId',
                        users.uuid AS 'users.uuid',
                        users.status AS 'users.status',
                        users.username AS 'users.username',
                        users.dateLastModified AS 'users.dateLastModified',
                        users.password AS 'users.password' ,
                        users.orgSourcedIds AS 'users.orgSourcedIds' ,
                        users.agentSourcedIds AS 'users.agentSourcedIds' ,
                        users.isLocal AS 'users.isLocal' ,
                        users.familyName AS 'users.familyName' ,
                        users.givenName AS 'users.givenName' ,
                        users.middleName AS 'users.middleName' ,
                        users.metadataJpKanaFamilyName AS 'users.metadataJpKanaFamilyName' ,
                        users.metadataJpKanaGivenName AS 'users.metadataJpKanaGivenName' ,
                        users.metadataJpKanaMiddleName AS 'users.metadataJpKanaMiddleName' ,
                        enrollments.id AS 'enrollments.id',
                        enrollments.sourcedId AS 'enrollments.sourcedId',
                        enrollments.classSourcedId AS 'enrollments.classSourcedId',
                        enrollments.userSourcedId AS 'enrollments.userSourcedId',
                        enrollments.schoolSourcedId AS 'enrollments.schoolSourcedId',
                        enrollments.role AS 'enrollments.role',
                        enrollments.metadataJpShussekiNo AS 'enrollments.metadataJpShussekiNo',
                        enrollments.municipalId AS 'enrollments.municipalId',
                        lgate_users.id AS 'lgate_users.id',
                        lgate_enrollments.id AS 'import_enrollments.lgateId'
                    FROM 
                    import_users
                    INNER JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
                    INNER JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
                    INNER JOIN rel_classes ON rel_classes.importSourcedId = import_enrollments.classSourcedId
                    INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId 
                    LEFT JOIN lgate_users ON import_users.sourcedId = lgate_users.oldSourcedId 
                    LEFT JOIN lgate_enrollments ON import_enrollments.userSourcedId = lgate_enrollments.userOldSourcedId AND import_enrollments.classSourcedId = lgate_enrollments.school_class_uuid
                    LEFT JOIN users ON import_users.userIdLgate = users.sourcedId 
                    LEFT JOIN enrollments ON enrollments.userSourcedId = users.sourcedId AND enrollments.classSourcedId = rel_classes.rosterSourcedId 
                    WHERE 
                    import_users.role IN ("teacher", "student")
                    AND import_classes.classType = 'homeroom'
                    AND import_enrollments.submited = 0
                    AND import_users.isParentSkiped = 0
                    AND import_users.option != 'unfinished'
                    AND import_users.municipalId = '${param.municipalId}'
                    ${filter}
                    GROUP BY import_enrollments.sourcedId
                    LIMIT ${limit}
                `;

                const queryResult = await db[param.municipalId].query(query).then((item) => {
                    return item[0]
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 
                let updateImportEnrollment = [];
                
                if(queryResult && queryResult.length){
                    let redisSkippedData = await redisClient.get(`SKIPPED_USERS_${param.municipalId}`);
                    redisSkippedData = redisSkippedData ? JSON.parse(redisSkippedData) : [];

                    // insert to skipped redis
                    let queryResultImport = [];
                    const queryMapList = await mappingQueryArrayReturn(queryResult);
                    await Promise.all(queryResult.map(async (item)=> {
                      const skippedUser = redisSkippedData.findIndex(value => value.sourcedId === item.sourcedId);
                      let isSkipped = false;
                      const data = {
                        sourcedId : item.sourcedId,
                        status : item.status,
                        dateLastModified : item.dateLastModified,
                        enabledUser : item.enabledUser,
                        orgSourcedIds : item.orgSourcedIds,
                        role : item.role,
                        username : item.username,
                        userIds : item.userIds,
                        givenName : item.givenName,
                        familyName : item.familyName,
                        middleName : item.middleName,
                        metadataJpKanaGivenName : item.metadataJpKanaGivenName,
                        metadataJpKanaFamilyName : item.metadataJpKanaFamilyName,
                        metadataJpKanaMiddleName : item.metadataJpKanaMiddleName,
                        metadataJpHomeClass : item.metadataJpHomeClass,
                        identifier : item.identifier,
                        email : item.email,
                        sms : item.sms,
                        phone : item.phone,
                        agentSourcedIds : item.agentSourcedIds,
                        grades : item.grades,
                        password : item.password,
                        municipalId : item.municipalId,
                        userIdLgate : item.userIdLgate,
                        userLgateName : item.userLgateName,
                        userLgatePassword : item.userLgatePassword,
                        option : item.option,
                        submited : item.submited,
                        isDelta : item.isDelta
                      }
                      let pass = setPasswordRule(item);
                      if(!pass.setPassword && !pass.passwordValue){
                        if (skippedUser >= 0) {
                          redisSkippedData.splice(skippedUser, 1);
                        }
                      } else {
                        if (skippedUser >= 0) {
                            if ((pass.passwordValue && item.username) || item.option === 'skip_csv_to_lgate') {
                              redisSkippedData.splice(skippedUser, 1);
                            } else {
                              isSkipped = true;
                              data.submited = 1;
                              if (item.option != 'skip_csv_to_lgate') {
                                  redisSkippedData[skippedUser] = data;
                              }
                            }
                        } else if (!pass.passwordValue || !item.username) {
                            isSkipped = true;
                            data.submited = 1;
                            if (item.option != 'skip_csv_to_lgate') {
                                redisSkippedData.push(data);
                            }
                        }
                      }
                        
                      if (!isSkipped) {
                        queryResultImport.push(item);
                      } else {
                        importSubmited.push(data);
                        
                        //update enrollment
                        const getResultMapUser = queryMapList.findIndex(value => value.sourcedId === item.sourcedId);
                        if (getResultMapUser >= 0) {
                            await Promise.all(queryMapList[getResultMapUser].import_enrollments.map(async (item_enrollments) => {
                                if (item_enrollments.isParentSkiped === 0) {
                                    updateImportEnrollment.push({
                                        userSourcedId: item_enrollments.userSourcedId,
                                        classSourcedId: item_enrollments.classSourcedId
                                    });
                                }
                            }));
                        }
                      }
                    }));

                    await redisClient.set(`SKIPPED_USERS_${param.municipalId}`, JSON.stringify(redisSkippedData));
                    let queryResultMap = await mappingQueryArrayReturn(queryResultImport)
                    let importDataUser = [];
                    let importDataEnrollment = [];
                    let rosterUsers = [];
                    let insertRelUser = [];
                    let insertRelEnrollment = [];
                    let lgateSubmit = [];
                    let lgateSubmitEnrollments = [];
                    let tobedeletedSourcedId = [];

                    await Promise.all(queryResultMap.map(async (item)=> {
                        importDataUser.push({
                            sourcedId : item.sourcedId,
                            status : item.status,
                            dateLastModified : item.dateLastModified,
                            enabledUser : item.enabledUser,
                            orgSourcedIds : item.rel_classes[0].rosterSchoolSourcedId,
                            role : item.role,
                            username : item.username,
                            userIds : item.userIds,
                            givenName : item.givenName,
                            familyName : item.familyName,
                            middleName : item.middleName,
                            metadataJpKanaGivenName : item.metadataJpKanaGivenName,
                            metadataJpKanaFamilyName : item.metadataJpKanaFamilyName,
                            metadataJpKanaMiddleName : item.metadataJpKanaMiddleName,
                            metadataJpHomeClass : item.metadataJpHomeClass,
                            identifier : item.identifier,
                            email : item.email,
                            sms : item.sms,
                            phone : item.phone,
                            agentSourcedIds : item.agentSourcedIds,
                            grades : item.grades,
                            password : (item.userLgatePassword != null && item.userLgatePassword != '') ? item.userLgatePassword : item.password,
                            municipalId : item.municipalId,
                            userIdLgate : item.userIdLgate,
                            userLgateName : item.userLgateName,
                            userLgatePassword : item.userLgatePassword,
                            option : item.option,
                            submited : item.submited,
                            termSourcedIds : item.rel_classes[0].rosterTermSourcedIds,
                            isDelta : item.isDelta,
                            lgateUsersId : item.lgate_users[0]?.id
                        })

                        if (item.option != 'skip_csv_to_lgate' && item.option != 'delete_add_from_lgate') {
                            let tempData = {
                                rosterSourcedId : item.users[0]?.sourcedId || item.sourcedId,
                                rosterOrgSourcedIds : item.rel_classes[0].rosterSchoolSourcedId,
                                rosterAgentSourcedIds : item.users[0]?.agentSourcedIds || item.agentSourcedIds,
                                importSourcedId : item.sourcedId,
                                importOrgSourcedIds : item.orgSourcedIds,
                                importAgentSourcedIds : item.agentSourcedIds,
                                municipalId: item.municipalId,
                                isTemp: 1,
                            }

                            const relData = await db[param.municipalId].relUsers.findAll({
                              where: {
                                rosterSourcedId: tempData.rosterSourcedId,
                                importSourcedId: tempData.importSourcedId,
                              },
                            }).then((item) => {
                                return item
                            }).catch((err) => {
                                let validationError = JSON.parse(JSON.stringify(err))?.original
                                return done({message : validationError?.sqlMessage})
                            }) ;

                            if (relData.length == 0) {
                                insertRelUser.push(tempData)
                            }

                            if(item.users?.length){
                                rosterUsers.push({
                                    id : item.users[0].id,
                                    sourcedId : item.users[0].sourcedId,
                                    uuid : item.users[0].uuid,
                                    status : item.users[0].status,
                                    dateLastModified : item.users[0].dateLastModified,
                                    enabledUser : item.enabledUser,
                                    orgSourcedIds : item.rel_classes[0].rosterSchoolSourcedId,
                                    role : item.role,
                                    username : item.users[0].username,
                                    userIds : item.userIds,
                                    givenName : item.users[0].givenName,
                                    familyName : item.users[0].familyName,
                                    middleName : item.users[0].middleName,
                                    metadataJpKanaGivenName : item.users[0].metadataJpKanaGivenName,
                                    metadataJpKanaFamilyName : item.users[0].metadataJpKanaFamilyName,
                                    metadataJpKanaMiddleName : item.users[0].metadataJpKanaMiddleName,
                                    metadataJpHomeClass : item.metadataJpHomeClass,
                                    identifier : item.identifier,
                                    email : item.email,
                                    sms : item.sms,
                                    phone : item.phone,
                                    agentSourcedIds : item.agentSourcedIds,
                                    grades : item.grades,
                                    password : item.users[0].password,
                                    isLocal : item.users[0].isLocal,
                                    municipalId : item.municipalId,
                                    yearId : item.rel_classes[0].rosterTermSourcedIds,
                                    toBeDeleted : 0
                                })
                            }
                        }
                            
                            await Promise.all(item.import_enrollments.map(async (item_enrollments,index_enrollments) => {
                                if (item_enrollments.isParentSkiped === 0) {
                                    updateImportEnrollment.push({
                                        userSourcedId: item_enrollments.userSourcedId,
                                        classSourcedId: item_enrollments.classSourcedId
                                    });
                                }
                                if (item_enrollments.option != 'skip_csv_to_lgate' && item.option != 'skip_csv_to_lgate' && item.option != 'delete_add_from_lgate') {
                                if (!item_enrollments.lgateId) {
                                let tempData = {
                                    rosterSourcedId : item.enrollments[index_enrollments].sourcedId || item_enrollments.sourcedId,
                                    rosterUserSourcedId : item.users[0].sourcedId || item_enrollments.userSourcedId || item_enrollments.userSourcedId,
                                    rosterSchoolSourcedId : item.rel_classes[index_enrollments].rosterSchoolSourcedId,
                                    rosterClassSourcedId : item.rel_classes[index_enrollments].rosterSourcedId,
                                    importSourcedId : item_enrollments.sourcedId,
                                    importUserSourcedId : item_enrollments.userSourcedId,
                                    importSchoolSourcedId : item_enrollments.schoolSourcedId,
                                    importClassSourcedId : item_enrollments.classSourcedId,
                                    municipalId: item_enrollments.municipalId,
                                    isTemp: 1,
                                }

                                const relData = await db[param.municipalId].relEnrollments.findAll({
                                where: {
                                    rosterSourcedId: tempData.rosterSourcedId,
                                    importSourcedId: tempData.importSourcedId,
                                    rosterUserSourcedId: tempData.rosterUserSourcedId,
                                    importUserSourcedId: tempData.importUserSourcedId,
                                },
                                }).then((item) => {
                                    return item
                                }).catch((err) => {
                                    let validationError = JSON.parse(JSON.stringify(err))?.original
                                    return done({message : validationError?.sqlMessage})
                                }) ;

                                if (relData.length == 0) {
                                    insertRelEnrollment.push(tempData);
                                }

                                if (config.IMPORT_TO_LGATE) {
                                    lgateSubmitEnrollments.push({
                                        userOldSourcedId : item.users[0].sourcedId || item_enrollments.userSourcedId,
                                        school_class_uuid: item.rel_classes[index_enrollments].rosterSourcedId,
                                        role_uuid: null,
                                        role: item_enrollments.role,
                                        organization_uuid: item.rel_classes[index_enrollments].rosterSchoolSourcedId,
                                        school_class_number: item_enrollments.metadataJpShussekiNo || "0",
                                        municipalId: item_enrollments.municipalId
                                    })
                                }
                                }
                                } else {
                                    bulkDeleteEnrData.push(item_enrollments.sourcedId)
                                    bulkDeleteEnrLgate.push({
                                        'userSourcedId': item_enrollments.userSourcedId,
                                        'classSourcedId': item_enrollments.classSourcedId
                                    })
                                }
                            }))
                    }))

                    await Promise.all(
                        importDataUser.map(async (item) => {
                            const userLgateId = item.lgateUsersId;
                            delete item.lgateUsersId;
                            item.submited = 1;
                            if (item.option !== 'delete_add_from_lgate') {
                                importSubmited.push(JSON.parse(JSON.stringify(item)));
                            }
                            
                            if (item.option == 'add_from_lgate' || item.option == 'update_csv_to_lgate') {
                                let lgateIndex = rosterUsers.findIndex((row) => item.userIdLgate === row.sourcedId);
                                if (lgateIndex >= 0) {
                                    data = rosterUsers[lgateIndex];
                                    item.status = item.status ? item.status : data.status;

                                    if(item.dateLastModified) {
                                        item.dateLastModified = item.dateLastModified
                                    } else {
                                        item.dateLastModified = `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
                                    } 
                        
                                    let returnedTarget = Object.assign(JSON.parse(JSON.stringify(data)), JSON.parse(JSON.stringify(item)));
                                    returnedTarget.sourcedId = data.sourcedId
                                    returnedTarget.password = item.password || ""
                                    returnedTarget.username = data.username
                                    returnedTarget.submited = 0
                                    if(item.isDelta && returnedTarget.status == 'tobedeleted'){
                                      tobedeletedSourcedId.push(returnedTarget.sourcedId)
                                      returnedTarget.isToBeDeleted = 1
                                    }

                                    returnedTarget = filterUsersSubmitSetting(data, returnedTarget, param.submitSetting);

                                    if (config.IMPORT_TO_LGATE && !userLgateId) {
                                        let username = returnedTarget.username.split("@");
                                        lgateSubmit.push({
                                            last_name:returnedTarget.familyName,
                                            last_name_kana: returnedTarget.metadataJpKanaFamilyName,
                                            first_name: returnedTarget.givenName,
                                            first_name_kana: returnedTarget.metadataJpKanaGivenName,
                                            login_id: username[0],
                                            password: returnedTarget.password,
                                            is_local: data?.isLocal,
                                            is_active: true,
                                            organization_uuid: returnedTarget.orgSourcedIds,
                                            option : 'update',
                                            municipalId : returnedTarget.municipalId,
                                            oldSourcedId : returnedTarget.sourcedId
                                        });
                                    }
                                }
                            } else if (item.option == 'add_csv_to_lgate') {
                                if (config.IMPORT_TO_LGATE && !userLgateId) {
                                    let username = item.username.split("@");
                                    lgateSubmit.push({
                                        last_name:item.familyName,
                                        last_name_kana: item.metadataJpKanaFamilyName,
                                        first_name: item.givenName,
                                        first_name_kana: item.metadataJpKanaGivenName,
                                        login_id: username[0],
                                        password: item.password,
                                        is_local: config.IS_LOCAL ? 1 : 0,
                                        is_active: true,
                                        organization_uuid: item.orgSourcedIds,
                                        option : 'insert',
                                        municipalId : item.municipalId,
                                        oldSourcedId : item.sourcedId
                                    });
                                }
                            } else if (item.option == 'skip_csv_to_lgate' || item.option === 'delete_add_from_lgate') {
                                bulkDeleteCsv.push(item.sourcedId);
                                if (item.option === 'delete_add_from_lgate') {
                                    bulkDeleteEnrCsv.push(item.sourcedId);
                                }
                            }
                        })
                    )

                    Array.prototype.push.apply(initData.bulkDeleteCsv,bulkDeleteCsv); 
                    
                    if(lgateSubmit.length){
                        await db[param.municipalId].lgateUsers.bulkCreate(lgateSubmit).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) 
                    }

                    if(lgateSubmitEnrollments.length){
                        await db[param.municipalId].lgateEnrollments.bulkCreate(lgateSubmitEnrollments).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) 
                    }
                    
                    if(insertRelUser.length){
                        await db[param.municipalId].relUsers.bulkCreate(insertRelUser).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;
                    }
                    if(insertRelEnrollment.length){
                        await db[param.municipalId].relEnrollments.bulkCreate(insertRelEnrollment).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;
                    }
                    if (bulkDeleteCsv.length) {
                        await db[param.municipalId].importUsers.destroy({
                            where: {
                                sourcedId: { [Op.in]: bulkDeleteCsv },
                            },
                        }).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        });
                        
                        if (bulkDeleteEnrCsv.length) {
                            await db[param.municipalId].importEnrollments.destroy({
                                where: {
                                    userSourcedId: { [Op.in]: bulkDeleteEnrCsv },
                                },
                            });
                        }
                        
                        await db[param.municipalId].lgateUsers.destroy({
                            where: {
                                oldSourcedId: { [Op.in]: bulkDeleteCsv },
                            },
                        });

                        await db[param.municipalId].lgateEnrollments.destroy({
                            where: {
                                userOldSourcedId: { [Op.in]: bulkDeleteCsv },
                            },
                        });

                        await db[param.municipalId].relUsers.destroy({
                            where: {
                                importSourcedId: { [Op.in]: bulkDeleteCsv },
                                isTemp: 1
                            },
                        });
                        
                        await db[param.municipalId].relEnrollments.destroy({
                            where: {
                                importUserSourcedId: { [Op.in]: bulkDeleteCsv },
                                isTemp: 1
                            },
                        });
                    }

                    if (bulkDeleteEnrData.length) {
                        await db[param.municipalId].relEnrollments.destroy({
                            where: {
                                importSourcedId: { [Op.in]: bulkDeleteEnrData },
                                isTemp: 1
                            },
                        });
                    }

                    if (bulkDeleteEnrLgate.length) {
                        const delLgateCondition = [];
                        bulkDeleteEnrLgate.map(item => {
                            delLgateCondition.push({
                                userOldSourcedId: item.userSourcedId,
                                school_class_uuid: item.classSourcedId
                            })
                        })
                        await db[param.municipalId].lgateEnrollments.destroy({
                            where: {
                                [Op.or]: delLgateCondition
                            },
                        });
                    }
                    
                    if (updateImportEnrollment.length) {
                        await db[param.municipalId].importEnrollments.update(
                            {
                                submited: 1
                            },
                            {
                            where: {
                                [Op.or]: updateImportEnrollment
                            },
                        })
                    }

                    let attrImportSubmited = [];
                    if (importSubmited.length) {
                        let excludeImportUsers = ["sourcedId","orgSourcedIds"]
                        for (let key in importSubmited[0]) {
                            if(!excludeImportUsers.includes(key)){
                                attrImportSubmited.push(key);
                            }
                        }
                        importSubmited = await convertDateForInsert(importSubmited,'dateLastModified');
                        await db[param.municipalId].importUsers.bulkCreate(importSubmited, { updateOnDuplicate: attrImportSubmited }).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;
                    }

                    let filter = param?.schoolSourcedId ? ` AND (rel_classes.rosterSchoolSourcedId = '${param?.schoolSourcedId}' OR rel_classes.importSchoolSourcedId = '${param?.schoolSourcedId}') ` : ``;
                    
                    if(param.classSourceId && param.classSourceId !== "undefined" && param.classSourceId !== ""){
                        filter = filter+`  AND (rel_classes.rosterSourcedId = '${param.classSourceId}' )`
                    }

                    const queryImportCsvDataSubmited = `
                        SELECT 
                            import_users.sourcedId
                        FROM 
                            import_users
                        INNER JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
                        INNER JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
                        INNER JOIN rel_classes ON rel_classes.importSourcedId = import_enrollments.classSourcedId
                        INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId
                        WHERE 
                            import_users.role IN ("teacher", "student")
                            AND import_users.municipalId = '${param.municipalId}'
                            AND import_enrollments.submited = 1
                            AND import_classes.classType = 'homeroom'
                            AND import_users.option != 'skip_csv_to_lgate'
                            AND import_users.option != 'delete_add_from_lgate'
                            ${filter}
                        GROUP BY import_users.sourcedId
                    `;
                    const [resultImportCsvDataSubmited] = await db[param.municipalId].query(queryImportCsvDataSubmited)
                    initData.progress = resultImportCsvDataSubmited.length
                    await job.progress({total_row:initData.importCsvDataAll,progress_row:initData.progress,is_calculating:true})

                    rowstart = ((offset*limit)+1)
                    rowend = ((offset+1)*limit)
                    rowend = initData.importCsvDataAll < rowend ? initData.importCsvDataAll : rowend
                    
                    initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                    initData.logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.csv_data_merged_process').replace('%ROW_START%',rowstart).replace('%ROW_END%',rowend), executionTime : initData.insertTime}
                    LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
                } else {
                    ++stepIndex
                    offset = 0
                }
            break;
            
            case 'update_tobedeleted': 
            initData.startInsertTime = moment()
                let bulkTobeDeleted = [];

                let filterTobeDeleted = '';
                if (param.schoolSourcedId) filterTobeDeleted += ` AND (rel_classes.rosterSchoolSourcedId = '${param?.schoolSourcedId}' OR rel_classes.importSchoolSourcedId = '${param?.schoolSourcedId}') `;

                const queryTobeDeleted = `
                    SELECT 
                        users.* 
                    FROM 
                        users
                    INNER JOIN enrollments ON enrollments.userSourcedId = users.sourcedId
                    INNER JOIN rel_orgs ON rel_orgs.rosterSourcedId = users.orgSourcedIds
                    INNER JOIN rel_classes ON rel_classes.rosterSourcedId = enrollments.classSourcedId
                    INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId
                    LEFT JOIN import_users ON (import_users.userIdLgate = users.sourcedId)
                    WHERE 
                        users.role IN ("teacher", "student")
                        AND import_classes.classType = 'homeroom'
                        AND users.municipalId = '${param.municipalId}'
                        AND import_users.userIdLgate IS NULL
                        ${filterTobeDeleted}
                `;
                
                const tobedeletedData = await db[param.municipalId].query(queryTobeDeleted).then((item) => {
                    return item[0]
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 
            
                await Promise.all(
                    tobedeletedData.map(async (item) => {
                        bulkTobeDeleted.push(item.id);
                    })
                );
                
                bulkTobeDeleted = bulkTobeDeleted.filter((value, index, self) => {
                    return self.indexOf(value) === index;
                });
            
                if (bulkTobeDeleted.length) {
                    await db[param.municipalId].users.update(
                        {isToBeDeleted: 1, dateLastModified : `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`},
                        { where: { id: { [Op.in]: bulkTobeDeleted } } }
                    ).then((item) => {
                    }).catch((err) => {
                        let validationError = JSON.parse(JSON.stringify(err))?.original
                        return done({message : validationError?.sqlMessage})
                    }) ;
                }
                
                ++stepIndex
                
                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.roster_data_status_tobedeleted'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
            break;
            
            case 'count_all_data_import' :
                initData.startInsertTime = moment()
                let filterAll = param?.schoolSourcedId ? ` AND (rel_classes.rosterSchoolSourcedId = '${param?.schoolSourcedId}' OR rel_classes.importSchoolSourcedId = '${param?.schoolSourcedId}') ` : ``;
                if(param.classSourceId && param.classSourceId !== "undefined" && param.classSourceId !== ""){
                    filterAll = filterAll+`  AND (import_enrollments.classSourcedId = '${param.classSourceId}' )`
                }

                const queryImportCsvDataAll = `
                    SELECT 
                        import_users.sourcedId
                    FROM 
                    import_users
                    INNER JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
                    INNER JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
                    INNER JOIN rel_classes ON rel_classes.importSourcedId = import_enrollments.classSourcedId
                    INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId 
                    WHERE 
                        import_users.role IN ("teacher", "student")
                        AND import_classes.classType = 'homeroom'
                        AND import_users.option != 'skip_csv_to_lgate'
                        AND import_users.option != 'delete_add_from_lgate'
                        AND import_users.option != 'unfinished'
                        AND import_users.municipalId = '${param.municipalId}'
                        ${filterAll}
                    GROUP BY import_users.sourcedId
                `;
            
                const resultImportCsvDataAll = await db[param.municipalId].query(queryImportCsvDataAll).then((item) => {
                    return item[0]
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 
                initData.importCsvDataAll = resultImportCsvDataAll.length
                if (initData.importCsvDataAll != initData.progress) {
                    initData.progress = initData.importCsvDataAll;
                }
                await job.progress({total_row:initData.importCsvDataAll,progress_row:initData.progress,is_calculating:true})
                ++stepIndex

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.count_all_csv_import_data'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
            break;
            
            default:
                
                return done(null,initData.importCsvDataAll)
        }

        await this.onProcess(job,done,initData,stepIndex,limit,offset);
    }

    onActive = async (job, jobPromise) => {
        let logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.submit_merged_start')}
        LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});

        await db[job.data.municipalId].importTaskJob.create({
            municipalId : job.data.municipalId,
            type : job.data.type,
            jobId : job.id,
            userId : job.data.userId,
            createdDate : moment().format("YYYY-MM-DD HH:mm:ss")
        })
    }

    onWaiting = async (jobId) => {
        console.log('waiting',jobId)
    }

    onError = async (error) => {
        console.log('error',error)
    }

    onProgress = async (job, progress) => {

        if(typeof progress === 'number') {
            console.log('progress',job.id, progress)
            
        }
    }

    onRemoved = async (job) => {
        console.log('remove',job.id)
    }

    onCompleted = async (job,result) => {

        let percent = 0
        let resultOrgSubmited = []
        const importTaskProgressId = `${job.data.municipalId}_${CLASS_ATENDANCE_COLLATION}`

        // HANDLE IF HALFT DATA PER ORG PROGRESSBAR -- start
        if(job.data && job.data.schoolSourcedId){
            let queryOrg = `
                SELECT 
                    import_users.sourcedId, import_enrollments.submited
                FROM 
                import_users
                INNER JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
                INNER JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
                INNER JOIN rel_classes ON rel_classes.importSourcedId = import_enrollments.classSourcedId
                INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId 
                WHERE 
                    import_users.role IN ("teacher", "student")
                    AND import_classes.classType = 'homeroom'
                    AND import_users.option != 'skip_csv_to_lgate'
                    AND import_users.option != 'delete_add_from_lgate'
                    AND import_users.municipalId = '${job.data.municipalId}'
                    AND import_users.orgSourcedIds = '${job.data.schoolSourcedId}' 
            `;

            if(job.data.classSourceId)
                queryOrg = queryOrg+` AND rel_classes.importSourcedId = '${job.data.classSourceId}'`

            queryOrg = queryOrg+` GROUP BY import_users.sourcedId`

            const [result_org] = await db[job.data.municipalId].query(queryOrg)

            // IF BULK BASED ON ORG ID AND !SUPERADMIN
            resultOrgSubmited = result_org.filter((item)=>item.submited == 1)
            if (result_org.length && resultOrgSubmited.length) {
                percent = (resultOrgSubmited.length / result_org.length) * 100;
            } else {
                percent = 100;
            }

            await db[job.data.municipalId].importTaskProgressDetail.upsert({
                id: job.data.classSourceId ? `${job.data.municipalId}_${job.data.classSourceId}_${CLASS_ATENDANCE_COLLATION}` : `${job.data.municipalId}_${job.data.schoolSourcedId}_${CLASS_ATENDANCE_COLLATION}`,
                importTaskProgressId: importTaskProgressId,
                municipalId: job.data.municipalId,
                type: CLASS_ATENDANCE_COLLATION, 
                status: percent == 100 ? STATUS_COMPLETED : STATUS_PROCESSING,
                progress: percent,
                lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                orgSourcedId:job.data.schoolSourcedId,
                classSourceId:job.data.classSourceId
            });
        }
        // HANDLE IF HALFT DATA PER ORG PROGRESSBAR -- end
        
        const queryall = `
            SELECT 
                import_users.sourcedId, import_users.submited
            FROM 
            import_users
            INNER JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
            INNER JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
            INNER JOIN rel_classes ON rel_classes.importSourcedId = import_enrollments.classSourcedId
            INNER JOIN import_classes ON rel_classes.importSourcedId = import_classes.sourcedId 
            WHERE 
                import_users.role IN ("teacher", "student")
                AND import_classes.classType = 'homeroom'
                AND import_users.option != 'skip_csv_to_lgate'
                AND import_users.option != 'delete_add_from_lgate'
                AND import_users.municipalId = '${job.data.municipalId}'
            GROUP BY import_users.sourcedId
        `;
        const [resultall] = await db[job.data.municipalId].query(queryall)

        const resultsubmited = resultall.filter((item)=>item.submited == 1)
 
        if (resultall.length && resultsubmited.length) {
            percent = (resultsubmited.length / resultall.length) * 100;
        } else {
            percent = 100;
        }
        
        // HANDLE PARENT AND CHILD PROGRESS BAR -- start
        if(job.data.schoolSourcedId){
            const [classHasbeenSubmited] = await db[job.data.municipalId].query(`SELECT orgSourcedId, classSourceId, progress FROM import_task_progress_details WHERE municipalId = '${job.data.municipalId}' AND type = '${CLASS_ATENDANCE_COLLATION}'`)
                
            const [classHaveToSubmit] = await db[job.data.municipalId].query(
                `SELECT COUNT(sourcedId) as count, schoolSourcedId FROM import_classes WHERE municipalId = '${job.data.municipalId}' and import_classes.option != 'skip_csv_to_lgate' and import_classes.classType='homeroom' and import_classes.isParentSkiped='0' group by schoolSourcedId`
            )

            const classProgress = classHasbeenSubmited.filter(item => item.classSourceId);
            const orgsProgress = classHasbeenSubmited.filter(item => !item.classSourceId);

            let totalClassMunicipal = 0;
            let classSubmitedProgress = 0;
            classHaveToSubmit.map((item) => {
                const findIdxOrgsProgress = orgsProgress.findIndex((val) => val.orgSourcedId === item.schoolSourcedId)
                const totalClassSubmited = (classProgress.filter((val) => val.orgSourcedId=== item.schoolSourcedId)).length;
                classSubmitedProgress += (findIdxOrgsProgress >= 0) ? (orgsProgress[findIdxOrgsProgress].progress*item.count/100) : totalClassSubmited;
                totalClassMunicipal += item.count;
            })

            percent = (classSubmitedProgress / totalClassMunicipal) * 100;
        } 
        // HANDLE PARENT AND CHILD PROGRESS BAR -- end
        
        if(percent > 100) percent = 100;

        await db[job.data.municipalId].importTaskProgress.upsert({
            id: importTaskProgressId,
            municipalId: job.data.municipalId,
            type: CLASS_ATENDANCE_COLLATION,
            userId: "-",
            status: percent == 100 ? STATUS_COMPLETED : STATUS_PROCESSING,
            progress: percent,
            lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
        });

        if(percent == 100){
            await db[job.data.municipalId].importTaskJob.destroy({
                where : {
                    municipalId : job.data.municipalId,
                    type : job.data.type
                }
            })
        }
 
        let logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.submit_merged_finish')}
        LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
        console.log('completeds',job.id, result)
    }

    onFailed = async (job, err) => {
        let logData = {logFor: CLASS_ATENDANCE_COLLATION,message:lang.t('submit_users_classes.submit_merged_failed').replace('%MESSAGE%',err.message)}
        LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
        console.log('failed',job.id)
        
    }
    
}

/**
 * Create export variable to running function SubmitUsersEnrollments
 * @constructor
 */
const SubmitUsersEnrollmentsProcess = new SubmitUsersEnrollments()

export default SubmitUsersEnrollmentsProcess