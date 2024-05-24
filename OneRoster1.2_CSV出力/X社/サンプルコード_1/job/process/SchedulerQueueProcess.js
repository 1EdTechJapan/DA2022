
import moment from 'moment';
import { v4 as uuidv4 } from "uuid";
import {db} from "../../models/index.js";
import lang from '../../i18n.js';
import config from '../../config/config.js';
import {existsSync,readdirSync,unlinkSync} from 'fs';
import writecsv from '../../helpers/wtirecsv.js';
import zipper from '../../helpers/zipper.js';
import redisClient from "../../redisClient.js";
import {ContainerClient} from '@azure/storage-blob';
import LogHelper from "../../helpers/log.js";
import AzureLogHelper from "../../helpers/azureLog.js";
import { 
    TABLE_NAME_ACADEMIC_SESSIONS,
    TABLE_NAME_ORGS,
    TABLE_NAME_COURSES,
    TABLE_NAME_CLASSES,
    TABLE_NAME_USERS,
    TABLE_NAME_ENROLLMENTS,
    TABLE_NAME_ROLES,
    TABLE_NAME_IMPORT_USERS,
    CSV_ZIP_TO_BLOB,
    OUTPUT_TARGET_ALL,
    OUTPUT_TARGET_STUDENT,
    OUTPUT_TARGET_TEACHER,
    OUTPUT_RANGE_BULK,
    OUTPUT_RANGE_DELTA,

    SINGLE_EXPORT,

    STATUS_COMPLETED,
    STATUS_PROCESSING,
    STATUS_FAILED,
    OUTPUT_OPERATION_SCHEDULE_TO_BLOB,
    OUTPUT_OPERATION_TO_BLOB_ONCE,
    LOG_TYPE_INFO,
    LOG_TYPE_ERROR,
    LOG_TYPE_SUCCESS,
    CSV_FILENAME_ACADEMIC_SESSIONS,
    CSV_FILENAME_ORGS,
    CSV_FILENAME_COURSES,
    CSV_FILENAME_CLASSES,
    CSV_FILENAME_USERS,
    CSV_FILENAME_ENROLLMENTS,
    CSV_FILENAME_ROLES,
    CSV_FILENAME_MANIFEST,
    MANIFEST_PROPERTY_NAME_LABEL,
    MANIFEST_VALUE_LABEL,
    MANIFEST_VERSION,
    MANIFEST_ONEROSTER_VERSION,
    MANIFEST_FILE_VALUE_ABSENT,
    MANIFEST_FILE_VALUE_BULK,
    MANIFEST_FILE_VALUE_DELTA,
    MANIFEST_SYSTEM_NAME,
    MANIFEST_SYSTEM_CODE,
    OUTPUT_TARGET_ACADEMIC_SESSION_PAST,
    OUTPUT_TARGET_ACADEMIC_SESSION_LAST,
    OUTPUT_TARGET_ACADEMIC_SESSION_CURRENT,
    OUTPUT_TARGET_ACADEMIC_SESSION_NEXT,
    OUTPUT_TARGET_ACADEMIC_SESSION_FUTURE,
    OUTPUT_TARGET_ACADEMIC_SESSION_INFINITY
} from "../../constants/constans.js";

const LOG = new LogHelper("SCHEDULER");
const AZURELOG = new AzureLogHelper();

const tables = [TABLE_NAME_ACADEMIC_SESSIONS,TABLE_NAME_ORGS,TABLE_NAME_COURSES,TABLE_NAME_CLASSES,TABLE_NAME_USERS,TABLE_NAME_ENROLLMENTS,TABLE_NAME_ROLES,TABLE_NAME_IMPORT_USERS];
// let tables = [TABLE_NAME_ORGS,TABLE_NAME_COURSES,TABLE_NAME_CLASSES]; 

/**
 * Processing bull job for scheduler action
 * @constructor
 */
