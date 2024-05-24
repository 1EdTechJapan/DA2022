import moment from 'moment';
import { v4 as uuidv4 } from "uuid";
import config from "../../config/config.js";
import {db} from "../../models/index.js";
import lang from '../../i18n.js';
import { readCsv } from '../../helpers/import.js';
import { convertToSingleByte, convertDateForInsert } from '../../helpers/utility.js';
import redisClient from "../../redisClient.js";
import {
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PROCESSING,
    STATUS_WAITING,
    TABLE_NAME_ACADEMIC_SESSIONS,
    TABLE_NAME_ORGS,
    TABLE_NAME_COURSES,
    TABLE_NAME_CLASSES,
    TABLE_NAME_GROUPS,
    TABLE_NAME_USERS,
    TABLE_NAME_ROLES,
    TABLE_NAME_ENROLLMENTS,
    IMPORT_CSV,
    IMPORT_EMPTY_DELTA,
    YEAR_COLLATION,
    SCHOOL_COLLATION,
    CLASS_COLLATION,
    OTHER_CLASS_COLLATION,
    COURSES_COLLATION,
    ADMINISTRATOR_COLLATION,
    CLASS_ATENDANCE_COLLATION,
    OTHER_ATENDANCE_COLLATION,
    ADMIN_TEACHER_COLLATION,
    STUDENT_COLLATION,
    USER_ASSIGNMENT_SCREEN,
    USER_CONFIRMATION_SCREEN,
    GET_DELTA_ORGS,
    GET_DELTA_YEAR,
    SCHOOL_TYPE_LIST,
    IMPORT_DELTA_MERGE,
    FILL_USER_PRIMARY_ORGS,
    CHECK_SOURCED_ID
} from "../../constants/constans.js";
import { mergedUsersImport } from "./SubmitClassesProcess.js";
import { mergedUsersGroup } from "./SubmitGroupProcess.js";
import { mergedClassImport } from "../../controllers/school_collation.controller.js";
import { processDiscardImport } from "../../controllers/import.controller.js";
import e from 'cors';
import QueryTypes from "sequelize";

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
 * Process to execute insert query into import table
 * @constructor
 */
