import moment from 'moment';
import { v4 as uuidv4 } from "uuid";
import { v5 as uuidv5 } from "uuid";
import config from "../../config/config.js";
import {db} from "../../models/index.js";
import lang from '../../i18n.js';
import redisClient from "../../redisClient.js";
import { 
    SUBMIT_TO_LGATE,
    SCHOOL_COLLATION,
    LOG_TYPE_SUBMIT_MATCHING,
    DEFAULT_USERS_STATUS,
    DEFAULT_ENROLLMENTS_STATUS, 
    DEFAULT_ROLES_STATUS,
    DEFAULT_ROLE_TYPE
} from "../../constants/constans.js";
import e from 'cors';
import { excludeArrayValue, mappingQueryArrayReturn, convertNullToString } from '../../helpers/utility.js';
import { 
    insertClass, 
    updateClass, 
    deleteClass,
    insertSchool,
    updateSchool,
    deleteSchool,
    insertUser,
    updateUser,
    deleteUser,
    getRoles
} from '../../helpers/lgateApi.js';
import LogHelper from "../../helpers/log.js";
import { constants } from 'crypto';
const LOG = new LogHelper('SUBMIT_TO_LGATE');

const Municipal = db.Master.municipal;
const Op = db.Master.Sequelize.Op;

let step = ['organization','classes','users_update_role','users','skipped_users']

/**
 * Get list of data from lgate table and redis
 * @constructor
 */
const getParamData = async (step,municipalId,limit,offset) => {
    let result;

    switch (step) {
        case 'organization' :
            result = await db[municipalId].lgateOrganization.findAll({
                where : {
                    municipalId : municipalId,
                    type : 2,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                },
                limit : limit
            });
            break;
          
        case 'classes' :
            result = await db[municipalId].lgateClasses.findAll({
                where : {
                    municipalId : municipalId,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                    isParentSkiped : 0,
                },
                limit : limit
            });
            break;

        case 'users' :
            result = await db[municipalId].lgateUsers.findAll({
                attributes : ["last_name","last_name_kana","first_name","first_name_kana","login_id","password","organization_uuid","oldSourcedId","option", "is_local"],
                include: [
                    {
                        as : "belongs",
                        model: db[municipalId].lgateEnrollments,
                        attributes: ["school_class_uuid","role_uuid","school_class_number"],
                        where : {
                            isParentSkiped : 0,
                        },
                    }, 
                    {
                        as : "import_users",
                        model: db[municipalId].importUsers
                    },
                    {
                        as : "import_role",
                        model: db[municipalId].importRoles
                    },
                ],
                where : {
                    municipalId : municipalId,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                    isParentSkiped : 0,
                },
                limit : limit
            });
            break;

        case 'skipped_users' :
            let redisSkippedData = await redisClient.get(`SKIPPED_USERS_${municipalId}`);
            redisSkippedData = redisSkippedData ? JSON.parse(redisSkippedData) : [];

            if (redisSkippedData.length) {
                result = redisSkippedData.splice(offset, limit);
            } else {
                result = [];
            }
            
            break;
    
        default :
            step = 'end'
            result = false
            break;
    }
    
    return {
        step : step,
        result : result
    }
}

/**
 * Process to change spacing string to ""
 * @constructor
 */
const cleanString = (str) => {
    return str?.replace(/(\r\n|\n|\r)/gm, "");
}

/**
 * Process to submit data from lgate table to lgate api
 * @constructor
 */