class SchedulerProcess {
    onProcess = async (job, done, limit = 100, offset = 0, progressPercent=0, yearId = true, initData = null) => {

            if(!initData){             
                initData = {
                    executionTime : null,
                    currentDate : null,
                    currentDateFormat : null,
                    procedDate : null,
                    folderName : null
                }
            }

            let lockJobMunicipal = await redisClient.get(`LOCK_SYNC_${job.data.municipalId}`);
            if(lockJobMunicipal){
                return done({code:`SCD0011`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0011')}`,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }
            
            initData.procedDate = moment(job.opts.timestamp).add(job.opts.delay,'ms')
            initData.currentDate = `${initData.procedDate.format('YYYYMMDDHHmm')}00`
            initData.currentDateFormat = `${initData.procedDate.format('YYYY-MM-DD HH:mm:')}00`
            initData.executionTime = moment(job.processedOn)
            initData.folderName = `${job.data.outputRange}-${initData.currentDate}`.toLowerCase()

            if(config.SCHEDULER_TIMEOUT_PROCESSED_TIME < initData.executionTime.diff(initData.procedDate,"minutes",true)){
                return done({code:`SCD0012`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0012')}`, procedDate: initData.procedDate, folderName:initData.folderName})
            }
          
            await redisClient.set(`${job.data.uniqueIdJob}_${CSV_ZIP_TO_BLOB}`, '')
            await redisClient.set(`${job.data.uniqueIdJob}_${tables[job.data.tableIndex]}`, 0);
            await redisClient.set(`${job.data.uniqueIdJob}_${tables[job.data.tableIndex]}_processedOn`, job.processedOn);
            await redisClient.set(`LOCK_EXPORT_${job.data.municipalId}`, 1);

            await db[job.data.municipalId].scheduler.update({
                statusJob : 1
            },{
                where : { uniqueIdJob : job.data.uniqueIdJob}
            })

            let data = job.data
            let tableIndex = data.tableIndex
            
            let currentTableName =''
            let currentFileName =''
            let currentTableData = []
            let currentTableHeader = []
            let currentTableStatus = STATUS_PROCESSING
            
            let academic_sessions = {
                header: [
                    'sourcedId',
                    'status',
                    'dateLastModified',
                    'title',
                    'type',
                    'startDate',
                    'endDate',
                    'parentSourcedId',
                    'schoolYear'
                ],
                query : {
                    attributes: [
                        'sourcedId',
                        'status',
                        'dateLastModified',
                        'title',
                        'type',
                        'startDate',
                        'endDate',
                        'parentSourcedId',
                        'schoolYear'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` }
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let orgs = {
                header: [
                    'sourcedId',
                    'status',
                    'dateLastModified',
                    'name',
                    'type',
                    'identifier',
                    'parentSourcedId'
                ],
                query : {
                    attributes: [
                        'sourcedId',
                        'status',
                        'dateLastModified',
                        'name',
                        'type',
                        'identifier',
                        'parentSourcedId'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let courses = {
                header: [
                    'sourcedId',
                    'status',
                    'dateLastModified',
                    'schoolYearSourcedId',
                    'title',
                    'courseCode',
                    'grades',
                    'orgSourcedId',
                    'subjects',
                    'subjectCodes'
                ],
                query : {
                    attributes: [
                        'sourcedId',
                        'status',
                        'dateLastModified',
                        'schoolYearSourcedId',
                        'title',
                        'courseCode',
                        'grades',
                        'orgSourcedId',
                        'subjects',
                        'subjectCodes'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }
            
            let classes = {
                header: [
                    'sourcedId',
                    'status',
                    'dateLastModified',
                    'title',
                    'grades',
                    'courseSourcedId',
                    'classCode',
                    'classType',
                    'location',
                    'schoolSourcedId',
                    'termSourcedIds',
                    'subjects',
                    'subjectCodes',
                    'periods'
                ],
                query : {
                    attributes: [
                        'sourcedId',
                        'status',
                        'dateLastModified',
                        'title',
                        'grades',
                        'courseSourcedId',
                        'classCode',
                        'classType',
                        'location',
                        'schoolSourcedId',
                        'termSourcedIds',
                        'subjects',
                        'subjectCodes',
                        'periods'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let users = {
                header: [
                    'sourcedId', 
                    'status', 
                    'dateLastModified', 
                    'enabledUser', 
                    'orgSourcedIds', 
                    'role', 
                    'username', 
                    'userIds', 
                    'givenName', 
                    'familyName', 
                    'middleName', 
                    'identifier', 
                    'email', 
                    'sms', 
                    'phone', 
                    'agentSourcedIds', 
                    'grades', 
                    'password'
                ],
                query : {
                    attributes: [
                        'sourcedId', 
                        'status', 
                        'dateLastModified', 
                        'enabledUser', 
                        'orgSourcedIds', 
                        'role', 
                        'username', 
                        'userIds', 
                        'givenName', 
                        'familyName', 
                        'middleName', 
                        'identifier', 
                        'email', 
                        'sms', 
                        'phone', 
                        'agentSourcedIds', 
                        'grades', 
                        'password'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let enrollments = {
                header: [
                    'sourcedId', 
                    'status', 
                    'dateLastModified', 
                    'classSourcedId', 
                    'schoolSourcedId', 
                    'userSourcedId', 
                    'role', 
                    'primary', 
                    'beginDate', 
                    'endDate'
                ],
                query : {
                    attributes: [
                        'sourcedId', 
                        'status', 
                        'dateLastModified', 
                        'classSourcedId', 
                        'schoolSourcedId', 
                        'userSourcedId', 
                        'role', 
                        'primary', 
                        'beginDate', 
                        'endDate'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let roles = {
                header: [
                    'sourcedId', 
                    'status', 
                    'dateLastModified', 
                    'userSourcedId', 
                    'roleType',
                    'role', 
                    'beginDate', 
                    'endDate',
                    'orgSourcedId',
                    'userProfileSourcedId'
                ],
                query : {
                    attributes: [
                        'sourcedId', 
                        'status', 
                        'dateLastModified', 
                        'userSourcedId', 
                        'roleType',
                        'role', 
                        'nullValue', 
                        'nullValue',
                        'orgSourcedId',
                        'nullValue'
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            let import_users = {
                header: [
                    `sourcedId`,
                    `status`,
                    `dateLastModified`,
                    `enabledUser`,
                    `orgSourcedIds`,
                    `role`, `username`,
                    `userIds`,
                    `givenName`,
                    `familyName`,
                    `middleName`, 
                    `identifier`,
                    `email`,
                    `sms`,
                    `phone`,
                    `agentSourcedIds`,
                    `grades`,
                    `password`,
                    `municipalId`,
                    `userIdLgate`,
                    `userLgateName`,
                    `userLgatePassword`,
                    `option`,
                    `submited`,
                    `isParentSkiped`,
                    `isDelta`
                ],
                query : {
                    attributes: [
                        `sourcedId`,
                        `status`,
                        `dateLastModified`,
                        `enabledUser`,
                        `orgSourcedIds`,
                        `role`, `username`,
                        `userIds`,
                        `givenName`,
                        `familyName`,
                        `middleName`, 
                        `identifier`,
                        `email`,
                        `sms`,
                        `phone`,
                        `agentSourcedIds`,
                        `grades`,
                        `password`,
                        `municipalId`,
                        `userIdLgate`,
                        `userLgateName`,
                        `userLgatePassword`,
                        `option`,
                        `submited`,
                        `isParentSkiped`,
                        `isDelta`
                    ],
                    where: {
                        municipalId: { [db[job.data.municipalId].Sequelize.Op.eq]: `${data.municipalId}` },
                    },
                    offset: offset,
                    limit: limit
                },
                exported:0,
                status :STATUS_PROCESSING
            }

            if(data?.schoolSelected.length > 0){
                orgs.query.where.sourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected};
                courses.query.where.orgSourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected};
                classes.query.where.schoolSourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected};
                users.query.where.orgSourcedIds = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected}
                enrollments.query.where.schoolSourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected}
                roles.query.where.orgSourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected}
            }
            
            if(data.municipalId === null || data.municipalId === '' || data.municipalId === undefined){ 
                return done({code:`SCD0001`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0001')}`,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }

            let pathFolder = `csv/${data.municipalId}/${initData.folderName}`;
            
            if(data?.outputOperation === OUTPUT_OPERATION_SCHEDULE_TO_BLOB || data?.outputOperation === OUTPUT_OPERATION_TO_BLOB_ONCE) {
                try {
                    const blobContainerClient = new ContainerClient(`${data.blobURL}${data.blobKey}`);  //start connection to blob use sas token
                    // check upload permission to blob

                    const blockBlobClient = blobContainerClient.getBlockBlobClient('index.html');                
                    try {
                        await blockBlobClient.uploadFile(`index.html`, {onProgress: (ev) => console.log(ev)});
                    } catch (err) {
                        return done({code:`SCD0003`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0003')}`,data:err?.code,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
                    }
                } catch(err){
                    return done({code:`SCD0010`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0010'),data:err,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
                }
            }

            switch(data?.outputTarget){
                case OUTPUT_TARGET_ALL:
                    break
                case OUTPUT_TARGET_TEACHER:
                    users.query.where.role = { [db[job.data.municipalId].Sequelize.Op.ne]: `${OUTPUT_TARGET_STUDENT}` } 
                    enrollments.query.where.role = { [db[job.data.municipalId].Sequelize.Op.ne]: `${OUTPUT_TARGET_STUDENT}` } 
                    roles.query.where.role = { [db[job.data.municipalId].Sequelize.Op.ne]: `${OUTPUT_TARGET_STUDENT}` } 
                    break
                case OUTPUT_TARGET_STUDENT:
                    users.query.where.role = { [db[job.data.municipalId].Sequelize.Op.eq]: `${OUTPUT_TARGET_STUDENT}` } 
                    enrollments.query.where.role = { [db[job.data.municipalId].Sequelize.Op.eq]: `${OUTPUT_TARGET_STUDENT}` } 
                    roles.query.where.role = { [db[job.data.municipalId].Sequelize.Op.eq]: `${OUTPUT_TARGET_STUDENT}` } 
                    break
                case "all_unmatch":
                    roles.query.where.role = { [db[job.data.municipalId].Sequelize.Op.eq]: `${'all_unmatch'}` }
                    break
                default:
                    return done({code:`SCD0004`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0004').replace("%OUTPUT_TARGET_ALL%", `${OUTPUT_TARGET_ALL}`).replace("%OUTPUT_TARGET_TEACHER%",`${OUTPUT_TARGET_TEACHER}`).replace("%OUTPUT_TARGET_STUDENT%",`${OUTPUT_TARGET_STUDENT}`),executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }
            
            switch(data?.outputRange){
                case OUTPUT_RANGE_BULK:
                    academic_sessions.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'title', 'type', 'startDate', 'endDate', 'nullValueString', 'schoolYear' ]
                    courses.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'schoolYearSourcedId', 'title', 'courseCode', 'grades', 'orgSourcedId', 'subjects', 'subjectCodes' ] 
                    classes.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'title', 'grades', 'courseSourcedId', 'classCode', 'classType', 'location', 'schoolSourcedId', 'termSourcedIds', 'subjects', 'subjectCodes', 'periods' ] 
                    enrollments.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'classSourcedId', 'schoolSourcedId', 'userSourcedId', 'role', 'primary', 'beginDate', 'endDate' ] 
                    roles.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'userSourcedId', 'roleType', 'role', 'nullValue', 'nullValue', 'orgSourcedId', 'nullValue' ] 
                    
                    academic_sessions.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'title', value: 'title' },{ label: 'type', value: 'type' },{ label: 'startDate', value: 'startDate' },{ label: 'endDate', value: 'endDate' },{ label: 'parentSourcedId', value: 'nullValueString' },{ label: 'schoolYear', value: 'schoolYear' } ] 
                    courses.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'schoolYearSourcedId', value: 'schoolYearSourcedId' },{ label: 'title', value: 'title' },{ label: 'courseCode', value: 'courseCode' },{ label: 'grades', value: 'grades' },{ label: 'orgSourcedId', value: 'orgSourcedId' },{ label: 'subjects', value: 'subjects' },{ label: 'subjectCodes', value: 'subjectCodes' } ] 
                    classes.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'title', value: 'title' },{ label: 'grades', value: 'grades' },{ label: 'courseSourcedId', value: 'courseSourcedId' },{ label: 'classCode', value: 'classCode' },{ label: 'classType', value: 'classType' },{ label: 'location', value: 'location' },{ label: 'schoolSourcedId', value: 'schoolSourcedId' },{ label: 'termSourcedIds', value: 'termSourcedIds' },{ label: 'subjects', value: 'subjects' },{ label: 'subjectCodes', value: 'subjectCodes' },{ label: 'periods', value: 'periods' } ] 
                    roles.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'userSourcedId', value: 'userSourcedId' },{ label: 'roleType', value: 'roleType' },{ label: 'role', value: 'role' },{ label: 'beginDate', value: 'nullValue' },{ label: 'endDate', value: 'nullValue' },{ label: 'orgSourcedId', value: 'orgSourcedId' },{ label: 'userProfileSourcedId', value: 'nullValue' } ]
                    
                    if (job.data.orVersion == 11) {
                        orgs.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'name', 'type', 'identifier', 'parentSourcedId' ] 
                        users.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'enabledUser', 'orgSourcedIds', 'role', 'username', 'userIds', 'givenName', 'familyName', 'middleName', 'identifier', 'email', 'sms', 'phone', 'agentSourcedIds', 'grades', 'password' ] 

                        orgs.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'name', value: 'name' },{ label: 'type', value: 'type' },{ label: 'identifier', value: 'identifier' },{ label: 'parentSourcedId', value: 'parentSourcedId' } ] 
                        users.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'enabledUser', value: 'enabledUser' },{ label: 'orgSourcedIds', value: 'orgSourcedIds' },{ label: 'role', value: 'role' },{ label: 'username', value: 'username' },{ label: 'userIds', value: 'userIds' },{ label: 'givenName', value: 'givenName' },{ label: 'familyName', value: 'familyName' },{ label: 'middleName', value: 'middleName' },{ label: 'identifier', value: 'identifier' },{ label: 'email', value: 'email' },{ label: 'sms', value: 'sms' },{ label: 'phone', value: 'phone' },{ label: 'agentSourcedIds', value: 'agentSourcedIds' },{ label: 'grades', value: 'grades' },{ label: 'password', value: 'nullValue' } ] 
                        enrollments.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'classSourcedId', value: 'classSourcedId' },{ label: 'schoolSourcedId', value: 'schoolSourcedId' },{ label: 'userSourcedId', value: 'userSourcedId' },{ label: 'role', value: 'role' },{ label: 'primary', value: 'primary' },{ label: 'beginDate', value: 'beginDate' },{ label: 'endDate', value: 'endDate' } ]    
                    }else{
                        orgs.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'name', 'type', 'schoolCode', 'parentSourcedId' ] 
                        users.query.attributes = [ 'sourcedId', 'nullValue', 'nullValue', 'enabledUser', 'username', 'userIds', 'givenName', 'familyName', 'middleName', 'identifier', 'email', 'sms', 'phone', 'agentSourcedIds', 'grades', 'password', 'nullValue', 'nullValue', 'nullValue', 'nullValue', 'orgSourcedIds', 'nullValue' ] 

                        orgs.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'name', value: 'name' },{ label: 'type', value: 'type' },{ label: 'identifier', value: 'schoolCode' },{ label: 'parentSourcedId', value: 'parentSourcedId' } ] 
                        users.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'enabledUser', value: 'enabledUser' },{ label: 'username', value: 'username' },{ label: 'userIds', value: 'userIds' },{ label: 'givenName', value: 'givenName' },{ label: 'familyName', value: 'familyName' },{ label: 'middleName', value: 'middleName' },{ label: 'identifier', value: 'identifier' },{ label: 'email', value: 'nullValue' },{ label: 'sms', value: 'sms' },{ label: 'phone', value: 'phone' },{ label: 'agentSourcedIds', value: 'agentSourcedIds' },{ label: 'grades', value: 'grades' },{ label: 'password', value: 'nullValue' },{ label: 'userMasterIdentifier', value: 'sourcedId' },{ label: 'resourceSourcedIds', value: 'nullValue' },{ label: 'preferredGivenName', value: 'givenName' },{ label: 'preferredMiddleName', value: 'middleName' },{ label: 'preferredFamilyName', value: 'familyName' },{ label: 'primaryOrgSourcedId', value: 'orgSourcedIds' },{ label: 'pronouns', value: 'nullValue' } ] 
                        enrollments.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'nullValue' },{ label: 'dateLastModified', value: 'nullValue' },{ label: 'classSourcedId', value: 'classSourcedId' },{ label: 'schoolSourcedId', value: 'schoolSourcedId' },{ label: 'userSourcedId', value: 'userSourcedId' },{ label: 'role', value: 'role' },{ label: 'primary', value: 'primary' },{ label: 'beginDate', value: 'beginDate' },{ label: 'endDate', value: 'endDate' } ]
                    }

                    academic_sessions.query.where.status = "active" 
                    orgs.query.where.status = "active"
                    courses.query.where.status = "active" 
                    classes.query.where.status = "active"
                    users.query.where.status = "active"
                    enrollments.query.where.status = "active"
                    roles.query.where.status = "active"

                    break
                case OUTPUT_RANGE_DELTA:
                    if (job.data.orVersion != 11) {
                        orgs.query.attributes = [ 'sourcedId', 'status', 'dateLastModified', 'name', 'type', 'schoolCode', 'parentSourcedId' ] 
                        users.query.attributes = [ 'sourcedId', 'status', 'dateLastModified', 'enabledUser', 'username', 'userIds', 'givenName', 'familyName', 'middleName', 'identifier', 'email', 'sms', 'phone', 'agentSourcedIds', 'grades', 'password', 'nullValue', 'nullValue', 'nullValue', 'nullValue', 'nullValue', 'orgSourcedIds', 'nullValue' ] 

                        orgs.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'status' },{ label: 'dateLastModified', value: 'dateLastModified' },{ label: 'name', value: 'name' },{ label: 'type', value: 'type' },{ label: 'identifier', value: 'schoolCode' },{ label: 'parentSourcedId', value: 'parentSourcedId' } ] 
                        users.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'status' },{ label: 'dateLastModified', value: 'dateLastModified' },{ label: 'enabledUser', value: 'enabledUser' },{ label: 'username', value: 'username' },{ label: 'userIds', value: 'userIds' },{ label: 'givenName', value: 'givenName' },{ label: 'familyName', value: 'familyName' },{ label: 'middleName', value: 'middleName' },{ label: 'identifier', value: 'identifier' },{ label: 'email', value: 'nullValue' },{ label: 'sms', value: 'sms' },{ label: 'phone', value: 'phone' },{ label: 'agentSourcedIds', value: 'agentSourcedIds' },{ label: 'grades', value: 'grades' },{ label: 'password', value: 'nullValue' },{ label: 'userMasterIdentifier', value: 'sourcedId' },{ label: 'resourceSourcedIds', value: 'nullValue' },{ label: 'preferredGivenName', value: 'givenName' },{ label: 'preferredMiddleName', value: 'middleName' },{ label: 'preferredFamilyName', value: 'familyName' },{ label: 'primaryOrgSourcedId', value: 'orgSourcedIds' },{ label: 'pronouns', value: 'nullValue' } ] 
                        enrollments.header = [ { label: 'sourcedId', value: 'sourcedId' },{ label: 'status', value: 'status' },{ label: 'dateLastModified', value: 'dateLastModified' },{ label: 'classSourcedId', value: 'classSourcedId' },{ label: 'schoolSourcedId', value: 'schoolSourcedId' },{ label: 'userSourcedId', value: 'userSourcedId' },{ label: 'role', value: 'role' },{ label: 'primary', value: 'nullValue' },{ label: 'beginDate', value: 'beginDate' },{ label: 'endDate', value: 'endDate' } ]
                    }

                    let startDate = moment().subtract(data.outputRangeDay, 'days').format('YYYY-MM-DD')
                    academic_sessions.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    orgs.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    courses.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    classes.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    users.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    enrollments.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    roles.query.where.dateLastModified = { [db[job.data.municipalId].Sequelize.Op.gte]: `${startDate} 00:00:00` } 
                    
                    if(data.outputRangeDay === null || data.outputRangeDay === '' || data.outputRangeDay === undefined || data.outputRangeDay < 1 || data.outputRangeDay > 31){
                        return done({code:`SCD0002`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0002')}`,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
                    }
                    break

                case SINGLE_EXPORT:
                    
                    import_users.query.where.option = { [db[job.data.municipalId].Sequelize.Op.or] : ["add_csv_to_lgate"] }
                    import_users.query.where.municipalId = job.data.municipalId

                    console.log({sid:data.schoolSelected})
                    
                    if(data.schoolSelected && data.schoolSelected.length > 0)
                        import_users.query.where.orgSourcedIds = { [db[job.data.municipalId].Sequelize.Op.in]: data.schoolSelected}
    
                    break
                default:
                    return done({code:`SCD0005`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0005').replace("%OUTPUT_RANGE_BULK%", `${OUTPUT_RANGE_BULK}`).replace("%OUTPUT_RANGE_DELTA%",`${OUTPUT_RANGE_DELTA}`),executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }

            if(data?.outputTargetAcademicSession?.length < 1){
                return done({code:`SCD0007`,type:LOG_TYPE_ERROR,message:`${lang.t('scheduler.error.SCD0007')}`,executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }
            
            if(offset == 0){
                yearId = []
                let academicSessionSelected;
                
                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_PAST)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            startDate : { [db[job.data.municipalId].Sequelize.Op.lte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').subtract(1,'y').format('YYYY-MM-DD') },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })

                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }
                
                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_LAST)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            startDate :{ [db[job.data.municipalId].Sequelize.Op.lte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').subtract(1,'y').format('YYYY-MM-DD') },
                            endDate : { [db[job.data.municipalId].Sequelize.Op.gte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').subtract(1,'y').format('YYYY-MM-DD') },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })
                    
                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }
                
                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_CURRENT)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            startDate :{ [db[job.data.municipalId].Sequelize.Op.lte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD') },
                            endDate : { [db[job.data.municipalId].Sequelize.Op.gte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD') },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })
                    
                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }
                
                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_NEXT)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            startDate :{ [db[job.data.municipalId].Sequelize.Op.lte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').add(1,'y').format('YYYY-MM-DD') },
                            endDate : { [db[job.data.municipalId].Sequelize.Op.gte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').add(1,'y').format('YYYY-MM-DD') },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })
                    
                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }
                
                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_FUTURE)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.ne]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            endDate : { [db[job.data.municipalId].Sequelize.Op.gte]: moment(initData.currentDateFormat,'YYYY-MM-DD HH:mm:ss').add(1,'y').format('YYYY-MM-DD') },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })
                    
                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }

                if(data?.outputTargetAcademicSession.includes(OUTPUT_TARGET_ACADEMIC_SESSION_INFINITY)){
                    academicSessionSelected = await db[job.data.municipalId].academicSessions.findAll({
                        attributes: ["title","sourcedId","endDate","startDate"],
                        where: {
                            title : { [db[job.data.municipalId].Sequelize.Op.eq]: config.ACADEMIC_SESSION_INFINITY_TITLE },
                            municipalId : { [db[job.data.municipalId].Sequelize.Op.eq]: job.data.municipalId}
                        }
                    })
                    
                    academicSessionSelected.map((item)=>{
                        if(!yearId.includes(item.sourcedId)){
                            yearId.push(item.sourcedId)
                        }
                    }) 
                }
            }      

            if(yearId?.length > 0){
                academic_sessions.query.where.sourcedId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
                courses.query.where.yearId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
                classes.query.where.yearId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
                users.query.where.yearId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
                enrollments.query.where.yearId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
                roles.query.where.yearId = { [db[job.data.municipalId].Sequelize.Op.in]: yearId } 
            }

            switch(tables[tableIndex]){
                case TABLE_NAME_ACADEMIC_SESSIONS:

                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)
                    
                    currentTableName = TABLE_NAME_ACADEMIC_SESSIONS
                    
                    if(yearId){
                        currentTableData = await db[job.data.municipalId].academicSessions.findAll(academic_sessions.query)
                    } else {
                        currentTableData = null
                    }

                    currentTableHeader = academic_sessions.header
                    currentFileName = CSV_FILENAME_ACADEMIC_SESSIONS
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }
    
                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);
    
                        currentTableStatus = academic_sessions.query.status = STATUS_PROCESSING
                        academic_sessions.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = academic_sessions.query.status = STATUS_COMPLETED
                    }
                    

                    break
                case TABLE_NAME_ORGS:

                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)
                    currentTableName = TABLE_NAME_ORGS
                    currentTableData = await db[job.data.municipalId].orgs.findAll(orgs.query)
                    currentTableHeader = orgs.header
                    currentFileName = CSV_FILENAME_ORGS
                    
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }

                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);

                        currentTableStatus = orgs.query.status = STATUS_PROCESSING
                        orgs.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = orgs.query.status = STATUS_COMPLETED
                    }
                    

                    break
                case TABLE_NAME_COURSES:
                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)
                    currentTableName = TABLE_NAME_COURSES
                    if(yearId){
                        currentTableData = await db[job.data.municipalId].courses.findAll(courses.query)
                    } else {
                        currentTableData = null
                    }
                    currentTableHeader = courses.header
                    currentFileName = CSV_FILENAME_COURSES
                    
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }

                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);

                        currentTableStatus = courses.query.status = STATUS_PROCESSING
                        courses.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = courses.query.status = STATUS_COMPLETED
                    }

                    break
                case TABLE_NAME_CLASSES:
                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)

                    if(config.EXPORT_METADATA_JP){
                        let metaJpAttributes = ['metadataJpSpecialNeeds']
                        classes.query.attributes = classes.query.attributes.concat(metaJpAttributes)
                        
                        let metaJpHeader = [
                            {
                                label: 'metadata.jp.specialNeeds',
                                value: 'metadataJpSpecialNeeds'
                            }
                        ]
                        classes.header = classes.header.concat(metaJpHeader)
                    }

                    currentTableName = TABLE_NAME_CLASSES
                    if(yearId){
                        currentTableData = await db[job.data.municipalId].classes.findAll(classes.query)
                    } else {
                        currentTableData = null
                    }
                    currentTableHeader = classes.header
                    currentFileName = CSV_FILENAME_CLASSES
                    
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }
                        
                        if (job.data.orVersion == 12) {
                            for (var z = currentTableData.length - 1; z >= 0; z--) {
                                if(currentTableData[z].grades == "zz"){
                                    currentTableData[z].grades = "";
                                }
                            }
                        }

                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);
    
                        currentTableStatus = classes.query.status = STATUS_PROCESSING
                        classes.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = classes.query.status = STATUS_COMPLETED
                    }
                    
                    break
                case TABLE_NAME_USERS:
                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)
                    if(config.EXPORT_METADATA_JP){
                        let metaJpAttributes = ['metadataJpKanaGivenName','metadataJpKanaFamilyName','metadataJpKanaMiddleName','metadataJpHomeClass']
                        users.query.attributes = users.query.attributes.concat(metaJpAttributes)
                        
                        let metaJpHeader = [
                            {
                                label: 'metadata.jp.kanaGivenName',
                                value: 'metadataJpKanaGivenName'
                            },
                            {
                                label: 'metadata.jp.kanaFamilyName',
                                value: 'metadataJpKanaFamilyName'
                            },
                            {
                                label: 'metadata.jp.kanaMiddleName',
                                value: 'metadataJpKanaMiddleName'
                            }
                        ]

                        if (job.data.orVersion == 11) {
                            metaJpHeader.push({label: 'metadata.jp.homeClass',value: 'metadataJpHomeClass'});
                        }else{
                            metaJpHeader.push({label: 'metadata.jp.homeClass',value: 'metadataJpHomeClass'});
                        }

                        users.header = users.header.concat(metaJpHeader)
                    }

                    currentTableName = TABLE_NAME_USERS
                    if(yearId){
                        currentTableData = await db[job.data.municipalId].users.findAll(users.query)
                    } else {
                        currentTableData = null
                    }
                    currentTableHeader = users.header
                    currentFileName = CSV_FILENAME_USERS
                    
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }

                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);

                        currentTableStatus = users.query.status = STATUS_PROCESSING
                        users.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = users.query.status = STATUS_COMPLETED
                    }

                    break
                case TABLE_NAME_ENROLLMENTS:
                    // logger.info(`Scheduler Job(#${job.id}) is run process table '${tables[tableIndex]}' data rows [${offset+1} ~ ${offset+limit}]`)
                    if(config.EXPORT_METADATA_JP){
                        let metaJpAttributes = ['metadataJpShussekiNo','metadataJpPublicFlag']
                        enrollments.query.attributes = enrollments.query.attributes.concat(metaJpAttributes)

                        let metaJpHeader = [
                            {
                                label: 'metadata.jp.ShussekiNo',
                                value: 'metadataJpShussekiNo'
                            },
                            {
                                label: 'metadata.jp.PublicFlg',
                                value: 'metadataJpPublicFlag'
                            },
                        ]
                        enrollments.header = enrollments.header.concat(metaJpHeader)
                    }

                    currentTableName = TABLE_NAME_ENROLLMENTS
                    if(yearId){
                        currentTableData = await db[job.data.municipalId].enrollments.findAll(enrollments.query)
                    } else {
                        currentTableData = null
                    }
                    currentTableHeader = enrollments.header
                      
                    currentFileName = CSV_FILENAME_ENROLLMENTS
                    
                    if(currentTableData?.length > 0){
                        if(offset == 0){
                            if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                            }
                        }

                        if(data?.outputRange != SINGLE_EXPORT)
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);
    
                        currentTableStatus = enrollments.query.status = STATUS_PROCESSING
                        enrollments.query.exported = offset + currentTableData?.length
                    } else {
                        currentTableStatus = enrollments.query.status = STATUS_COMPLETED
                    }
                    break
                case TABLE_NAME_ROLES:
                    if (job.data.orVersion == 11) {
                        currentTableStatus = roles.query.status = STATUS_COMPLETED
                    }else{
                        currentTableName = TABLE_NAME_ROLES
                        if(yearId){
                            currentTableData = await db[job.data.municipalId].roles.findAll(roles.query)
                        } else {
                            currentTableData = null
                        }
                        currentTableHeader = roles.header
                          
                        currentFileName = CSV_FILENAME_ROLES
                        
                        if(currentTableData?.length > 0){
                            if (job.data.orVersion != 11) {
                                for (var i = currentTableData.length - 1; i >= 0; i--) {
                                    if (currentTableData[i].role == 'administrator') {
                                        currentTableData[i].role = "districtAdministrator";   
                                    }
                                }
                            }
                            if(offset == 0){
                                if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                    unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                                }
                            }

                            if(data?.outputRange != SINGLE_EXPORT)
                                await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);

                            currentTableStatus = roles.query.status = STATUS_PROCESSING
                            roles.query.exported = offset + currentTableData?.length
                        } else {
                            currentTableStatus = roles.query.status = STATUS_COMPLETED
                        }
                    }
                    break
                case TABLE_NAME_IMPORT_USERS:
                    if(data?.outputRange != SINGLE_EXPORT){
                        currentTableStatus = import_users.query.status = STATUS_COMPLETED
                    }else{
                        currentTableName = TABLE_NAME_IMPORT_USERS
                        if(yearId){
                            currentTableData = await db[job.data.municipalId].importUsers.findAll(import_users.query)
                        } else {
                            currentTableData = null
                        }
                        currentTableHeader = import_users.header
                        currentFileName = TABLE_NAME_IMPORT_USERS
                        
                        if(currentTableData?.length > 0){
                            if(offset == 0){
                                if (existsSync(`${pathFolder}/${currentFileName}.csv`)) {
                                    unlinkSync(`${pathFolder}/${currentFileName}.csv`)
                                }
                            }
                            await writecsv(`${currentFileName}.csv`, pathFolder, currentTableHeader, currentTableData);
                            currentTableStatus = import_users.query.status = STATUS_PROCESSING
                            import_users.query.exported = offset + currentTableData?.length
                        } else {
                            currentTableStatus = import_users.query.status = STATUS_COMPLETED
                        }
                    }    
                break
            
                default:

                break

            }


            switch(currentTableStatus){
                case STATUS_PROCESSING:
                    await this.onProcess(job,done,limit,(offset+limit),progressPercent,yearId,initData)
                    break
                case STATUS_COMPLETED:
                    return done(null,{
                        status:true,
                        message: lang.t('scheduler.message.processed').replace('%TABLE%',currentTableName),executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName
                    })
                default:
                    return done({code:`SCD0008`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0008'),executionTime:initData.executionTime, procedDate: initData.procedDate, folderName:initData.folderName})
            }
    }

    onWaiting = async (jobId) => {
        let content = {type:LOG_TYPE_INFO,message:lang.t('scheduler.message.onWaiting').replace('%JOB_ID%',`${jobId}`)}
        LOG.create(content);
    }

    onError = async (error) => {
        let content = {code :'SCD0009',type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0009').replace('%ERROR_MESSAGE%',`${error}`),executionTime:0}
        LOG.create(content);
    }

    onProgress = async (job, progress) => {
        
        let message = lang.t('scheduler.message.onProgress').replace('%SCHEDULER_NAME%',`${job.data.scheduleName}`).replace('%MESSAGE%',`${progress.message}`)
        
        let content = {
            jobId: job.data.uniqueIdJob,
            municipalId: job.data.municipalId,
            type: STATUS_PROCESSING,
            userId: '-',
            message: message,
            outputOperation: job.data.outputOperation,
            progress: progress?.percent,
            payloadRequest: job.data,
            notifUUID: job.data.notifUUID
        }
        console.log('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',`${job.data.uniqueIdJob}`, progress?.percent,'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        this.notificationsLog(content);
        
        content.executionTime = moment().diff(progress.executionTime,"seconds",true)
        LOG.create(content);
    }

    onRemoved = async (job) => {
        let content = {type:LOG_TYPE_INFO,message:lang.t('scheduler.message.onRemoved').replace('%SCHEDULER_NAME%',`${job.data.scheduleName}`)}
        this.loggerJob(1,job.data,content,job)
        LOG.create(content);
    }

    onCompleted = async (job,result) => {
        let resultCSVZip = await this.csvZipToBLOB(job,result)
        if(resultCSVZip.status){
            if(resultCSVZip.percent == 100){

                await db[job.data.municipalId].scheduler.update({
                    statusJob : 2
                },{
                    where : { uniqueIdJob : job.data.uniqueIdJob}
                })
                
                let message = lang.t('scheduler.message.onCompleted').replace('%SCHEDULER_NAME%',job.data.scheduleName).replace('%MESSAGE%',resultCSVZip?.message)
                
                console.log('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',resultCSVZip?.percent,'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                this.notificationsLog({
                    jobId: job.data.uniqueIdJob,
                    municipalId: job.data.municipalId,
                    type: STATUS_COMPLETED,
                    userId: '-',
                    message: message,
                    link: resultCSVZip.link,
                    path: resultCSVZip.path,
                    outputOperation: job.data.outputOperation,
                    progress: resultCSVZip?.percent,
                    payloadRequest: job.data,
                    notifUUID: job.data.notifUUID
                });
                
                let processedOn1 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[0]}`)
                let processedOn2 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[1]}`)
                let processedOn3 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[2]}`)
                let processedOn4 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[3]}`)
                let processedOn5 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[4]}`)
                let processedOn6 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[5]}`)
                let processedOn7 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[6]}`)
                let processedOn8 = await redisClient.get(`${job.data.uniqueIdJob}_${tables[7]}`)
                let processedOnArr = [processedOn1,processedOn2,processedOn3,processedOn4,processedOn5,processedOn6,processedOn7,processedOn8]

                let content = {type:LOG_TYPE_SUCCESS,message:message,result:result,executionTime:moment().diff(result.executionTime,"seconds",true)}
                this.loggerJob(1,job.data,content,job)
                LOG.create(content);
                // AZURELOG.create(`export,${job.data.municipalName} ${job.data.scheduleName}(${moment().format('YYYY-MM-DD')}),${LOG_TYPE_SUCCESS},`);
                
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[0]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[1]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[2]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[3]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[4]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[5]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[6]}`)
                await redisClient.del(`${job.data.uniqueIdJob}_${tables[7]}`)
            } else {
                this.onProgress(job,{
                    processing: tables[job.data.tableIndex],
                    percent: resultCSVZip?.percent,
                    message: resultCSVZip.message
                })
            }
        }
    }

    onFailed = async (job, err) => {
        if(err?.code){
            err.message = lang.t('scheduler.message.onFailed').replace('%SCHEDULER_NAME%',job.data.scheduleName).replace('%MESSAGE%',err?.message)
        } else {
            err.message = lang.t('scheduler.message.onFailedError').replace('%SCHEDULER_NAME%',job.data.scheduleName).replace('%MESSAGE%',err?.message)
        }

        await db[job.data.municipalId].scheduler.update({
            statusJob : 3
        },{
            where : { uniqueIdJob : job.data.uniqueIdJob}
        })

        let content = {
            jobId: job.data.uniqueIdJob,
            municipalId: job.data.municipalId,
            type: STATUS_FAILED,
            userId: '-',
            message: err.message,
            outputOperation: job.data.outputOperation,
            progress: 0,
            payloadRequest: job.data,
            notifUUID: job.data.notifUUID
        }
        
        this.notificationsLog(content)
        LOG.create(content);
        err.executionTime= moment().diff(err?.executionTime,"seconds",true)
        this.loggerJob(0,job.data,err,job)

        redisClient.del(job.id);
    }

    loggerJob = async (status,data,content,job=null) => {
        content.job = JSON.parse(JSON.stringify(job))
        await db[data?.municipalId].schedulerLog.upsert({
            createdDate: `${moment(job.processedOn).format('YYYY-MM-DD HH:mm:ss')}`,
            scheduleDate: `${moment(job.opts.timestamp).add(job.opts.delay,'ms').format('YYYY-MM-DD HH:mm:ss')}`,
            scheduleTitle: data?.scheduleName,
            municipalId: data?.municipalId,
            scheduleJobId: job.data.uniqueIdJob,
            scheduleDetail: JSON.stringify(data),
            status: status,
            scheduleLogId: `${unqieJobId(job)}`,
            content: typeof content === 'string' || content instanceof String ? content : JSON.stringify(content)
        })

    }
    
    notificationsLog = async(data) => {
        await db[data?.municipalId].notifications.update({
            jobId: data?.jobId,
            municipalId: data?.municipalId,
            type: data?.type,
            userId: data?.userId,
            message: data?.message,
            link: data?.link,
            path: data?.path,
            outputOperation: data?.outputOperation,
            progress: data?.progress ? data?.progress : 0,
            payloadRequest: typeof data?.payloadRequest === 'string' || data?.payloadRequest instanceof String ? data?.payloadRequest : JSON.stringify(data?.payloadRequest),
            createdDate: `${moment().format('YYYY-MM-DD HH:mm:ss')}`
        },{
            where: { uuid: data.notifUUID }
        });
    }

    csvZipToBLOB = async(job,result) => {        
        await redisClient.set(`${job.data.uniqueIdJob}_${tables[job.data.tableIndex]}`, 1);

        let zipRedisName = `${job.data.uniqueIdJob}_${CSV_ZIP_TO_BLOB}`
        let zipRedis = await redisClient.get(zipRedisName)
        let percent = 0
                
        let pathFolder = `csv/${job.data.municipalId}/${result.folderName}`;
        let zipName = `${result.folderName}.zip`;
        let pathZip = `csv/${job.data.municipalId}/${zipName}`;
        let downloadLink = '';
        
        let progressAllJob = await this.countProgress(job)

        if( tables.length === progressAllJob && zipRedis == ''){
            await redisClient.set(zipRedisName, job.id);
            await sleep(1000)
            
            let zipRedisNew = await redisClient.get(zipRedisName)
            if(zipRedisNew == job.id){
                
                    await this.manifestCSV(pathFolder,job.data.outputRange,job.data.orVersion);

                    await zipper(pathFolder, pathZip);

                    // create manifest here

                    if(job.data?.outputOperation === OUTPUT_OPERATION_SCHEDULE_TO_BLOB || job.data?.outputOperation === OUTPUT_OPERATION_TO_BLOB_ONCE) {
                        try{
                            const blobContainerClient = new ContainerClient(`${job.data.blobURL}${job.data.blobKey}`);  //start connection to blob use sas token
                            if (existsSync(pathZip)) {              
                                const blobName = `${job.data.municipalName}/${zipName}`;
                                const blockBlobClient = blobContainerClient.getBlockBlobClient(blobName);
                                try {
                                    const uploadBlobResponse = await blockBlobClient.uploadFile(pathZip, {
                                        onProgress: (ev) => console.log(ev)
                                    });
                                    
                                    if(uploadBlobResponse){
                                        let blobURL = job.data.blobURL.replace(/^\/+|\/+$/gm,'');
                                        downloadLink = `${blobURL}/${blobName}${job.data.blobKey}`
                                    }
                                } catch (err) {
                                    return {status:false,code:`SCD0006`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0006').replace("%blobName%", `${blobName}`),data:err?.code}
                                }
                            }
                        } catch(err){
                            return {status:false,code:`SCD0010`,type:LOG_TYPE_ERROR,message:lang.t('scheduler.error.SCD0010'),data:err}
                        }

                    } else {
                        downloadLink = `${config.BASE_URL}/api/scheduler/download/${job.data.uniqueIdJob}/${job.data.municipalId}`
                    }
                    

                    tables.map((tablename) => {
                        redisClient.del(`${job.data.uniqueIdJob}_${tablename}`);
                    })
                    redisClient.del(zipRedisName);
                    redisClient.del(`LOCK_EXPORT_${job.data.municipalId}`);

                    percent = Math.round(( progressAllJob / tables.length) * 100)
                    
                    return {
                        status:true,
                        message:lang.t('scheduler.message.completed'),
                        link:downloadLink,
                        percent: percent == 'NaN' || percent == 'Infinity' || isNumber(percent) == false ? 0 : percent,
                        path:pathZip
                    }

                

            }
        }
        
        percent = Math.round((progressAllJob / tables.length) * 100)
        return {
            status:true,
            message:lang.t('scheduler.message.processed').replace('%TABLE%',tables[job.data.tableIndex]),
            link:null,
            percent:percent,
            path:pathZip
        } 
    }

    countProgress = async(job) => {
        let progressTable = 0
        let progressAllTable = 0
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[0]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[1]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[2]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[3]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[4]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[5]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[6]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)
        progressTable = await redisClient.get(`${job.data.uniqueIdJob}_${tables[7]}`)
        progressAllTable = progressAllTable + parseInt(progressTable)

        return progressAllTable
    }

    manifestCSV = async(pathFolder,outputRange,orVersion) => {

        const manifestHeader =  [
            MANIFEST_PROPERTY_NAME_LABEL,
            MANIFEST_VALUE_LABEL,
        ]

        const manifestValue = outputRange === OUTPUT_RANGE_BULK ? MANIFEST_FILE_VALUE_BULK : MANIFEST_FILE_VALUE_DELTA

        const manifestAcamicSessions = checkFile(pathFolder,`${CSV_FILENAME_ACADEMIC_SESSIONS}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestOrgs = checkFile(pathFolder,`${CSV_FILENAME_ORGS}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestClasses = checkFile(pathFolder,`${CSV_FILENAME_CLASSES}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestCourses = checkFile(pathFolder,`${CSV_FILENAME_COURSES}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestUsers = checkFile(pathFolder,`${CSV_FILENAME_USERS}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestEnrollments = checkFile(pathFolder,`${CSV_FILENAME_ENROLLMENTS}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        const manifestRoles = checkFile(pathFolder,`${CSV_FILENAME_ROLES}.csv`) ? manifestValue : MANIFEST_FILE_VALUE_ABSENT
        let manifestBody = [];

        if (orVersion == 11 && outputRange != SINGLE_EXPORT) {
            manifestBody = [
                { propertyName : 'manifest.version'  , value : MANIFEST_VERSION } ,
                { propertyName : 'oneroster.version'  , value : orVersion.slice(0, 1) + "." + orVersion.slice(1) } ,
                { propertyName : 'file.academicSessions'  , value : manifestAcamicSessions } ,
                { propertyName : 'file.categories'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.classes'  , value : manifestClasses } ,
                { propertyName : 'file.classResources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.courses'  , value : manifestCourses } ,
                { propertyName : 'file.courseResources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.demographics'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.enrollments'  , value : manifestEnrollments } ,
                { propertyName : 'file.lineItems'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.orgs'  , value : manifestOrgs } ,
                { propertyName : 'file.resources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.results'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.users'  , value : manifestUsers } ,
                { propertyName : 'source.systemName'  , value : MANIFEST_SYSTEM_NAME } ,
                { propertyName : 'source.systemCode'  , value : MANIFEST_SYSTEM_CODE } 
            ]
        }
        
        if(orVersion != 11 && outputRange != SINGLE_EXPORT){
            manifestBody = [
                { propertyName : 'manifest.version'  , value : MANIFEST_VERSION } ,
                { propertyName : 'oneroster.version'  , value : orVersion.slice(0, 1) + "." + orVersion.slice(1) } ,
                { propertyName : 'file.academicSessions'  , value : manifestAcamicSessions } ,
                { propertyName : 'file.categories'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.classes'  , value : manifestClasses } ,
                { propertyName : 'file.classResources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.courses'  , value : manifestCourses } ,
                { propertyName : 'file.courseResources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.demographics'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.enrollments'  , value : manifestEnrollments } ,
                { propertyName : 'file.lineItemLearningObjectiveIds'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.lineItems'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.lineItemScoreScales'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.orgs'  , value : manifestOrgs } ,
                { propertyName : 'file.resources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.resultLearningObjectiveIds'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.results'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.resultScoreScales'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.roles'  , value : manifestRoles } ,
                { propertyName : 'file.scoreScales'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.userProfiles'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.userResources'  , value : MANIFEST_FILE_VALUE_ABSENT } ,
                { propertyName : 'file.users'  , value : manifestUsers } ,
                { propertyName : 'source.systemName'  , value : MANIFEST_SYSTEM_NAME } ,
                { propertyName : 'source.systemCode'  , value : MANIFEST_SYSTEM_CODE } 
            ]
        }

        if(outputRange == SINGLE_EXPORT){
            manifestBody = [
                { propertyName : 'manifest.version'  , value : MANIFEST_VERSION }
            ]
        }

        
        if (existsSync(`${pathFolder}/${CSV_FILENAME_MANIFEST}.csv`)) {
            unlinkSync(`${pathFolder}/${CSV_FILENAME_MANIFEST}.csv`)
        }

        await writecsv(`${CSV_FILENAME_MANIFEST}.csv`, pathFolder, manifestHeader, manifestBody);

        return `${CSV_FILENAME_MANIFEST}.csv`
    }

}

/**
 * Create new job id
 * @constructor
 */
const unqieJobId = (job) =>{
    return `${moment(job.opts.timestamp).format("YYYYMMDDHHmmss")}-${job.data.uniqueIdJob}`
}

/**
 * Process to validating file is exists on directory
 * @constructor
 */
const checkFile = (dir,filename) => {
    
    if (existsSync(`${dir}/${filename}`)) {  
        const dirents = readdirSync(dir, { withFileTypes: true });
        
        const index = dirents.findIndex((files)=>files.name == filename);
        return index >= 0 ? true : false
    } else {
        return false
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
 * Process to validating string is a numbers
 * @constructor
 */
const isNumber = (n) => {
    return /^-?[\d.]+(?:e-?\d+)?$/.test(n);
}

/**
 * Create export variable to running function SchedulerProcess
 * @constructor
 */
const schedulerQueueProcess = new SchedulerProcess()

export default schedulerQueueProcess