const executeQuery = async (type, data, municipalId) => {
    const insetData = await convertEmptyToNull(convertDateForInsert(data,'dateLastModified'));
    switch(type) {
        case TABLE_NAME_ACADEMIC_SESSIONS:
            return await db[municipalId].importAcademicSessions.bulkCreate( insetData, {updateOnDuplicate: ["yearIdLgate","yearLgateName","option","isDelta"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            }) 
        case TABLE_NAME_ORGS:
            
            return await db[municipalId].importOrgs.bulkCreate( insetData, { updateOnDuplicate: ["orgsIdLgate","orgsLgateName", "orgsLgateIdentifier", "option", "identifier","isDelta"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            }) 
        case TABLE_NAME_CLASSES:
            let formatDataInsertClasses = insetData.map(item => ({...item, title: convertToSingleByte(item?.title), metadataJpSpecialNeeds: item?.["metadata.jp.specialNeeds"]}))
            return await db[municipalId].importClasses.bulkCreate( formatDataInsertClasses, { updateOnDuplicate: ["classesIdLgate","classLgateName","option"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            })
        case TABLE_NAME_COURSES:
            return await db[municipalId].importCourses.bulkCreate( insetData, { updateOnDuplicate: ["sourcedId"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            })
        case TABLE_NAME_USERS:
            let formatDataInsertUser = insetData.map(item => ({...item, orgSourcedIds: item?.["primaryOrgSourcedId"]?item?.["primaryOrgSourcedId"]:item?.["orgSourcedIds"], metadataJpKanaGivenName: item?.["metadata.jp.kanaGivenName"], metadataJpKanaFamilyName: item?.["metadata.jp.kanaFamilyName"], metadataJpKanaMiddleName: item?.["metadata.jp.kanaMiddleName"], metadataJpHomeClass: item?.["metadata.jp.homeClass"]}))
            return await db[municipalId].importUsers.bulkCreate( formatDataInsertUser, { updateOnDuplicate: ["userIdLgate","userLgateName","userLgatePassword","option"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            })
        case TABLE_NAME_ROLES:
            return await db[municipalId].importRoles.bulkCreate( insetData, { updateOnDuplicate: ["sourcedId"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            })
        case TABLE_NAME_ENROLLMENTS:
            let formattedDataInsertEnroll = insetData.map(item => ({...item, option: "update_csv_to_lgate", metadataJpShussekiNo: item?.["metadata.jp.ShussekiNo"], metadataJpPublicFlag: item?.["metadata.jp.PublicFlg"]}))
            return await db[municipalId].importEnrollments.bulkCreate( formattedDataInsertEnroll, { updateOnDuplicate: ["sourcedId"] } ).then((item) => {
                return {status:true, message: `${type} success insert`}
            }).catch((err) => {
                let validationError = JSON.parse(JSON.stringify(err))?.original
                return {status:false, message:validationError.sqlMessage}
            })
    }
}

/**
 * Process to delete data from import table
 * @constructor
 */
const clearImportData = async (type,municipalId) => {
    switch(type) {
        case TABLE_NAME_ACADEMIC_SESSIONS:
            return await db[municipalId].importAcademicSessions.destroy({
                where: { municipalId: municipalId }
            })
        case TABLE_NAME_ORGS:  
            return await db[municipalId].importOrgs.destroy({
                where: { municipalId: municipalId }
            })
        case TABLE_NAME_CLASSES:
            return await db[municipalId].importClasses.destroy({
                where: { municipalId: municipalId }
            })

        case TABLE_NAME_COURSES:
            return await db[municipalId].importCourses.destroy({
                where: { municipalId: municipalId }
            })

        case TABLE_NAME_USERS:
            return await db[municipalId].importUsers.destroy({
                where: { municipalId: municipalId }
            })

        case TABLE_NAME_ROLES:
            return await db[municipalId].importRoles.destroy({
                where: { municipalId: municipalId }
            })

        case TABLE_NAME_ENROLLMENTS:
            return await db[municipalId].importEnrollments.destroy({
                where: { municipalId: municipalId }
            })

    }
}

/**
 * Process to change empty value to null
 * @constructor
 */
const convertEmptyToNull = async(arr) => {
    return arr.map((object) => {
        if(typeof object == 'object'){
            for(let key in object) {
                if(object[key] === "") object[key] = null
            }
        } else {
            if(object === "") object = null
        }
        return object
    })
}

/**
 * Process to import read data from csv file
 * @constructor
 */
const importCSV = async (municipalId,data,index=0,percent=0,job,jobProgress) => {
    let chunk = config.IMPORT_CSV_CHUNK;
    if(!data?.csvChunk){
        data.csvChunk = arrayChunk(data.csv,chunk)
    }
    let insert;

    if(index === 0){
        await clearImportData(data.table,municipalId)
    }
    if(data?.csvChunk){
        if(data?.csvChunk[index]?.length > 0){
            let dataInsert = data.csvChunk[index]
            let diff = chunk - dataInsert.length
            let dataProgress = (chunk * (index+1)) - diff

            insert = await executeQuery(data.table,dataInsert, municipalId)
            if(insert?.status){
                percent = (dataProgress/data.csv.length) * 100;
            }
            jobProgress.data[data.table] = {total_row:data.csv.length,progress_row:dataProgress,is_calculating:false}
            await job.progress(jobProgress)
            return await importCSV(municipalId,data,++index,percent,job,jobProgress)
        } else {
            return true
        }
    } else {
        return true
    }
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
 * Process to merged data of import_academic_sessions table with data from academic_sessions table
 * @constructor
 */
const mergedAcademicSessions = async (municipalId) => {
    let queryImport = await db[municipalId].importAcademicSessions.findAll({
        where: { municipalId: municipalId }
    })
    let sourcedId = [],startDate = [], schoolYear = [];
    
    queryImport.map(function(row) { 
        sourcedId.push(row.sourcedId); 
        startDate.push(row.startDate);
        schoolYear.push(row.schoolYear);
    });

    let queryLgate = await db[municipalId].academicSessions.findAll({
        attributes: {
            exclude : ["importSourcedId"]
        },
        include : [{
            model: db[municipalId].relAcademicSessions,
            required : false
        }],
        where: { 
            [Op.or]: [
                {
                    startDate: {
                        [Op.in]: startDate
                    }
                },{
                    schoolYear: {
                        [Op.in]: schoolYear
                    }
                },
                {
                    "$rel_academic_session.importSourcedId$": { [Op.in]: sourcedId },
                }
            ],
            [Op.and]: [
               { municipalId: municipalId }
            ]
        },
    })

    let queryMerged = queryImport.map(function(row) { 
        // sourcedId Check
        row.isDelta = 0;

        let lgateIndex = -1;
        if(lgateIndex < 0){
            lgateIndex = queryLgate.findIndex((item)=>item.rel_academic_session.importSourcedId == row.sourcedId);
            if(lgateIndex < 0){
                lgateIndex = queryLgate.findIndex((item)=>item.startDate == row.startDate);
                if(lgateIndex < 0){
                    lgateIndex = queryLgate.findIndex((item)=>item.schoolYear == row.schoolYear);
                }
            }else{
                row.isDelta = 1;
            }
        }

        if(lgateIndex < 0){
            row.yeadIdLgate = null
            row.yearLgateName = null
            row.option = 'add_csv_to_lgate'
        } else {
            row.yearIdLgate = queryLgate[lgateIndex].sourcedId
            row.yearLgateName = queryLgate[lgateIndex].title
            row.option = 'update_csv_to_lgate'
        }
        row.submited = 1
        return row
    });

    return queryMerged;
}

/**
 * Process to merged data of import_orgs table with data from orgs table
 * @constructor
 */
const mergedSchool = async (municipalId) => {
    let queryImport = await db[municipalId].importOrgs.findAll({
        where: { municipalId: municipalId }
    })
    let sourcedId = [],name = [];
    
    queryImport.map(function(row) { 
        sourcedId.push(row.sourcedId); 
        name.push(row.name);
    });

    let queryLgate = await db[municipalId].orgs.findAll({
        attributes: {
            exclude : ["importSourcedId"]
        },
        include : [{
            model: db[municipalId].relOrgs,
            required : false
        }],
        where: { 
            [Op.or]: [
                {
                    name: {
                        [Op.in]: name
                    }
                },
                {
                    "$rel_org.importSourcedId$": { [Op.in]: sourcedId },
                }
            ],
            [Op.and]: [
               { municipalId: municipalId }
            ]
        }
    })

    let queryMerged = queryImport.map(function(row) { 
        row.isDelta = 0;
        // sourcedId Check
        let lgateIndex = -1;
        if(lgateIndex < 0){
            lgateIndex = queryLgate.findIndex((item)=>item.rel_org.importSourcedId == row.sourcedId);
            if(lgateIndex < 0){
                lgateIndex = queryLgate.findIndex((item)=>item.name == row.name);
            }else{
                row.isDelta = 1;
            }
        }

        if(lgateIndex < 0){
            let iden = SCHOOL_TYPE_LIST[0]?.key;
            for (var i = SCHOOL_TYPE_LIST.length - 1; i >= 0; i--) {
                if (row.identifier == SCHOOL_TYPE_LIST[i].name || row.identifier == SCHOOL_TYPE_LIST[i].key) {
                    iden = SCHOOL_TYPE_LIST[i]?.key;
                }
            }
            row.orgsIdLgate = null
            row.orgsLgateName = null
            row.orgsLgateIdentifier = null
            row.identifier = iden
            row.option = 'add_csv_to_lgate'
        } else {
            row.orgsIdLgate = queryLgate[lgateIndex].sourcedId
            row.orgsLgateName = queryLgate[lgateIndex].name
            row.orgsLgateIdentifier = queryLgate[lgateIndex].identifier
            row.identifier = queryLgate[lgateIndex].identifier
            row.option = 'update_csv_to_lgate'
        }
        row.submited = 1
        return row
    });

    return queryMerged;
}
let processStatus = true;
let processMsg = [];

/**
 * Processing bull job for import data from csv files
 * @constructor
 */
class ImportProcess {
    onProcess = async (job,done,csvMerged=false,index=0,timeout=0) => {
        let status = STATUS_PROCESSING;
        let lockJobMunicipal = await redisClient.get(`LOCK_IMPORT_${job.data.municipalId}`);
        let errmessage = ""
        switch(job.data.type) {
            case IMPORT_CSV:
                if (!processStatus) processStatus = true;
                if (processStatus) {
                    await redisClient.set(`LOCK_IMPORT_${job.data.municipalId}`, 1);
                }
                let importSuccess = 0
                let percent = 0
                let jobProgress = {
                    current : '',
                    message: '',
                    data: {}
                }
                if(job.data.data.length > 0){
                    await Promise.all(job.data.data.map(async (item) => {
                        let counter;
                        switch(item.table){
                            case TABLE_NAME_ACADEMIC_SESSIONS:
                                item.totalCsv = 0;
                                item.csv = await readCsv(`${item.path}academicSessions.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_ACADEMIC_SESSIONS] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_ORGS:
                                item.totalCsv = 0;
                                counter = 0;
                                item.csv = await readCsv(`${item.path}orgs.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        counter++
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        if (!["school","district"].includes(row.type)) {
                                            jobProgress.message += `[orgs.csv] - ROW ${counter} - type [${row.type}] is not supported, the value will be directly change to [school]\n`
                                            row.type = "school"
                                        }
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_ORGS] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_CLASSES:
                                item.totalCsv = 0;
                                counter = 0;
                                item.csv = await readCsv(`${item.path}classes.csv`, { headers: true }, async (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        counter++
                                        row.grades = !row.grades ? 'zz' : row.grades;
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        if (!["homeroom","scheduled"].includes(row.classType)) {
                                            jobProgress.message += `[classes.csv] - ROW ${counter} - type [${row.classType}] is not supported, the value will be directly change to [homeroom]\n`
                                            row.type = "homeroom"
                                        }
                                        
                                        //cek multiple grade
                                        const expGrade = row.grades.split(",");
                                        if (expGrade.length > 1) {
                                            jobProgress.message += `[classes.csv] - ROW ${counter} - grade [${row.grades}] is not supported, the value will be directly change to [zz]\n`
                                            row.grades = "zz";
                                        }

                                        //cek multiple term
                                        const expTerm = row.termSourcedIds.split(",");
                                        if (expTerm.length > 1) {
                                            processMsg.push(`[classes.csv] - ROW ${counter} - termSourcedIds [${row.termSourcedIds}] is not supported`);
                                            processStatus = false;
                                        }
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_CLASSES] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_COURSES:
                                let classCsv = await readCsv(`${item.path}classes.csv`, { headers: true }, (row) => {
                                    if (row.status !== 'tobedeleted') {
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        return row
                                    }
                                })
                        
                                item.totalCsv = 0;
                                item.csv = await readCsv(`${item.path}courses.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        let classindex = classCsv.findIndex( (item) => item.courseSourcedId === row.sourcedId);
                                        if(classindex >= 0){
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        row.classesId = classCsv[classindex].sourcedId
                                        return row
                                        }
                                    }
                                })
                                jobProgress.data[TABLE_NAME_COURSES] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_USERS:
                                counter = 0;
                                item.totalCsv = 0;
                                item.csv = await readCsv(`${item.path}users.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        counter++
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'

                                        if (row.primaryOrgSourcedId) {
                                            //cek multiple school sourced id
                                            const expSchool = row.primaryOrgSourcedId.split(",");
                                            if (expSchool.length > 1) {
                                                processMsg.push(`[users.csv] - ROW ${counter} - primaryOrgSourcedId [${row.primaryOrgSourcedId}] is not supported`);
                                                processStatus = false;
                                            }
                                        }

                                        if (row.orgSourcedIds) {
                                            //cek multiple orgSourcedId
                                            const expOrg = row.orgSourcedIds.split(",");
                                            if (expOrg.length > 1) {
                                                processMsg.push(`[users.csv] - ROW ${counter} - orgSourcedId [${row.orgSourcedIds}] is not supported`);
                                                processStatus = false;
                                            }
                                        }
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_USERS] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_ROLES:
                                item.totalCsv = 0;
                                counter = 0;
                                item.csv = await readCsv(`${item.path}roles.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        counter++
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        if (row.role == 'districtAdministrator') {
                                            row.role = "administrator";
                                        }
                                        if (!['student','teacher','administrator','guardian','districtAdministrator','relative','siteAdministrator','principal'].includes(row.role)) {
                                            jobProgress.message += `[roles.csv] - ROW ${counter} - role [${row.role}] is not supported, the value will be directly change to [student]\n`
                                            row.role = "student"
                                        }
                                        if (row.role) {
                                            //cek multiple role
                                            const expRole = row.role.split(",");
                                            if (expRole.length > 1) {
                                                processMsg.push(`[roles.csv] - ROW ${counter} - role [${row.role}] is not supported`);
                                                processStatus = false;
                                            }
                                        }
                                        if (row.orgSourcedId) {
                                            //cek multiple role
                                            const expOrgSrcId = row.orgSourcedId.split(",");
                                            if (expOrgSrcId.length > 1) {
                                                processMsg.push(`[roles.csv] - ROW ${counter} - orgSourcedId [${row.orgSourcedId}] is not supported`);
                                                processStatus = false;
                                            }
                                        }
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_ROLES] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                            case TABLE_NAME_ENROLLMENTS:
                                item.totalCsv = 0;
                                counter = 0;
                                item.csv = await readCsv(`${item.path}enrollments.csv`, { headers: true }, (row) => {
                                    item.totalCsv++;
                                    if (row.status !== 'tobedeleted') {
                                        counter++
                                        row.municipalId = job.data.municipalId
                                        row.option = 'add_csv_to_lgate'
                                        if (row.role == 'districtAdministrator') {
                                            row.role = "administrator";
                                        }
                                        if (!["student","teacher","administrator"].includes(row.role)) {
                                            jobProgress.message += `[enrollments.csv] - ROW ${counter} - role [${row.role}] is not supported, the value will be directly change to [student]\n`
                                            row.role = "student"
                                        }
                                        return row
                                    }
                                })
                                jobProgress.data[TABLE_NAME_ENROLLMENTS] = {total_row:item.csv.length,progress_row:0,is_calculating:true}
                                break;
                        }
                    }))

                    await Promise.all(job.data.data.map(async (item) => {
                        
                        let importCSVData = true;
                        if(item?.csv?.length){
                            importCSVData = await importCSV(job.data.municipalId,item,0,0,job,jobProgress);
                        } else {
                            jobProgress.data[item.table] = {total_row:item.totalCsv,progress_row:item.totalCsv,is_calculating:false}
                        }
                        if(importCSVData){
                            ++importSuccess
                        } else {
                            errmessage = `csv process ${item.table} failed`
                        }
                        percent = importSuccess/job.data.data.length * 100
                        // await job.progress(percent)
                    }))

                    if(percent == 100){
                        status = STATUS_COMPLETED
                        await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
                    } else {
                        await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
                        status = STATUS_FAILED
                    }
                } else {
                    await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
                    status = STATUS_FAILED
                    errmessage = lang.t('import.message.import_failed_csv');
                }
                break;
            
            case IMPORT_EMPTY_DELTA:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:
                        if (!job.data.stepIndex) job.data.stepIndex = 0;
                        if (!job.data.stepOffset) job.data.stepOffset = 0;

                        const stepDeltaImported = [GET_DELTA_ORGS,GET_DELTA_YEAR,TABLE_NAME_CLASSES,TABLE_NAME_ORGS,TABLE_NAME_ACADEMIC_SESSIONS];
                        if (!job.data.listSchoolAutoImport) job.data.listSchoolAutoImport = [];
                        if (!job.data.listYearAutoImport) job.data.listYearAutoImport = [];

                        const condCurrentStep = job.data.autoImportTable[stepDeltaImported[job.data.stepIndex]];
                        switch (stepDeltaImported[job.data.stepIndex]) {
                            case GET_DELTA_ORGS:
                                if (!job.data.importedTable[TABLE_NAME_ORGS] && !job.data.importedTable[TABLE_NAME_CLASSES]) {
                                    // get list school from users
                                    const query = `
                                        SELECT
                                            rel_orgs.importSourcedId as orgSourcedIds
                                        FROM
                                            import_users
                                        INNER JOIN rel_orgs
                                            ON rel_orgs.importSourcedId = import_users.orgSourcedIds
                                        WHERE 
                                            import_users.municipalId = $bind_municipalId
                                        GROUP BY import_users.orgSourcedIds
                                        LIMIT ${config.IMPORT_CSV_CHUNK} OFFSET ${job.data.stepOffset}
                                    `;
                                    const [getListUser] = await db[job.data.municipalId].query(query,{
                                        bind: { 
                                            bind_municipalId: job.data.municipalId
                                        },
                                        type: QueryTypes.SELECT
                                    });

                                    getListUser.map(async (item) => {
                                        const checkOrgClass = job.data.listSchoolAutoImport.filter(e => e === item.orgSourcedIds);
                                        if (checkOrgClass.length < 1) {
                                            job.data.listSchoolAutoImport.push(item.orgSourcedIds);
                                        }
                                    });

                                    if (getListUser.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }
                                } else if (job.data.importedTable[TABLE_NAME_CLASSES]) {
                                    // get list school from class
                                    const query = `
                                        SELECT
                                            rel_orgs.rosterSourcedId as schoolSourcedId,
                                            rel_academic_sessions.rosterSourcedId as termSourcedIds
                                        FROM
                                            import_classes
                                        INNER JOIN rel_orgs
                                            ON rel_orgs.importSourcedId = import_classes.schoolSourcedId
                                        INNER JOIN rel_academic_sessions
                                            ON rel_academic_sessions.importSourcedId = import_classes.termSourcedIds
                                        WHERE 
                                            import_classes.municipalId = $bind_municipalId
                                        GROUP BY import_classes.schoolSourcedId, import_classes.termSourcedIds
                                        LIMIT ${config.IMPORT_CSV_CHUNK} OFFSET ${job.data.stepOffset}
                                    `;
                                    const [getListClass] = await db[job.data.municipalId].query(query,{
                                        bind: { 
                                            bind_municipalId: job.data.municipalId
                                        },
                                        type: QueryTypes.SELECT
                                    });

                                    getListClass.map((item)=>{
                                        const checkOrgsClass = job.data.listSchoolAutoImport.filter(e => e === item.schoolSourcedId);
                                        if (checkOrgsClass.length < 1) {
                                            job.data.listSchoolAutoImport.push(item.schoolSourcedId);
                                        }
                                        
                                        const checkYearClass = job.data.listYearAutoImport.filter(e => e === item.termSourcedIds);
                                        if (checkYearClass.length < 1) {
                                            job.data.listYearAutoImport.push(item.termSourcedIds);
                                        }
                                    })

                                    if (getListClass.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }
                                } else if (job.data.importedTable[TABLE_NAME_ORGS]) {
                                    // get list school from orgs
                                    const query = `
                                        SELECT
                                            rel_orgs.rosterSourcedId as sourcedId
                                        FROM
                                            import_orgs
                                        JOIN rel_orgs
                                            ON rel_orgs.importSourcedId = import_orgs.sourcedId
                                        WHERE 
                                            import_orgs.municipalId = $bind_municipalId
                                        GROUP BY rel_orgs.rosterSourcedId
                                        LIMIT ${config.IMPORT_CSV_CHUNK} OFFSET ${job.data.stepOffset}
                                    `;
                                    const [getListOrgs] = await db[job.data.municipalId].query(query,{
                                        bind: { 
                                            bind_municipalId: job.data.municipalId
                                        },
                                        type: QueryTypes.SELECT
                                    });

                                    getListOrgs.map(async (item) => {
                                        const checkOrgs = job.data.listSchoolAutoImport.filter(e => e === item.sourcedId);
                                        if (checkOrgs.length < 1) {
                                            job.data.listSchoolAutoImport.push(item.sourcedId);
                                        }
                                    });

                                    if (getListOrgs.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }
                                } else {
                                    job.data.stepIndex++;
                                }
                                break;
                            case GET_DELTA_YEAR:
                                if (job.data.listSchoolAutoImport.length > 0 && (!job.data.importedTable[TABLE_NAME_CLASSES] || (job.data.importedTable[TABLE_NAME_ORGS] && !job.data.importedTable[TABLE_NAME_CLASSES]))) {
                                    // get list year from class
                                    const query = `
                                        SELECT
                                            termSourcedIds
                                        FROM
                                            classes
                                        WHERE 
                                            classes.municipalId = $bind_municipalId
                                            AND classes.schoolSourcedId IN ( ${JSON.stringify(job.data.listSchoolAutoImport).replace("[","").replace("]","")} )
                                        GROUP BY classes.termSourcedIds
                                        LIMIT ${config.IMPORT_CSV_CHUNK} OFFSET ${job.data.stepOffset}
                                    `;
                                    const [getListYear] = await db[job.data.municipalId].query(query,{
                                        bind: { 
                                            bind_municipalId: job.data.municipalId
                                        },
                                        type: QueryTypes.SELECT
                                    });

                                    getListYear.map((item)=>{
                                        const checkYearClass = job.data.listYearAutoImport.filter(e => e === item.termSourcedIds);
                                        if (checkYearClass.length < 1) {
                                            job.data.listYearAutoImport.push(item.termSourcedIds);
                                        }
                                    })

                                    if (getListYear.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }
                                } else {
                                    job.data.stepIndex++;
                                } 
                                break
                            case TABLE_NAME_CLASSES:
                                if (!condCurrentStep) {
                                    job.data.stepIndex++;
                                } else {
                                    //insert to import class & courses
                                    const classAttr = [ 'sourcedId', 'status', 'dateLastModified', 'title', 'grades', 'courseSourcedId', 'classCode', 'classType', 'location', 'schoolSourcedId', 'termSourcedIds', 'subjects', 'subjectCodes', 'periods', 'municipalId' ];

                                    const coursesAttr = [ 'sourcedId', 'status', 'dateLastModified', 'schoolYearSourcedId', 'title', 'courseCode', 'grades', 'orgSourcedId', 'subjects', 'subjectCodes', 'municipalId','classesId' ];
                                    
                                    let getClassAutoImport = await db[job.data.municipalId].classes.findAll({
                                        attributes: classAttr,
                                        include: [
                                            {
                                                model: db[job.data.municipalId].courses,
                                                attributes: coursesAttr,
                                                include : [
                                                    {
                                                        model: db[job.data.municipalId].relCourses,
                                                        attributes: ['importSourcedId','importSchoolYearSourcedId'],
                                                    }
                                                ]
                                            },
                                            {
                                                model: db[job.data.municipalId].relClasses,
                                                attributes: ['importSourcedId','importSchoolSourcedId','importTermSourcedIds'],
                                            },
                                        ],
                                        where: {
                                            schoolSourcedId: { [Op.in]: job.data.listSchoolAutoImport },
                                            status: 'active',
                                            municipalId: job.data.municipalId 
                                        },
                                        offset: job.data.stepOffset,
                                        limit: config.IMPORT_CSV_CHUNK,
                                    })


                                    if (getClassAutoImport.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }

                                    const listClassAutoImport = [];
                                    const listCoursesAutoImport = [];
                                    getClassAutoImport.map((classes) => {
                                        const classInsert = {};
                                        classAttr.map((val) => {
                                            let itemVal = classes[val];
                                            if (val === "sourcedId") {
                                                itemVal = (classes.rel_class && classes.rel_class.importSourcedId) ? classes.rel_class.importSourcedId : itemVal;
                                            }
                                            if (val === "schoolSourcedId") {
                                                itemVal = (classes.rel_class && classes.rel_class.importSchoolSourcedId) ? classes.rel_class.importSchoolSourcedId : itemVal;
                                            }
                                            if (val === "termSourcedIds") {
                                                itemVal = (classes.rel_class && classes.rel_class.importTermSourcedIds) ? classes.rel_class.importTermSourcedIds : itemVal;
                                            }
                                            classInsert[val] = itemVal;
                                        });
                                        classInsert.option = 'add_csv_to_lgate';
                                        listClassAutoImport.push(classInsert);

                                        const coursesInsert = {};
                                        coursesAttr.map((val) => {
                                            let itemCrsVal = classes.course[val];
                                            if (val === "sourcedId") {
                                                itemCrsVal = (classes.course.rel_course && classes.course.rel_course.importSourcedId) ? classes.course.rel_course.importSourcedId : itemCrsVal;
                                            }
                                            if (val === "schoolYearSourcedId") {
                                                itemCrsVal = (classes.course.rel_course && classes.course.rel_course.importSchoolYearSourcedId) ? classes.course.rel_course.importSchoolYearSourcedId : itemCrsVal;
                                            }
                                            coursesInsert[val] = itemCrsVal;
                                        });
                                        coursesInsert.option = 'add_csv_to_lgate';
                                        listCoursesAutoImport.push(coursesInsert);
                                    });
                                    if (listClassAutoImport.length > 0) await db[job.data.municipalId].importClasses.bulkCreate( listClassAutoImport, { updateOnDuplicate: classAttr } );
                                    if (listCoursesAutoImport.length > 0) await db[job.data.municipalId].importCourses.bulkCreate( listCoursesAutoImport, { updateOnDuplicate: coursesAttr } );
                                    
                                }
                                break;
                            case TABLE_NAME_ORGS:
                                if (!condCurrentStep) {
                                    job.data.stepIndex++;
                                } else {
                                    //insert to import org
                                    const orgsAttr = [ 'sourcedId', 'status', 'dateLastModified', 'name', 'type', 'identifier', 'parentSourcedId', 'municipalId' ];
                                    let getOrgsAutoImport = await db[job.data.municipalId].orgs.findAll({
                                        attributes: orgsAttr,
                                        include: [
                                            {
                                                model: db[job.data.municipalId].relOrgs,
                                                attributes: ['importSourcedId'],
                                            },
                                        ],
                                        where: {
                                            sourcedId: { [Op.in]: job.data.listSchoolAutoImport },
                                            status: 'active',
                                            municipalId: job.data.municipalId 
                                        },
                                        offset: job.data.stepOffset,
                                        limit: config.IMPORT_CSV_CHUNK,
                                    })

                                    if (getOrgsAutoImport.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }

                                    const listOrgsAutoImport = [];
                                    getOrgsAutoImport.map((orgsItem) => {
                                        const orgsInsert = {};
                                        orgsAttr.map((val) => {
                                            let itemVal = orgsItem[val];
                                            if (val === "sourcedId") {
                                                itemVal = (orgsItem.rel_org && orgsItem.rel_org.importSourcedId) ? orgsItem.rel_org.importSourcedId : itemVal;
                                            }
                                            orgsInsert[val] = itemVal;
                                        });
                                        orgsInsert.option = 'add_csv_to_lgate';
                                        listOrgsAutoImport.push(orgsInsert);
                                    });
                                    await db[job.data.municipalId].importOrgs.bulkCreate( listOrgsAutoImport, { updateOnDuplicate: orgsAttr } );
                                }
                                break;
                            case TABLE_NAME_ACADEMIC_SESSIONS:
                                if (!condCurrentStep) {
                                    job.data.stepIndex++;
                                } else {
                                    //insert to import year
                                    const yearAttr = [ 'sourcedId', 'status', 'dateLastModified', 'title', 'type', 'startDate', 'endDate', 'parentSourcedId', 'schoolYear', 'municipalId' ];
                                    let getYearAutoImport = await db[job.data.municipalId].academicSessions.findAll({
                                        attributes: yearAttr,
                                        include: [
                                            {
                                                model: db[job.data.municipalId].relAcademicSessions,
                                                attributes: ['importSourcedId'],
                                            },
                                        ],
                                        where: {
                                            sourcedId: { [Op.in]: job.data.listYearAutoImport },
                                            status: 'active',
                                            municipalId: job.data.municipalId 
                                        },
                                        offset: job.data.stepOffset,
                                        limit: config.IMPORT_CSV_CHUNK,
                                    })

                                    if (getYearAutoImport.length < config.IMPORT_CSV_CHUNK) {
                                        job.data.stepOffset = 0;
                                        job.data.stepIndex++;

                                        await db[job.data.municipalId].importTaskProgress.upsert({
                                            id: `${job.data.municipalId}_${YEAR_COLLATION}`,
                                            municipalId: job.data.municipalId,
                                            type: YEAR_COLLATION,
                                            userId: "-",
                                            status: STATUS_COMPLETED,
                                            progress: 100,
                                            importStatus: 0,
                                            lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                        })
                                    } else {
                                        job.data.stepOffset = job.data.stepOffset + config.IMPORT_CSV_CHUNK;
                                    }

                                    const listYearAutoImport = [];
                                    // console.log(getYearAutoImport)
                                    getYearAutoImport.map((yearItem) => {
                                        const yearInsert = {};
                                        yearAttr.map((val) => {
                                            let itemVal = yearItem[val];
                                            if (val === "sourcedId") {
                                                itemVal = (yearItem.rel_academic_session && yearItem.rel_academic_session.importSourcedId) ? yearItem.rel_academic_session.importSourcedId : itemVal;
                                            }
                                            yearInsert[val] = itemVal;
                                        });
                                        yearInsert.option = 'add_csv_to_lgate';
                                        listYearAutoImport.push(yearInsert);
                                    });
                                    await db[job.data.municipalId].importAcademicSessions.bulkCreate( listYearAutoImport, { updateOnDuplicate: yearAttr } );
                                    await db[job.data.municipalId].academicSessions.update({ isToBeDeleted: 1 }, { where: { sourcedId: { [Op.notIn]: job.data.listYearAutoImport } } })
                                }
                                break;
                        }
                        
                        if (job.data.stepIndex < stepDeltaImported.length) {
                            let percent = ((job.data.stepIndex + 1)/stepDeltaImported.length) * 100;
                            await job.progress(percent);
                            this.onProcess(job,done,csvMerged,index,0)
                        } else {
                            await job.progress(100);
                            status = STATUS_COMPLETED
                        }
                    break;
                }
                break;

            case YEAR_COLLATION:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:   
                        let insert;
                    
                        if(!csvMerged){
                            let queryMerged = await mergedAcademicSessions(job.data.municipalId)
                            csvMerged = {}
                            csvMerged.csv = JSON.parse(JSON.stringify(queryMerged))
                            if(!csvMerged?.csvChunk){
                                csvMerged.csvChunk = arrayChunk(csvMerged.csv,config.IMPORT_CSV_CHUNK)
                            }
                        }
                        
                        if(csvMerged?.csvChunk){
                            if(csvMerged.csvChunk[index]?.length > 0){
                                let dataInsert = csvMerged.csvChunk[index]
                                let diff = config.IMPORT_CSV_CHUNK - dataInsert.length
                                let dataProgress = (config.IMPORT_CSV_CHUNK * (index+1)) - diff
                                insert = await executeQuery(TABLE_NAME_ACADEMIC_SESSIONS,dataInsert,job.data.municipalId)
                                if(insert?.status){
                                    let percent = (dataProgress/csvMerged.csv.length) * 100;
                                    await job.progress(percent)
                                }
                                this.onProcess(job,done,csvMerged,++index,0)
                            } else {
                                await job.progress(100)
                                status = STATUS_COMPLETED
                            }
                        }
                        break;
                }
                break;
        
            case SCHOOL_COLLATION:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:   
                        let insert;
                    
                        if(!csvMerged){
                            let queryMerged = await mergedSchool(job.data.municipalId)
                            csvMerged = {}
                            csvMerged.csv = JSON.parse(JSON.stringify(queryMerged))
                            if(!csvMerged?.csvChunk){
                                csvMerged.csvChunk = arrayChunk(csvMerged.csv,config.IMPORT_CSV_CHUNK)
                            }
                        }
                        
                        if(csvMerged?.csvChunk){
                            if(csvMerged.csvChunk[index]?.length > 0){
                                let dataInsert = csvMerged.csvChunk[index]
                                let diff = config.IMPORT_CSV_CHUNK - dataInsert.length
                                let dataProgress = (config.IMPORT_CSV_CHUNK * (index+1)) - diff

                                insert = await executeQuery(TABLE_NAME_ORGS,dataInsert,job.data.municipalId)
                                if(insert?.status){
                                    let percent = (dataProgress/csvMerged.csv.length) * 100;
                                    await job.progress(percent)
                                }
                                this.onProcess(job,done,csvMerged,++index,0)
                            } else {
                                await job.progress(100)
                                status = STATUS_COMPLETED
                            }
                        }
                        break;
                }
                break;
            case IMPORT_DELTA_MERGE:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:   
                        if (!job.data.stepProgress) job.data.stepProgress = 0;
                        const stepMerged = [TABLE_NAME_ORGS,TABLE_NAME_CLASSES,TABLE_NAME_GROUPS];
                        switch (stepMerged[job.data.stepProgress]) {
                            case TABLE_NAME_ORGS:
                                if (job.data.autoImportTable[TABLE_NAME_ORGS]) {
                                    if (!job.data.orgMergedStatus) {
                                        job.data.orgMergedStatus = 1;
                                        const orgMerged = await mergedClassImport(job.data.municipalId);
                                        if (orgMerged) {
                                            job.data.orgMergedStatus = 2;
                                        }
                                    } else if (job.data.orgMergedStatus == 2) {
                                        job.data.stepProgress++;
                                        await db[job.data.municipalId].importTaskProgress.upsert({
                                            id: `${job.data.municipalId}_${SCHOOL_COLLATION}`,
                                            municipalId: job.data.municipalId,
                                            type: SCHOOL_COLLATION,
                                            userId: "-",
                                            status: STATUS_COMPLETED,
                                            progress: 100,
                                            importStatus: 0,
                                            lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                        })
                                    }
                                } else {
                                    job.data.stepProgress++;
                                }
                                break;
                            case TABLE_NAME_CLASSES:
                                if (job.data.autoImportTable[TABLE_NAME_CLASSES]) {
                                    if (!job.data.classMergedStatus) {
                                        job.data.classMergedStatus = 1;
                                        const classMerged = await mergedUsersImport(job.data.municipalId,["teacher", "student","administrator"],"homeroom");
                                        if (classMerged) {
                                            job.data.classMergedStatus = 2;
                                        }
                                    } else if (job.data.classMergedStatus == 2) {
                                        job.data.stepProgress++;
                                        await db[job.data.municipalId].importTaskProgress.upsert({
                                            id: `${job.data.municipalId}_${CLASS_COLLATION}`,
                                            municipalId: job.data.municipalId,
                                            type: CLASS_COLLATION,
                                            userId: "-",
                                            status: STATUS_COMPLETED,
                                            progress: 100,
                                            importStatus: 0,
                                            lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                        }); 
                                    }
                                } else {
                                    job.data.stepProgress++;
                                }
                                break;
                            case TABLE_NAME_GROUPS:
                                if (job.data.autoImportTable[TABLE_NAME_CLASSES]) {
                                    if (!job.data.groupMergedStatus) {
                                        job.data.groupMergedStatus = 1;
                                        const groupMerged = await mergedUsersGroup(job.data.municipalId,["teacher", "student","administrator"],"scheduled");
                                        if (groupMerged) {
                                            job.data.groupMergedStatus = 2;
                                        }
                                    } else if (job.data.groupMergedStatus == 2) {
                                        job.data.stepProgress++;
                                        await db[job.data.municipalId].importTaskProgress.upsert({
                                            id: `${job.data.municipalId}_${OTHER_CLASS_COLLATION}`,
                                            municipalId: job.data.municipalId,
                                            type: OTHER_CLASS_COLLATION,
                                            userId: "-",
                                            status: STATUS_COMPLETED,
                                            progress: 100,
                                            importStatus: 0,
                                            lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                        }); 
                                    }
                                } else {
                                    job.data.stepProgress++;
                                }
                                break;
                        }
                        if (job.data.stepProgress < stepMerged.length) {
                            let percent = ((job.data.stepProgress + 1)/stepMerged.length) * 100;
                            await job.progress(percent);
                            this.onProcess(job,done,csvMerged,index,0)
                        } else {
                            // insert progress auto import
                            if (!job.data.importedTable[TABLE_NAME_USERS] && !job.data.createProgressTask) {
                                job.data.createProgressTask = 1;
                                const createBulkProgress = [];
                                const defaultAttrPrgs = {
                                    municipalId: job.data.municipalId,
                                    userId: "-",
                                    status: STATUS_COMPLETED,
                                    progress: 100,
                                    importStatus: 0,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                };
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${ADMIN_TEACHER_COLLATION}`,
                                    type: ADMIN_TEACHER_COLLATION,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${STUDENT_COLLATION}`,
                                    type: STUDENT_COLLATION,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${CLASS_ATENDANCE_COLLATION}`,
                                    type: CLASS_ATENDANCE_COLLATION,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${OTHER_ATENDANCE_COLLATION}`,
                                    type: OTHER_ATENDANCE_COLLATION,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${USER_ASSIGNMENT_SCREEN}`,
                                    type: USER_ASSIGNMENT_SCREEN,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${ADMINISTRATOR_COLLATION}`,
                                    type: ADMINISTRATOR_COLLATION,
                                });
                                createBulkProgress.push({
                                    ...defaultAttrPrgs,
                                    id: `${job.data.municipalId}_${USER_CONFIRMATION_SCREEN}`,
                                    type: USER_CONFIRMATION_SCREEN,
                                });
                                await db[job.data.municipalId].importTaskProgress.bulkCreate(createBulkProgress);
                            }
                            await job.progress(100);
                            status = STATUS_COMPLETED
                        }
                        break;
                }
                break;

            case FILL_USER_PRIMARY_ORGS:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:
                        const query = `
                            UPDATE import_users iuser
                            INNER JOIN import_roles irole ON iuser.sourcedId = irole.userSourcedId
                            SET iuser.orgSourcedIds = irole.orgSourcedId
                            WHERE isNull(iuser.orgSourcedIds) AND irole.roleType = 'primary'
                        `;
                        await db[job.data.municipalId].query(query);
                        await job.progress(100);
                        status = STATUS_COMPLETED
                    break; 
                } 
                break;
            
            case CHECK_SOURCED_ID:
                switch(lockJobMunicipal) {
                    case 0:
                        status = STATUS_FAILED
                        break;
                    case 1:
                        if(timeout >= 300000){
                            status = STATUS_FAILED
                        }
                        await sleep(job.opts.delay);
                        timeout += job.opts.delay
                        this.onProcess(job,done,csvMerged,index,timeout);
                        break;
                    default:  
                        if (processStatus) {
                            //check courseSourcedId, schoolSourcedId, subjectCodes on classes.csv
                            const queryClassCheck = `
                            SELECT 
                                SUM(if(import_classes.courseSourcedId IS NOT NULL AND ISNULL(import_courses.sourcedId), 1, 0)) as invalidDataCourses, 
                                SUM(if(import_classes.subjectCodes IS NOT NULL AND (ISNULL(import_courses.subjectCodes) OR import_classes.subjectCodes!=import_courses.subjectCodes), 1, 0)) as invalidDataSubjectCodes, 
                                SUM(if(import_classes.schoolSourcedId IS NOT NULL AND ISNULL(import_orgs.sourcedId), 1, 0)) as invalidDataSchool, 
                                SUM(if(import_classes.schoolSourcedId IS NOT NULL AND import_orgs.sourcedId IS NOT NULL AND import_orgs.type = 'district', 1, 0)) as invalidTypeSchool, SUM(if(import_classes.termSourcedIds IS NOT NULL AND ISNULL(import_academic_sessions.sourcedId), 1, 0)) as invalidDataTerm 
                            FROM import_classes 
                                LEFT JOIN import_courses ON import_classes.courseSourcedId = import_courses.sourcedId
                                LEFT JOIN import_orgs ON import_classes.schoolSourcedId = import_orgs.sourcedId
                                LEFT JOIN import_academic_sessions ON import_classes.termSourcedIds = import_academic_sessions.sourcedId`;
                            
                            const [checkClasses] = await db[job.data.municipalId].query(queryClassCheck);

                            //check orgSourcedId, schoolYearSourcedId, subjectCodes on courses.csv
                            const queryCourseCheck = `SELECT SUM(if(import_courses.orgSourcedId IS NOT NULL AND ISNULL(import_orgs.sourcedId), 1, 0)) as invalidDataOrgs, SUM(if(import_courses.schoolYearSourcedId IS NOT NULL AND ISNULL(import_academic_sessions.sourcedId), 1, 0)) as invalidDataYear, SUM(if(import_courses.subjectCodes IS NOT NULL AND (ISNULL(import_classes.subjectCodes) OR import_classes.subjectCodes!=import_courses.subjectCodes), 1, 0)) as invalidDataSubjectCodes FROM import_courses LEFT JOIN import_academic_sessions ON import_courses.schoolYearSourcedId = import_academic_sessions.sourcedId LEFT JOIN import_orgs ON import_courses.orgSourcedId = import_orgs.sourcedId LEFT JOIN import_classes ON import_courses.sourcedId = import_classes.courseSourcedId`;
                            
                            const [checkCourses] = await db[job.data.municipalId].query(queryCourseCheck);

                            //check multiple school, invalid class on enrollments.csv
                            const queryMultipleSchoolEnr = `
                            SELECT 
                                import_enrollments.userSourcedId, 
                                COUNT(DISTINCT(import_enrollments.schoolSourcedId)) as total_school, 
                                SUM(if(import_enrollments.schoolSourcedId IS NOT NULL AND ISNULL(import_orgs.sourcedId), 1, 0)) as invalidSchool, 
                                SUM(if(import_enrollments.schoolSourcedId IS NOT NULL AND import_orgs.sourcedId IS NOT NULL AND import_orgs.type = 'district', 1, 0)) as invalidTypeSchool, 
                                SUM(if(import_enrollments.classSourcedId IS NOT NULL AND ISNULL(import_classes.sourcedId), 1, 0)) as invalidClass, 
                                SUM(if(import_enrollments.userSourcedId IS NOT NULL AND ISNULL(import_users.sourcedId), 1, 0)) as invalidUser 
                            FROM import_enrollments 
                                LEFT JOIN import_orgs ON import_enrollments.schoolSourcedId = import_orgs.sourcedId 
                                LEFT JOIN import_classes ON import_enrollments.classSourcedId = import_classes.sourcedId 
                                LEFT JOIN import_users ON import_enrollments.userSourcedId = import_users.sourcedId 
                            GROUP BY userSourcedId HAVING total_school > 1 or invalidSchool > 0 or invalidTypeSchool > 0 or invalidClass > 0 or invalidUser > 0`;
                            const [checkMultipleSchoolEnr] = await db[job.data.municipalId].query(queryMultipleSchoolEnr);

                            //check invalidUser, multiple school and multiple role on role.csv
                            const queryMultipleSchoolRole = `
                            SELECT 
                                SUM(if(impRoles.school_user > 1, 1, 0)) as invalidDataSchool, 
                                SUM(if(impRoles.role_user > 1, 1, 0)) as invalidDataRole, 
                                SUM(if(impRoles.invalidUser > 0, 1, 0)) as invalidDataUser, 
                                SUM(if(impRoles.invalidOrgs > 0, 1, 0)) as invalidDataOrgs, 
                                SUM(if(impRoles.primary_user < 1, 1, 0)) as invalidDataRoleType 
                            FROM 
                                (SELECT import_roles.userSourcedId, COUNT(DISTINCT(import_roles.orgSourcedId)) as school_user, COUNT(DISTINCT(import_roles.role)) as role_user, SUM(IF(import_roles.roleType = 'primary', 1, 0)) as primary_user, SUM(if(import_roles.userSourcedId IS NOT NULL AND ISNULL(import_users.sourcedId), 1, 0)) as invalidUser, SUM(if(import_roles.orgSourcedId IS NOT NULL AND ISNULL(import_orgs.sourcedId), 1, 0)) as invalidOrgs FROM import_roles LEFT JOIN import_users ON import_roles.userSourcedId = import_users.sourcedId LEFT JOIN import_orgs ON import_roles.orgSourcedId = import_orgs.sourcedId GROUP BY userSourcedId HAVING school_user > 1 OR role_user > 1 OR invalidUser > 0 or invalidOrgs > 0 or primary_user < 1) as impRoles`;
                            const [checkMultipleSchoolRole] = await db[job.data.municipalId].query(queryMultipleSchoolRole);

                            //check valid metadataJpHomeClass on users.csv
                            const queryValidHomeClassUser = `SELECT SUM(if(import_users.metadataJpHomeClass IS NOT NULL AND ISNULL(import_enrollments.sourcedId), 1, 0)) as invalidEnrollment, SUM(if(import_users.orgSourcedIds IS NOT NULL AND ISNULL(import_orgs.sourcedId), 1, 0)) as invalidOrgs FROM import_users LEFT JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId AND import_enrollments.classSourcedId = import_users.metadataJpHomeClass LEFT JOIN import_orgs ON import_users.orgSourcedIds = import_orgs.sourcedId HAVING invalidEnrollment > 0 or invalidOrgs > 0`;
                            const [checkValidHomeClassUser] = await db[job.data.municipalId].query(queryValidHomeClassUser);

                            if (
                                (checkClasses && checkClasses.length && (
                                    parseInt(checkClasses[0]['invalidDataCourses']) > 0 ||
                                    parseInt(checkClasses[0]['invalidDataSubjectCodes']) > 0 ||
                                    parseInt(checkClasses[0]['invalidDataSchool']) > 0 ||
                                    parseInt(checkClasses[0]['invalidTypeSchool']) > 0 ||
                                    parseInt(checkClasses[0]['invalidDataTerm']) > 0
                                )) ||
                                (checkCourses && checkCourses.length && (
                                    parseInt(checkCourses[0]['invalidDataSubjectCodes']) > 0 || 
                                    parseInt(checkCourses[0]['invalidDataOrgs']) > 0 || 
                                    parseInt(checkCourses[0]['invalidDataYear']) > 0
                                )) ||
                                (checkMultipleSchoolRole && checkMultipleSchoolRole.length && (
                                    parseInt(checkMultipleSchoolRole[0]['invalidDataSchool']) > 0 || 
                                    parseInt(checkMultipleSchoolRole[0]['invalidDataUser']) > 0 || 
                                    parseInt(checkMultipleSchoolRole[0]['invalidDataOrgs']) > 0 ||
                                    parseInt(checkMultipleSchoolRole[0]['invalidDataRoleType']) > 0
                                    // parseInt(checkMultipleSchoolRole[0]['invalidDataRole']) > 0
                                )) ||
                                (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && (
                                    parseInt(checkMultipleSchoolEnr[0]['total_school']) > 1 || 
                                    parseInt(checkMultipleSchoolEnr[0]['invalidSchool']) > 0 || 
                                    parseInt(checkMultipleSchoolEnr[0]['invalidClass']) > 0 || 
                                    parseInt(checkMultipleSchoolEnr[0]['invalidUser']) > 0 || 
                                    parseInt(checkMultipleSchoolEnr[0]['invalidTypeSchool']) > 0
                                )) ||
                                (checkValidHomeClassUser && checkValidHomeClassUser.length > 0 && (
                                    parseInt(checkValidHomeClassUser[0]['invalidEnrollment']) > 0 || 
                                    parseInt(checkValidHomeClassUser[0]['invalidOrgs']) > 0
                                ))
                            ) {
                                const invalidmessage = [];
                                if (checkClasses && checkClasses.length && parseInt(checkClasses[0]['invalidDataCourses']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_course_classes'))
                                }
                                if (checkClasses && checkClasses.length && parseInt(checkClasses[0]['invalidDataSubjectCodes']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_subjectCodes_classes'))
                                }
                                if (checkClasses && checkClasses.length && parseInt(checkClasses[0]['invalidDataSchool']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_school_classes'))
                                }
                                if (checkClasses && checkClasses.length && parseInt(checkClasses[0]['invalidTypeSchool']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_school_type_classes'))
                                }
                                if (checkClasses && checkClasses.length && parseInt(checkClasses[0]['invalidDataTerm']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_year_classes'))
                                }
                                if (checkCourses && checkCourses.length && parseInt(checkCourses[0]['invalidDataSubjectCodes']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_subjectCodes_courses'))
                                }
                                if (checkCourses && checkCourses.length && parseInt(checkCourses[0]['invalidDataOrgs']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_orgs_courses'))
                                }
                                if (checkCourses && checkCourses.length && parseInt(checkCourses[0]['invalidDataYear']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_year_courses'))
                                }
                                if (checkMultipleSchoolRole && checkMultipleSchoolRole.length && parseInt(checkMultipleSchoolRole[0]['invalidDataSchool']) > 0) {
                                    invalidmessage.push(lang.t('import.message.multiple_school_roles'))
                                }
                                if (checkMultipleSchoolRole && checkMultipleSchoolRole.length && parseInt(checkMultipleSchoolRole[0]['invalidDataRoleType']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_roleType_roles'))
                                }
                                // if (checkMultipleSchoolRole && checkMultipleSchoolRole.length && parseInt(checkMultipleSchoolRole[0]['invalidDataRole']) > 0) {
                                //     invalidmessage.push(lang.t('import.message.multiple_role_roles'))
                                // }
                                if (checkMultipleSchoolRole && checkMultipleSchoolRole.length && parseInt(checkMultipleSchoolRole[0]['invalidDataUser']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_user_roles'))
                                }
                                if (checkMultipleSchoolRole && checkMultipleSchoolRole.length && parseInt(checkMultipleSchoolRole[0]['invalidDataOrgs']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_orgs_roles'))
                                }
                                if (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && parseInt(checkMultipleSchoolEnr[0]['total_school']) > 1) {
                                    invalidmessage.push(lang.t('import.message.multiple_school_enrollments'))
                                }
                                if (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && parseInt(checkMultipleSchoolEnr[0]['invalidSchool']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_school_enrollments'))
                                }
                                if (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && parseInt(checkMultipleSchoolEnr[0]['invalidTypeSchool']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_school_type_enrollments'))
                                }
                                if (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && parseInt(checkMultipleSchoolEnr[0]['invalidClass']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_class_enrollments'))
                                }
                                if (checkMultipleSchoolEnr && checkMultipleSchoolEnr.length > 0 && parseInt(checkMultipleSchoolEnr[0]['invalidUser']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_user_enrollments'))
                                }
                                if (checkValidHomeClassUser && checkValidHomeClassUser.length > 0 && parseInt(checkValidHomeClassUser[0]['invalidEnrollment']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_homeclass_users'))
                                }
                                if (checkValidHomeClassUser && checkValidHomeClassUser.length > 0 && parseInt(checkValidHomeClassUser[0]['invalidOrgs']) > 0) {
                                    invalidmessage.push(lang.t('import.message.invalid_orgs_users'))
                                }
                                errmessage = lang.t('import.message.invalid_sourced_id') + invalidmessage.join(", ")
                                await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
                                status = STATUS_FAILED
                                await processDiscardImport(job.data.municipalId);
                            } else {
                                status = STATUS_COMPLETED
                            }
                        } else {
                            errmessage = lang.t('import.message.invalid_sourced_id') + processMsg.join(", ")
                            await redisClient.del(`LOCK_IMPORT_${job.data.municipalId}`);
                            status = STATUS_FAILED
                            await processDiscardImport(job.data.municipalId);
                        }
                }       
                break; 
        }

        switch(status) {
            case STATUS_COMPLETED:
                done(null,{message:STATUS_COMPLETED})
                break;
            
            case STATUS_FAILED:
                done({message:errmessage})
                break;
        }
    }

    onActive = async (job, jobPromise) => {
        const param = job.data

        await db[param.municipalId].lgateOrganization.destroy({
            where : {
                municipalId : param.municipalId
            }
        })
        await db[param.municipalId].lgateClasses.destroy({
            where : {
                municipalId : param.municipalId
            }
        })
        await db[param.municipalId].lgateUsers.destroy({
            where : {
                municipalId : param.municipalId
            }
        })
        await db[param.municipalId].lgateEnrollments.destroy({
            where : {
                municipalId : param.municipalId
            }
        })
        await db[param.municipalId].lgateRole.destroy({
            where : {
                municipalId : param.municipalId
            }
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
        await redisClient.set(`LOCK_IMPORT_${job.data.municipalId}`, 1);
        console.log('completed',job.id,result)
        
    }

    onFailed = async (job, err) => {
        console.log('failed',job.id)
        
    }
    
}

/**
 * Create export variable to running function ImportProcess
 * @constructor
 */
const ImportQueueProcess = new ImportProcess()

export default ImportQueueProcess