const submitApi = async (municipalId,step,option,item,jobData) => {
    const Orgs = db[municipalId].orgs 
    let LgateClasses = db[municipalId].lgateClasses

    if (step !== 'skipped_users') {
        LgateClasses = await LgateClasses.findOne({ where : {
            oldSourcedId: item.oldSourcedId
        },
        include: [
            {
                as : "import_class",
                model: db[municipalId].importClasses,
                include :
                {
                as : "import_course",
                model: db[municipalId].importCourses
                }
            }
        ],
        })
    }

    item = JSON.parse(JSON.stringify(item))

    let API;
    let logData;
    let param;
    let response = {
        is_successful : false,
        result: {
            message: `failed execute ${step}`,
            errors: {
              default: [
                `failed execute ${step}`
              ]
            }
          }
    };

    switch (step) {
        case 'organization' :
    
            logData = {
                logFor: 'SUBMIT_ORGANIZATION_TO_LGATE',
            }
            
            if(option == 'insert') {
                param = {
                    code: item.code,
                    school_code: item.school_code,
                    name: item.name,
                    type: item.type,
                }
                API = await insertSchool(municipalId, param, jobData);
                logData.api = API.response?.url, 
                logData.param = param,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)

                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data

                    // INSERT ORG TO APP TABLE FROM LGATETABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- start
                    if(response.is_successful == true){
                        const createDatPayloads = [
                            {
                                id: `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                sourcedId:response.result.uuid,
                                uuid : response.result.uuid,
                                status:'active', 
                                name:response.result.name,
                                type : item.type == 2 ? 'school' : 'district',//item.type, // school
                                identifier:response.result.code,
                                schoolCode:response.result.school_code,
                                parentSourcedId:null, //? from where ? 
                                municipalId,
                                dateLastModified:`${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
                            }
                        ]
                        await Orgs.bulkCreate(createDatPayloads).then((item) => {
                        }).catch((err) => { 
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            logData = {logFor: SCHOOL_COLLATION,message:lang.t('submit_school.message.submit_merged_failed').replace('%MESSAGE%',validationError?.sqlMessage)}
                            LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
                        })  
                    }
                    // INSERT ORG TO APP TABLE FROM LGATETABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- end

                }
            } else if(option == 'update') {
                param = {
                    code: item.code,
                    school_code: (item.school_code || item.school_code != "") ? item.school_code : null,
                    name: item.name,
                    type: item.type,
                }
                API = await updateSchool(item.oldSourcedId, municipalId, param, jobData);
                logData.api = API.response?.url, 
                logData.param = param,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)

                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data
                    // UPDATE ORG IN APP TABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- start
                    if(response.is_successful == true){
                        const updateDatPayloads =  {
                            identifier:item.code,
                            schoolCode:response.result.school_code, 
                            name:response.result.name,
                            type : item.type == 2 ? 'school' : 'district',//item.type, // school,
                            dateLastModified:`${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
                        }
                        await Orgs.update(updateDatPayloads,{where:{sourcedId:item.oldSourcedId}}).then((item) => {
                        }).catch((err) => { 
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            logData = {logFor: SCHOOL_COLLATION,message:lang.t('submit_school.message.submit_merged_failed').replace('%MESSAGE%',validationError?.sqlMessage)}
                            LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
                        })
                    }
                    // UPDATE ORG IN APP TABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- end
                }
            } else if(option == 'delete') {
                response = false
            }

            if(response){
                response.info = `${step} section error on [${item.name}] `
                if(response.is_successful){
                    logData.message = lang.t(`submit_lgate.message.${option}`).replace('%TABLE%',step)
                    let result = response.result
                    
                    await db[municipalId].lgateOrganization.update({
                        newSourcedId : result.uuid,
                        submited : 1
                    },{
                        where : {
                            oldSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].lgateClasses.update({
                        organization_uuid : result.uuid
                    },{
                        where : {
                            organization_uuid : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].lgateUsers.update({
                        organization_uuid : result.uuid
                    },{
                        where : {
                            organization_uuid : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].lgateEnrollments.update({
                        organization_uuid : result.uuid
                    },{
                        where : {
                            organization_uuid : item.oldSourcedId
                        }
                    })

                    await db[municipalId].classes.update({
                        schoolSourcedId : result.uuid
                    },{
                        where : {
                            schoolSourcedId : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].courses.update({
                        orgSourcedId : result.uuid
                    },{
                        where : {
                            orgSourcedId : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].users.update({
                        orgSourcedIds : result.uuid
                    },{
                        where : {
                            orgSourcedIds : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].enrollments.update({
                        schoolSourcedId : result.uuid
                    },{
                        where : {
                            schoolSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].orgs.update({
                        sourcedId: result.uuid,
                        uuid: result.uuid
                    },{
                        where : {
                            sourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relOrgs.update({
                        rosterSourcedId : result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relClasses.update({
                        rosterSchoolSourcedId: result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterSchoolSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relCourses.update({
                        rosterOrgSourcedId: result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterOrgSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relEnrollments.update({
                        rosterSchoolSourcedId : result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterSchoolSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relUsers.update({
                        rosterOrgSourcedIds : result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterOrgSourcedIds : item.oldSourcedId
                        }
                    })

                } else {
                    logData.message = lang.t(`submit_lgate.message.failed_${option}`).replace('%TABLE%',step)
                }
            }
            LOG.create({type: SUBMIT_TO_LGATE,logData});
            break;
          
        case 'classes' :

            logData = {
                logFor: 'SUBMIT_CLASSES_TO_LGATE',
            }

            if(option == 'insert') {
                param = {
                    term_uuid: item.term_uuid,
                    grade_code: item.grade_code,
                    name: item.name,
                    class_type: item.classType == 'scheduled' ? 2 : 1
                }
                API = await insertClass(municipalId, item.organization_uuid, param, jobData);
                logData.api = API.response?.url, 
                logData.param = param,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)
                
                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data  
                    // INSERT CLASS TO APP TABLE FROM LGATETABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- start
                        if(response.is_successful == true){
                            let {result} = response
                            let {import_class} = LgateClasses
                            let {import_course} = import_class

                            if(import_course){
                                const insertParamClasses = {
                                    id: `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                    sourcedId: result.uuid,
                                    uuid: result.uuid,
                                    status: 'active',
                                    dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`,
                                    title: result.name,
                                    grades: result.grade.code,// last here 
                                    courseSourcedId: import_class?.courseSourcedId,
                                    classCode: import_class?.classCode,
                                    classType: import_class?.classType,
                                    location: import_class?.location, 
                                    schoolSourcedId: result?.organization.uuid,
                                    termSourcedIds: result?.term.uuid, 
                                    subjectCodes: import_class?.subjectCodes,
                                    periods: import_class?.periods,
                                    municipalId: import_class?.municipalId,
                                    yearId: result?.term.uuid,
                                    metadataJpSpecialNeeds: import_class?.metadataJpSpecialNeeds
                                }
     
                                await db[municipalId].classes.bulkCreate([insertParamClasses]).then((item) => { 
                                }).catch((err) => {
                                    let validationError = JSON.parse(JSON.stringify(err))?.original
                                    logData = {logFor: "INSERT_CLASS" ,message:lang.t('submit_classes.message.submit_merged_failed').replace('%MESSAGE%',validationError?.sqlMessage)}
                                    LOG.create({type: "INSERT_CLASS", logData});
                                });

                                const insertParamCourses = {
                                    id : `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                    sourcedId : import_class?.courseSourcedId,
                                    uuid : import_class?.courseSourcedId,
                                    status: 'active',
                                    dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`,
                                    schoolYearSourcedId : result?.term.uuid,
                                    title : import_course?.title,
                                    courseCode : import_course?.courseCode,
                                    grades : result.grade.code,
                                    orgSourcedId : result?.organization.uuid,
                                    subjects : import_course?.subjects,
                                    subjectCodes : import_course?.subjectCodes,
                                    municipalId,
                                    yearId : result?.term.uuid,
                                    classesId : result.uuid,
                                    toBeDeleted : 0,
                                };

                                await db[municipalId].courses.bulkCreate([insertParamCourses]).then((item) => { 
                                }).catch((err) => {
                                    let validationError = JSON.parse(JSON.stringify(err))?.original
                                    logData = {logFor: "INSERT_COURSE" ,message:lang.t('submit_classes.message.submit_merged_failed').replace('%MESSAGE%',validationError?.sqlMessage)}
                                    LOG.create({type: "INSERT_COURSE", logData});
                                });

                                await db[municipalId].relCourses.update({
                                    rosterSourcedId: import_class?.courseSourcedId,
                                    rosterSchoolYearSourcedId: result?.term.uuid,
                                    isTemp: 0
                                },{
                                    where : {
                                        rosterSourcedId : import_course?.sourcedId
                                    }
                                })
                            }
                             
                        } 
                    // INSERT CLASS TO APP TABLE FROM LGATETABLE IF INSERT TO LGATE SUCCESSED //T_SUBMIT --- end

                }
            } else if(option == 'update') {
                param = {
                    term_uuid: item.term_uuid,
                    grade_code: item.grade_code,
                    name: item.name,
                    class_type: item.classType == 'scheduled' ? 2 : 1
                }
                API = await updateClass(item.oldSourcedId, municipalId, item.organization_uuid, param, jobData);
                logData.api = API.response?.url, 
                logData.param = param,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)

                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data
                    if(response.is_successful){ 
                        await db[municipalId].classes.update({ title: item.name , dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`, grades: item.grade_code , termSourcedIds : item.term_uuid, classType :item.classType },{where:{sourcedId:item.oldSourcedId}}).then((item) => {
                            
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            logData = {logFor: "UPDATE_CLASS",message:lang.t('submit_classes.message.submit_merged_failed').replace('%MESSAGE%',validationError?.sqlMessage)}
                            LOG.create({type: "UPDATE_CLASS", logData});
                        }) ;
                    }
                }
            } else if(option == 'delete') {
                response = false
            }

            if(response){
                response.info = `${step} section error on [${item.name}] `
                if(response.is_successful){
                    logData.message = lang.t(`submit_lgate.message.${option}`).replace('%TABLE%',step)
                    let result = response.result

                    await db[municipalId].lgateClasses.update({
                        newSourcedId : result.uuid,
                        submited : 1
                    },{
                        where : {
                            oldSourcedId : item.oldSourcedId
                        }
                    })
                    
                    await db[municipalId].lgateEnrollments.update({
                        school_class_uuid : result.uuid
                    },{
                        where : {
                            school_class_uuid : item.oldSourcedId
                        }
                    })

                    await db[municipalId].courses.update({
                        classesId : result.uuid
                    },{
                        where : {
                            classesId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].enrollments.update({
                        classSourcedId : result.uuid
                    },{
                        where : {
                            classSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].classes.update({
                        sourcedId: result.uuid,
                        uuid: result.uuid
                    },{
                        where : {
                            sourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relClasses.update({
                        rosterSourcedId: result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relEnrollments.update({
                        rosterClassSourcedId : result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterClassSourcedId : item.oldSourcedId
                        }
                    })
                } else {
                    logData.message = lang.t(`submit_lgate.message.failed_${option}`).replace('%TABLE%',step)
                }
            }
            LOG.create({type: SUBMIT_TO_LGATE,logData});
            break; 
        
        case 'users' :

            logData = {
                logFor: 'SUBMIT_USERS_TO_LGATE',
            }
            let params = JSON.parse(JSON.stringify(item));

            delete params.option
            delete params.oldSourcedId
            params.is_active = true
            
            if(option == 'insert') {
                let getMunicipal = await Municipal.findOne({ where: { sourcedId: municipalId } });
                params.is_local = getMunicipal?.isLocal == 1 ? true : false  || config.IS_LOCAL;
                const paramsSend = { ...params };
                delete paramsSend.import_users;
                delete paramsSend.import_role;
                API = await insertUser(municipalId, paramsSend, jobData);
                logData.api = API.response?.url, 
                logData.param = params,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)

                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data  
                    // CREATE USER IF SUBMIT LGATE SUCCESS  T_SUBMIT -- start
                    if(response.is_successful){     
                        let {result} = response;
                        let academicSessionSelected = await db[municipalId].academicSessions.findAll({
                            attributes: ["title","sourcedId","endDate","startDate"],
                            where: {
                                title : { [Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                                startDate :{ [Op.lte]: moment.unix(result.updated_at).utc().format('YYYY-MM-DD') },
                                endDate : { [Op.gte]: moment.unix(result.updated_at).utc().format('YYYY-MM-DD') },
                                municipalId : { [Op.eq]: municipalId}
                            }
                        })     
                        const initDataYearId = [];
                        academicSessionSelected.map((item)=>{
                            if(!initDataYearId.includes(item.sourcedId)){
                                initDataYearId.push(item.sourcedId)
                            }
                        }) 

                        //insert enrollment
                        const insertEnrolmentDatPayloads = [];
                        if(result.belongs?.length > 0){
                            let belongIndex = 0;
                            let userGrade = null;
                            let gradeUser = [];
                            let currentYearGrade = false;
                            result.belongs.map((belong,index)=>{
                                insertEnrolmentDatPayloads.push({
                                    id: `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                    sourcedId: belong.uuid || "-",
                                    uuid: belong.uuid,
                                    status: DEFAULT_ENROLLMENTS_STATUS || 'active',
                                    dateLastModified: `${moment.unix(belong.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                    classSourcedId: belong.school_class.uuid || "-",
                                    schoolSourcedId: belong.school_class.organization.uuid || "-",
                                    userSourcedId: result.uuid || "-",
                                    role: belong.role.permission_code || "-",
                                    primary: belong.role.permission_code === 'teacher' ? 'true':'false',
                                    beginDate: `${moment.unix(belong.start_at).utc().format("YYYY-MM-DD")}`,
                                    endDate: `${moment.unix(belong.end_at).utc().format("YYYY-MM-DD")}`,
                                    municipalId: municipalId,
                                    yearId: belong.school_class.term.uuid,
                                    metadataJpShussekiNo: belong.role.permission_code === 'teacher' || belong.number == '' || belong.number == null ? "": belong.number,
                                    metadataJpPublicFlag: "",
                                    hardDelete: item.is_local
                                })
                                
                                if(initDataYearId.includes(belong.school_class.term.uuid)){
                                    currentYearGrade = true
                                }

                                if(result.belongs?.length > 1 && initDataYearId.includes(belong.school_class.term.uuid)){
                                    if(belong.school_class.grade.code != config.USERS_GRADE_CODE_SKIP) {
                                        belongIndex = index
                                        userGrade = belong.school_class.grade.code
                                        gradeUser.push(userGrade)
                                    }
                                }
                            })
                            
                            gradeUser = gradeUser.filter((v, i, a) => a.indexOf(v) === i);
                            userGrade = ((result.belongs[belongIndex].school_class.grade.code == config.USERS_GRADE_CODE_SKIP) || !currentYearGrade || gradeUser.length > 1) ? null : result.belongs[belongIndex].school_class.grade.code;

                            let insertUserDatPayload = {
                                id:`${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                sourcedId:result.uuid,
                                uuid:result.uuid,
                                status:DEFAULT_USERS_STATUS,
                                dateLastModified:`${moment.unix(result.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                enabledUser:"true",
                                orgSourcedIds:result.belongs[belongIndex].school_class.organization.uuid || "-",
                                role:result.belongs[belongIndex].role.permission_code || "-",
                                username:result.login_id, 
                                givenName:result.last_name,
                                familyName:result.first_name,
                                email:result.email,
                                grades:userGrade ? cleanString(userGrade?.replace(/"/g,'""')) : "",
                                // password:item.password,
                                municipalId,
                                yearId:result.belongs[belongIndex].school_class.term.uuid,
                                metadataJpKanaGivenName:item?.import_users?.metadataJpKanaGivenName,
                                metadataJpKanaFamilyName:item?.import_users?.metadataJpKanaFamilyName,
                                metadataJpKanaMiddleName:item?.import_users?.metadataJpKanaMiddleName,
                                metadataJpHomeClass:result.belongs[belongIndex].school_class.uuid, 
                                importSourcedId:item?.import_users?.sourcedId,
                                isLocal:item.is_local, 
                            } 
                            await db[municipalId].users.bulkCreate([insertUserDatPayload]).then((item) => {
                                return item
                            }).catch((err) => {
                                let validationError = JSON.parse(JSON.stringify(err))?.original
                                logData = {logFor: "USER_COLLATION",error:validationError?.sqlMessage,message:lang.t('submit_lgate.message.insert',{TABLE:'users'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                LOG.create({type: "INSERT_USER", logData});
                            })
                            // CREATE USER IF SUBMIT LGATE SUCCESS  T_SUBMIT -- end

                            // INSERT TO ENROLLMENT TABEL T_SUBMIT -- start
                            if (insertEnrolmentDatPayloads.length > 0) {
                                await db[municipalId].enrollments.bulkCreate(insertEnrolmentDatPayloads).then((item) => {
                                }).catch((err) => {
                                    let validationError = JSON.parse(JSON.stringify(err))?.original
                                    logData = {logFor: "ENROLEMENT_COLLATION",message:lang.t('submit_lgate.message.insert',{TABLE:'enrollments'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                    LOG.create({type: "INSERT_ENROLMENT", logData});
                                })
                            }
                            // INSERT TO ENROLLMENT TABEL T_SUBMIT -- end

                            // INSERT TO ROLE TABEL T_SUBMIT -- start 
                            let tmp_role_id = `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`
                            let insertRoleDatPayloads = {
                                id: tmp_role_id,
                                sourcedId: uuidv5("ROLES",result.uuid) || tmp_role_id,
                                status:item?.import_role?.status ||DEFAULT_ROLES_STATUS,
                                dateLastModified: `${moment.unix(result.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                userSourcedId: result.uuid || "-",
                                roleType: DEFAULT_ROLE_TYPE,
                                role: result.belongs[belongIndex].role.permission_code || "-",
                                beginDate:item?.import_role?.beginDate || null,
                                endDate:item?.import_role?.endDate || null,
                                orgSourcedId: result.belongs[belongIndex].school_class.organization.uuid || "-",
                                userProfileSourcedId:item?.import_role?.userProfileSourcedId,
                                municipalId,
                                yearId: result.belongs[belongIndex].school_class.term.uuid,
                                toBeDeleted:item?.import_role?.toBeDeleted || 0,
                                hardDelete: item.is_local
                            };

                            await  db[municipalId].roles.bulkCreate([insertRoleDatPayloads]).then((item) => {
                            }).catch((err) => {
                                let validationError = JSON.parse(JSON.stringify(err))?.original
                                logData = {logFor: "ROLE_COLLATION",errors:validationError?.sqlMessage,message:lang.t('submit_lgate.message.insert',{TABLE:'roles'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                LOG.create({type: "INSERT_ROLE", logData});
                            }) 
                            // INSERT TO ROLE TABEL T_SUBMIT -- end 
                        }
                    }     
                }
            } else if(option == 'update') {
                params.is_local = params?.is_local == 1 ? true : false;
                if(!item.password) {
                    delete params.password
                }
                const paramsSend = { ...params };
                delete paramsSend.import_users;
                delete paramsSend.import_role;
                API = await updateUser(item.oldSourcedId, municipalId, paramsSend, jobData);
                logData.api = API.response?.url, 
                logData.param = params,
                logData.executionTime = API.response?.headers['request-duration']
                logData.response = JSON.stringify(API)

                if (API.status == 0) {
                    response.result.errors.default = `${response?.result?.errors?.default} ${API.error?.response?.status} ${API.error?.response?.statusText}`
                    logData.message = lang.t(`submit_lgate.message.error_${option}`).replace('%TABLE%',step);
                } else {
                    response = API.response?.data
                    if(response.is_successful){
                        const {result} = response;
                        
                        let academicSessionSelected = await db[municipalId].academicSessions.findAll({
                            attributes: ["title","sourcedId","endDate","startDate"],
                            where: {
                                title : { [Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                                startDate :{ [Op.lte]: moment.unix(result.updated_at).utc().format('YYYY-MM-DD') },
                                endDate : { [Op.gte]: moment.unix(result.updated_at).utc().format('YYYY-MM-DD') },
                                municipalId : { [Op.eq]: municipalId}
                            }
                        })     
                        const initDataYearId = [];
                        academicSessionSelected.map((item)=>{
                            if(!initDataYearId.includes(item.sourcedId)){
                                initDataYearId.push(item.sourcedId)
                            }
                        })
                        
                        if(result.belongs?.length > 0){
                            let belongIndex = 0;
                            let userGrade = null;
                            let gradeUser = [];
                            let currentYearGrade = false;
                            const activeEnroll = [];
                            const activeClass = [];
                            await Promise.all(result.belongs.map(async (belong,index)=>{
                                activeEnroll.push(belong.uuid);
                                activeClass.push(belong.school_class.uuid);
                                // get enrollment
                                const cekDataEnroll = await db[municipalId].enrollments.findAll({ 
                                    where : {
                                        sourcedId: belong.uuid
                                    }
                                })

                                if (cekDataEnroll.length) {
                                    await db[municipalId].enrollments.update({
                                        dateLastModified:`${moment.unix(belong.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                        userSourcedId:result.uuid,
                                        role: belong.role.permission_code,
                                        beginDate: `${moment.unix(belong.start_at).utc().format("YYYY-MM-DD")}`,
                                        endDate: `${moment.unix(belong.end_at).utc().format("YYYY-MM-DD")}`,
                                        classSourcedId: belong.school_class.uuid || "-",
                                        schoolSourcedId: belong.school_class.organization.uuid || "-",
                                        municipalId,
                                        yearId: belong.school_class.term.uuid,
                                        metadataJpShussekiNo: belong.role.permission_code === 'teacher' || belong.number == '' || belong.number == null ? "": belong.number,
                                        toBeDeleted:0,
                                        hardDelete:item.is_local
                                    },{where:{sourcedId:belong.uuid}}).then((item) => {
                                    }).catch((err) => {
                                        let validationError = JSON.parse(JSON.stringify(err))?.original
                                        logData = {logFor: "ENROLMENT_COLLACTION",message:lang.t('submit_lgate.message.update',{TABLE:'enrollments'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                        LOG.create({type: "UPDATE_ENROLLMENT", logData});
                                    });
                                } else {
                                    await db[municipalId].enrollments.bulkCreate([{
                                        id: `${moment().format("YYYYMMDDHHmmss")}-${uuidv4()}`,
                                        sourcedId: belong.uuid || "-",
                                        uuid: belong.uuid,
                                        status: DEFAULT_ENROLLMENTS_STATUS || 'active',
                                        dateLastModified: `${moment.unix(belong.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                        classSourcedId: belong.school_class.uuid || "-",
                                        schoolSourcedId: belong.school_class.organization.uuid || "-",
                                        userSourcedId: result.uuid || "-",
                                        role: belong.role.permission_code || "-",
                                        primary: belong.role.permission_code === 'teacher' ? 'true':'false',
                                        beginDate: `${moment.unix(belong.start_at).utc().format("YYYY-MM-DD")}`,
                                        endDate: `${moment.unix(belong.end_at).utc().format("YYYY-MM-DD")}`,
                                        municipalId: municipalId,
                                        yearId: belong.school_class.term.uuid,
                                        metadataJpShussekiNo: belong.role.permission_code === 'teacher' || belong.number == '' || belong.number == null ? "": belong.number,
                                        metadataJpPublicFlag: "",
                                        hardDelete: item.is_local
                                    }]).then((item) => {
                                    }).catch((err) => {
                                        let validationError = JSON.parse(JSON.stringify(err))?.original
                                        logData = {logFor: "ENROLEMENT_COLLATION",message:lang.t('submit_lgate.message.insert',{TABLE:'enrollments'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                        LOG.create({type: "INSERT_ENROLMENT", logData});
                                    })
                                }
                                // EDIT USERS ENROLMENT -- end
                                
                                if(initDataYearId.includes(belong.school_class.term.uuid)){
                                    currentYearGrade = true
                                }

                                if(result.belongs?.length > 1 && initDataYearId.includes(belong.school_class.term.uuid)){
                                    if(belong.school_class.grade.code != config.USERS_GRADE_CODE_SKIP) {
                                        belongIndex = index
                                        userGrade = belong.school_class.grade.code
                                        gradeUser.push(userGrade)
                                    }
                                }
                            }));

                            //update status lgate master
                            if (activeEnroll.length > 0) {
                                const queryUpdate = `
                                    UPDATE enrollments SET status = 'tobedeleted' WHERE userSourcedId = '${result.uuid}' AND sourcedId NOT IN ( ${JSON.stringify(activeEnroll).replace("[","").replace("]","")} )
                                `;
                                await db[municipalId].query(queryUpdate);
                            }
                            //update relEnrollment
                            if (activeEnroll.length > 0) {
                                const queryUpdateRel = `
                                    DELETE FROM rel_enrollments WHERE importUserSourcedId = '${item.oldSourcedId}' AND rosterClassSourcedId NOT IN ( ${JSON.stringify(activeClass).replace("[","").replace("]","")} )
                                `;
                                await db[municipalId].query(queryUpdateRel);
                            }
                            
                            gradeUser = gradeUser.filter((v, i, a) => a.indexOf(v) === i);
                            userGrade = ((result.belongs[belongIndex].school_class.grade.code == config.USERS_GRADE_CODE_SKIP) || !currentYearGrade || gradeUser.length > 1) ? null : result.belongs[belongIndex].school_class.grade.code;

                            // EDIT USERS DETAIL -- start 
                            await db[municipalId].users.update({
                                dateLastModified:`${moment.unix(result.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                givenName:result.last_name,
                                familyName:result.first_name, 
                                email:result.login_id,   
                                is_local : result.is_local,
                                username:result.login_id,
                                role:result.belongs[belongIndex].role.permission_code || "-", 
                                grades:userGrade ? cleanString(userGrade?.replace(/"/g,'""')) : "",
                                yearId:result.belongs[belongIndex].school_class.term.uuid,
                                metadataJpKanaGivenName:item?.import_users?.metadataJpKanaGivenName,
                                metadataJpKanaFamilyName:item?.import_users?.metadataJpKanaFamilyName,
                                metadataJpKanaMiddleName:item?.import_users?.metadataJpKanaMiddleName,
                                metadataJpHomeClass:result.belongs[belongIndex].school_class.uuid, 
                            },{where:{sourcedId:result.uuid}}).then((item) => {
                                
                            }).catch((err) => {
                                let validationError = JSON.parse(JSON.stringify(err))?.original
                                logData = {logFor: "USER_COLLACTION",message:lang.t('submit_lgate.message.update',{TABLE:'users'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                LOG.create({type: "INSERT_USER", logData});
                            });
                            
                            // EDIT USERS ROLE -- start
                            await db[municipalId].roles.update({ 
                                sourcedId:item?.import_role?.sourcedId,
                                dateLastModified: `${moment.unix(result.updated_at).utc().format('YYYY-MM-DD HH:mm:ss.SSS')}`,
                                userSourcedId:result.uuid,
                                roleType:item?.import_role?.roleType || DEFAULT_ROLE_TYPE,
                                role: result.belongs[belongIndex].role.permission_code || "-",
                                beginDate:item?.import_role?.beginDate,
                                endDate:item?.import_role?.endDate,
                                userProfileSourcedId:item?.import_role?.userProfileSourcedId,
                                municipalId:item.municipalId,
                                yearId: result.belongs[belongIndex].school_class.term.uuid,
                                toBeDeleted:item?.import_role?.toBeDeleted || 0,
                                hardDelete:1
                            },{where:{userSourcedId:result.uuid}}).then((item) => {
                            }).catch((err) => {
                                let validationError = JSON.parse(JSON.stringify(err))?.original
                                logData = {logFor: "ROLE_COLLACTION",message:lang.t('submit_lgate.message.update',{TABLE:'enrollments'}).replace('%MESSAGE%',validationError?.sqlMessage)}
                                LOG.create({type: "UPDATE_ROLE", logData});
                            });
                            // EDIT USERS ROLE -- end
                        }
                    }
                }
            } else if(option == 'delete') {
            }

            if(response){
                response.info = `${step} section error on [${item.login_id}] `
                if(response.is_successful){
                    logData.message = lang.t(`submit_lgate.message.${option}`).replace('%TABLE%',step);
                    let result = response.result
                    
                    await db[municipalId].lgateUsers.update({
                        newSourcedId : result.uuid,
                        submited : 1
                    },{
                        where : {
                            oldSourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].users.update({
                        sourcedId: result.uuid,
                        uuid: result.uuid,
                    },{
                        where : {
                            sourcedId : item.oldSourcedId
                        }
                    })

                    await db[municipalId].relUsers.update({
                        rosterSourcedId: result.uuid,
                        isTemp: 0
                    },{
                        where : {
                            rosterSourcedId : item.oldSourcedId
                        }
                    })

                    if (Array.isArray(result.belongs)) {
                        await Promise.all(result.belongs.map(async (belong)=>{
                            await db[municipalId].enrollments.update({
                                userSourcedId: result.uuid,
                                sourcedId: belong.uuid
                            },{
                                where : {
                                    userSourcedId : item.oldSourcedId,
                                    classSourcedId : belong.school_class.uuid,
                                }
                            })

                            await db[municipalId].relEnrollments.update({
                                rosterUserSourcedId: result.uuid,
                                rosterSourcedId: belong.uuid
                            },{
                                where : {
                                    rosterUserSourcedId : item.oldSourcedId,
                                    rosterClassSourcedId : belong.school_class.uuid,
                                }
                            })
                        }))
                    }
                } else {
                    logData.message = lang.t(`submit_lgate.message.failed_${option}`).replace('%TABLE%',step);
                }
            }
            
            LOG.create({type: SUBMIT_TO_LGATE,logData});
            break;
        
        case 'skipped_users' :

            logData = {
                logFor: 'SUBMIT_SKIPPED_USERS_TO_DB',
            }
            
            if (item?.isParentSkiped !== 1) {
            //cek to skipped import users
            await db[municipalId].skipedImportUsers.destroy({
                where : {
                    municipalId : municipalId,
                    sourcedId : item.sourcedId
                }
            })

            const isUnregisteredUser = item?.classSourcedId ? item?.classSourcedId : false;
            delete item.classSourcedId;
            delete item.classSourcedName;
            delete item.yearSelected;
            delete item.isParentSkiped;
            const skippedUsersArray = [item];
            await db[municipalId].skipedImportUsers.bulkCreate(skippedUsersArray);

            // get import enrollments
            const arrSkippedEnrollment = [];
            if (isUnregisteredUser) {
                let enrollmentSourcedId = uuidv4();
                arrSkippedEnrollment.push({
                    sourcedId: enrollmentSourcedId,
                    classSourcedId: isUnregisteredUser,
                    schoolSourcedId: item?.orgSourcedIds,
                    userSourcedId: item.sourcedId,
                    role: item?.role,
                    primary: item?.role === 'teacher' ? 'true':'false',
                    beginDate: `${moment.utc().format("YYYY-MM-DD")}`,
                    endDate: `${moment.utc().format("YYYY-MM-DD")}`,
                    metadataJpShussekiNo: '',
                    metadataJpPublicFlag: '',
                    municipalId,
                    isDelta: item?.isDelta,
                    submited: 0,
                });
            } else {
                const queryGetSkippedEnrollment = await db[municipalId].importEnrollments.findAll({
                    where : {
                        municipalId : municipalId,
                        userSourcedId : item.sourcedId,
                        isParentSkiped: 0,
                        option : {[Op.ne] : 'skip_csv_to_lgate'}
                    }
                });

                queryGetSkippedEnrollment.map(valitem => {
                    arrSkippedEnrollment.push({
                        sourcedId: valitem?.sourcedId,
                        classSourcedId: valitem?.classSourcedId,
                        schoolSourcedId: valitem?.schoolSourcedId,
                        userSourcedId: valitem?.userSourcedId,
                        role: valitem?.role,
                        primary: valitem?.primary,
                        beginDate: valitem?.beginDate,
                        endDate: valitem?.endDate,
                        metadataJpShussekiNo: valitem?.metadataJpShussekiNo,
                        metadataJpPublicFlag: valitem?.metadataJpPublicFlag,
                        municipalId: valitem?.municipalId,
                        isDelta: valitem?.isDelta,
                        submited: 0,
                    });
                })
            }

            await db[municipalId].skipedImportEnrollments.destroy({
                where : {
                    municipalId : municipalId,
                    userSourcedId : item.sourcedId
                }
            })
            await db[municipalId].skipedImportEnrollments.bulkCreate(arrSkippedEnrollment).then((item) => {
            }).catch((err) => {
                console.log(err)
                logData.message = lang.t(`submit_lgate.message.failed_insert`).replace('%TABLE%',step);
            })
            }
            
            LOG.create({type: SUBMIT_TO_LGATE,logData});
            response.is_successful = true;
            break;

        default :
            response = false
            break;
    }
    return response
}

/**
 * Get total of data from lgate table and redis
 * @constructor
 */
const getCountData = async (step,municipalId) => {
    let result;

    switch (step) {
        case 'organization' :
            result = await db[municipalId].lgateOrganization.findAll({
                where : {
                    municipalId : municipalId,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                }
            });
            result = result.length
            break;
          
        case 'classes' :
            result = await db[municipalId].lgateClasses.findAll({
                where : {
                    municipalId : municipalId,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                    isParentSkiped : 0,
                }
            });
            result = result.length
            break;

        case 'users' :
            result = await db[municipalId].lgateUsers.findAll({
                where : {
                    municipalId : municipalId,
                    option : {[Op.ne] : 'delete'},
                    submited : 0,
                    isParentSkiped : 0,
                }
            });
            result = result.length
            break;
        
        case 'skipped_users' :
            let redisSkippedData = await redisClient.get(`SKIPPED_USERS_${municipalId}`);
            redisSkippedData = redisSkippedData ? JSON.parse(redisSkippedData) : [];
            result = redisSkippedData.length
            break;
    
        default :
            step = 'end'
            result = 0
            break;
    }
    
    return result
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
 * Processing bull job of submit to lgate process
 * @constructor
 */
class SubmitToLgate {
    onProcess = async (job,done,initData = null,stepIndex=0, limit=10, offset=0) => {
        const param = job.data;
        
        if(!initData){
            initData = {
                total_row : 0,
                progress_row : 0,
                jobProgress : {
                    current : '',
                    message: '',
                    data: {}
                },
                err : []
            }
        }

        let finishedStep = false;
        if (step[stepIndex] === "users_update_role") {
            const getOrgs = await db[param.municipalId].importOrgs.findAll({ 
                where: { municipalId: param.municipalId },
                include: [
                    {
                        model: db[param.municipalId].relOrgs,
                        attributes: ["rosterSourcedId"],
                    }, 
                ]
            });

            if (getOrgs.length > 0) {
                if (!job.data.progressRoleStart) job.data.progressRoleStart = false;
                if (!job.data.progressRoleInsert) job.data.progressRoleInsert = 0;
                if (!job.data.progressRoleStart) {
                    await Promise.all(
                        getOrgs.map(async (item) => {
                            const getLgateOrgs = await db[param.municipalId].lgateRole.findAll({ where: { organization_uuid: item.rel_org.rosterSourcedId, municipalId: param.municipalId } });
                            if (getLgateOrgs.length < 1) {
                                job.data.progressRoleStart = true;
                                let Roles = await getRoles(param.municipalId, item.rel_org.rosterSourcedId, param);
                                if (Roles) {
                                    await db[param.municipalId].lgateRole.bulkCreate(Roles);
            
                                    let query = `
                                        UPDATE 
                                            lgate_enrollments,
                                            lgate_role 
                                        SET  
                                            lgate_enrollments.role_uuid = lgate_role.role_uuid 
                                        WHERE
                                            lgate_enrollments.role = lgate_role.permission_code 
                                            AND lgate_enrollments.organization_uuid = lgate_role.organization_uuid
                                    `;
                                    await db[param.municipalId].query(query);
                                    job.data.progressRoleInsert++;
                                }
                            } else {
                                job.data.progressRoleInsert++;
                            }
                            
                            if (job.data.progressRoleInsert === getOrgs.length) {
                                finishedStep = true;
                            }
                        })
                    );
                }
            }else{
                finishedStep = true;
            }
        } else {
            const data = await getParamData(step[stepIndex],param.municipalId,limit,offset);
            let errors = []

            if(!step[stepIndex]){

                if(initData.err.length){
                    return done({
                        status :false,
                        errors : initData.err
                    })
                }
                
                return done(null,{
                    status : true,
                    data : []
                })
            }
        
            if(offset == 0){
                initData.total_row = await getCountData(step[stepIndex],param.municipalId)
                initData.progress_row = 0
            }

            if(data.result?.length && initData.total_row >= offset){
                await Promise.all(
                    data.result.map(async (item) => {
                        let response = await submitApi(param.municipalId,data.step,item.option,item,param);
                        if(response.is_successful == true){
                            ++initData.progress_row
                        } else if(response.is_successful == false){
                            initData.err.push({
                                is_successful : response.is_successful,
                                info : response.info,
                                result : response.result
                            })
                        } else {
                            initData.err.push({
                                is_successful : false,
                                info : `${step} section error`,
                                result : {
                                    message: `failed connect ${step}`,
                                    errors: {
                                        default: [
                                            `failed connect ${step}`
                                        ]
                                    }
                                }
                            })
                        }
                    })
                )
                offset = offset+limit
            } else {
                finishedStep = true;
            }
        }

        initData.jobProgress.current = step[stepIndex]
        initData.jobProgress.data[step[stepIndex]] = {total_row:initData.total_row,progress_row:initData.progress_row,is_calculating:false}
        
        if (finishedStep) {
            ++stepIndex
            offset = 0
        }

        job.progress( initData.jobProgress )

        await this.onProcess(job,done,initData,stepIndex,limit,offset);
    }

    onActive = async (job, jobPromise) => {
        LOG.create({type: SUBMIT_TO_LGATE,message : 'JOB START', param : job.data});
        console.log('active',job.id)
    }

    onWaiting = async (jobId) => {
        LOG.create({type: SUBMIT_TO_LGATE,message : 'JOB WAITING'});
        console.log('waiting',jobId)
    }

    onError = async (error) => {
        LOG.create({type: SUBMIT_TO_LGATE,message : 'JOB ERROR'});
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
        LOG.create({type: SUBMIT_TO_LGATE,message : 'JOB COMPLETED', param : job.data});
        await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
        await redisClient.del(`SKIPPED_USERS_${job.data.municipalId}`);

        await db[job.data.municipalId].relAcademicSessions.update({
            isTemp: 0,
        },{
            where : {
                municipalId : job.data.municipalId,
                isTemp: 1,
            }
        })

        await db[job.data.municipalId].import.destroy({
            where : {
                municipalId : job.data.municipalId
            }
        })
        console.log('completeds',job.id, result)
    }

    onFailed = async (job, err) => {
        LOG.create({type: SUBMIT_TO_LGATE,message : 'JOB FAILED', param : job.data});
        job.moveToCompleted(err,true)
        console.log('failed',job.id,err) 
    }
    
}

/**
 * Create export variable to running function SubmitToLgate
 * @constructor
 */
const SubmitToLgateProcess = new SubmitToLgate()

export default SubmitToLgateProcess