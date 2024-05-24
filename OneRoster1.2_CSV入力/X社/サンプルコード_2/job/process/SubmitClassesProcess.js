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
    DEFAULT_CLASSES_STATUS,
    LOG_TYPE_SUBMIT_MATCHING,
    CLASS_COLLATION,
    USER_ASSIGNMENT_SCREEN,
    ADMIN_TEACHER_COLLATION,
    STUDENT_COLLATION, 
    ADMINISTRATOR_COLLATION, 
    CLASS_ATENDANCE_COLLATION, 
    OTHER_ATENDANCE_COLLATION,
    MATCH_PRIORITY_EMAIL,
    MATCH_PRIORITY_NAME,
    MATCH_PRIORITY_ATTENDANCE_NUMBER,
    DEFAULT_MATCH_PRIORITY,
    SS_CLASS_NAME
} from "../../constants/constans.js";
import e from 'cors';
import { excludeArrayValue, mappingQueryArrayReturn, convertNullToString, convertDateForInsert } from '../../helpers/utility.js';
import LogHelper from "../../helpers/log.js";
const LOG = new LogHelper(CLASS_COLLATION);

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
 * Process to deleting import data related to data import classes that have status skip_csv_to_lgate or delete_add_from_lgate
 * @constructor
 */
export const deleteUsersImport = async (municipalId) => {
    const qDeleteImportUsers = `
        DELETE 
            import_users from import_users
        INNER JOIN import_enrollments
            ON import_users.sourcedId = import_enrollments.userSourcedId
        LEFT JOIN import_classes 
            ON import_enrollments.classSourcedId = import_classes.sourcedId 
        where import_classes.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteImportUsers);

    const qDeleteImportEnroll = `
        DELETE 
            import_enrollments from import_enrollments
        LEFT JOIN import_classes 
            ON import_enrollments.classSourcedId = import_classes.sourcedId 
        where import_classes.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteImportEnroll);

    //delete lgate
    const qDeleteLgateUsers = `
        DELETE 
            lgate_users from lgate_users
        LEFT JOIN import_users
            ON lgate_users.oldSourcedId = import_users.sourcedId
        where import_users.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteLgateUsers);

    const qDeleteLgateEnroll = `
        DELETE 
            lgate_enrollments from lgate_enrollments
        LEFT JOIN import_users 
            ON lgate_enrollments.userOldSourcedId = import_users.sourcedId
        where import_users.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteLgateEnroll);

    //delete rel
    const qDeleteRelUsers = `
        DELETE 
            rel_users from rel_users
        LEFT JOIN import_users
            ON rel_users.importSourcedId = import_users.sourcedId
        where rel_users.isTemp = 1 AND import_users.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteRelUsers);

    const qDeleteRelEnroll = `
        DELETE 
            rel_enrollments from rel_enrollments
        LEFT JOIN import_users 
            ON rel_enrollments.importUserSourcedId = import_users.sourcedId
        where rel_enrollments.isTemp = 1 AND import_users.sourcedId IS NULL`;
    await db[municipalId].query(qDeleteRelEnroll);
}

/**
 * Process to run function mergedUsers
 * @constructor
 */
export const mergedUsersImport = async (municipalId,role,classType) => {
    return await mergedUsers(municipalId,role,classType)
}

/**
 * Process to merged data of import_users table with data from users table along with its enrollment
 * @constructor
 */
const mergedUsers = async (municipalId,role,classType) => {
    const query = `
      SELECT
        import_users.*,
        COUNT(import_enrollments.classSourcedId) as totalEnrollment,
        GROUP_CONCAT(CONCAT_WS(":",import_enrollments.classSourcedId,import_enrollments.metadataJpShussekiNo)) as metadataJpShussekiNo,
        GROUP_CONCAT(import_enrollments.classSourcedId) as classSourcedId,
        GROUP_CONCAT(CONCAT_WS(":",import_enrollments.classSourcedId,import_enrollments.submited)) as submitedClassSourcedId,
        GROUP_CONCAT(CONCAT_WS(":",import_enrollments.classSourcedId,import_enrollments.option,import_enrollments.isParentSkiped)) as importEnrollmentOption,
        import_orgs.sourcedId as importOrgsId,
        GROUP_CONCAT(CONCAT_WS(":",import_classes.sourcedId,import_classes.classType)) as importClassUsers,
        import_roles.role as roleRelation,
        lgate_enrollments.id as lgateEnrollmentId,
        lgate_classes.oldSourcedId as lgateClassesId,
        rel_orgs.rosterSourcedId as rosterSchoolSourcedId
      FROM
        import_users
        LEFT JOIN import_enrollments ON import_enrollments.userSourcedId = import_users.sourcedId
        LEFT JOIN import_orgs ON import_orgs.sourcedId = import_users.orgSourcedIds AND import_orgs.option != 'skip_csv_to_lgate'
        LEFT JOIN import_classes ON import_classes.sourcedId = import_enrollments.classSourcedId AND import_classes.option != 'skip_csv_to_lgate'
        LEFT JOIN import_roles ON import_roles.userSourcedId = import_users.sourcedId
        LEFT JOIN lgate_enrollments ON lgate_enrollments.userOldSourcedId = import_users.sourcedId
        LEFT JOIN lgate_classes ON lgate_classes.oldSourcedId = lgate_enrollments.school_class_uuid AND lgate_classes.isParentSkiped = '0'
        LEFT JOIN rel_orgs ON rel_orgs.importSourcedId = import_users.orgSourcedIds
      WHERE
        (import_users.role IN ( ${JSON.stringify(role).replace("[","").replace("]","")} ) OR (import_roles.role IN ( ${JSON.stringify(role).replace("[","").replace("]","")} ) AND import_roles.roleType = 'primary') )
        AND import_users.municipalId = '${municipalId}' 
      GROUP BY
        import_users.sourcedId
    `;
    
    const [queryImport] = await db[municipalId].query(query)
  
    let sourcedId = [],username = [],givenName = [],familyName = [],metadataJpShussekiNo = [];
    
    queryImport.map(function(row) { 
        sourcedId.push(row.sourcedId); 
        username.push(row.username); 
        givenName.push(row.givenName); 
        familyName.push(row.familyName); 
        if (row.metadataJpShussekiNo != null) {
            const expAttendanceNo = row.metadataJpShussekiNo.split(',');
            for (let atn = 0; atn < expAttendanceNo.length; atn++) {
                const expAttdClass = expAttendanceNo[atn].split(':');
                if (expAttdClass.length > 1 && !metadataJpShussekiNo.includes(expAttdClass[1])) {
                    metadataJpShussekiNo.push(expAttdClass[1]);
                }
            }
        }
    });

    let metadataJpShussekiNoFilter = "";
    if (metadataJpShussekiNo.length > 0) {
        metadataJpShussekiNoFilter = `OR metadataJpShussekiNo IN (${JSON.stringify(metadataJpShussekiNo).replace("[","").replace("]","")})`;
    }
  
    if(queryImport.length){
        const query2 = `
            SELECT
              users.*,
              rel_users.importSourcedId as importSourcedIds,
              rel_users.rosterSourcedId as rosterSourcedIds,
              rel_orgs.importSourcedId as orgImportSourcedIds,
              classes.classType as lgateClassTypes,
              enrollments.metadataJpShussekiNo as metadataJpShussekiNo,
              enrollments.classSourcedId as classSourcedId
            FROM
              users
              LEFT JOIN enrollments ON enrollments.userSourcedId = users.sourcedId
              LEFT JOIN classes ON enrollments.classSourcedId = classes.sourcedId
              LEFT JOIN rel_orgs ON rel_orgs.rosterSourcedId = users.orgSourcedIds
              LEFT JOIN rel_classes ON rel_classes.rosterSourcedId = enrollments.classSourcedId
              LEFT JOIN rel_users ON rel_users.rosterSourcedId = users.sourcedId AND rel_users.isTemp = 0
            WHERE
              users.role IN ( ${JSON.stringify(role).replace("[","").replace("]","")} ) 
              AND users.STATUS = 'active' 
              AND users.municipalId = '${municipalId}' 
              AND (
                rel_users.importSourcedId IN (${JSON.stringify(sourcedId).replace("[","").replace("]","")})
                OR users.username IN (${JSON.stringify(username).replace("[","").replace("]","")})
                OR (users.givenName IN (${JSON.stringify(givenName).replace("[","").replace("]","")}) AND users.familyName IN (${JSON.stringify(familyName).replace("[","").replace("]","")}))
                ${metadataJpShussekiNoFilter}
              )
            GROUP BY
              users.sourcedId
        `;
  
        const [queryLgate] = await db[municipalId].query(query2)

        const getListSkipedClass = await db[municipalId].importClasses.findAll({
            attributes: ['sourcedId'],
            where: {
              municipalId: municipalId,
              option: { [Op.ne]: 'skip_csv_to_lgate' },
            },
        });
      
        let matchingPriority = DEFAULT_MATCH_PRIORITY;
        const matchingSetting = await db[municipalId].settingMatchingConditionModel.findOne({where: {municipalId: municipalId}})
        if (matchingSetting) {
            matchingPriority = matchingSetting.priority.split(',');
        }

        const updateParentSkiped = {
            'skiped0': [],
            'skiped1': []
        };
        const updateParentEnrSkiped = {
            'skiped0': [],
            'skiped1': []
        };
        const updateParentLEnrSkiped = {
            'skiped0': [],
            'skiped1': []
        };
        let unregisteredUsers = {};
        let adminTeacherUsers = {};
        let studentUsers = {};
        let adminUsers = {};
        let enrollClassUsers = {};
        let enrollGroupUsers = {};
        let redisSkippedData = await redisClient.get(`SKIPPED_USERS_${municipalId}`);
        redisSkippedData = redisSkippedData ? JSON.parse(redisSkippedData) : [];
        let queryMerged = await Promise.all(queryImport.map(async (row) => {
            if (row.option === 'add_from_lgate') {
              return row;
            }
            const skippedUser = redisSkippedData.findIndex(value => value.sourcedId === row.sourcedId);
            const prevOption = row.option; 
            let lgateIndex = -1;
            lgateIndex = queryLgate.findIndex((item)=>((item.importSourcedIds == row.sourcedId || item.rosterSourcedIds == row.sourcedId)));
            if(lgateIndex < 0){
                for (var i = 0; i < matchingPriority.length; i++) {
                    switch(matchingPriority[i]){
                        case MATCH_PRIORITY_EMAIL:
                            lgateIndex = queryLgate.findIndex((item)=> item.username == row.username);
                        break

                        case MATCH_PRIORITY_NAME:
                            lgateIndex = queryLgate.findIndex((item)=> item.givenName == row.givenName && item.familyName == row.familyName && row.rosterSchoolSourcedId == item.orgSourcedIds);
                        break

                        case MATCH_PRIORITY_ATTENDANCE_NUMBER:
                            if ((row.role == 'student' || row.roleRelation == 'student') && row.metadataJpShussekiNo != null) {
                                const rexpAttendanceNo = row.metadataJpShussekiNo.split(',');
                                for (let ratn = 0; ratn < rexpAttendanceNo.length; ratn++) {
                                    const rexpAttdClass = rexpAttendanceNo[ratn].split(':');
                                    if (rexpAttdClass.length > 1 && lgateIndex < 0) {
                                        lgateIndex = queryLgate.findIndex((item)=> parseInt(item.metadataJpShussekiNo) == parseInt(rexpAttdClass[1]) && row.rosterSchoolSourcedId == item.orgSourcedIds && rexpAttdClass[0] == item.classSourcedId);
                                    }
                                }
                            }
                        break
                    }

                    if (lgateIndex >= 0) {
                        i = matchingPriority.length;
                    }
                }
            }else{
                row.isDelta = 1;
            }

            if(lgateIndex >= 0){
                row.userIdLgate = queryLgate[lgateIndex].sourcedId
                row.userLgateName = `${queryLgate[lgateIndex].familyName} ${queryLgate[lgateIndex].givenName}`
                row.userLgatePassword = queryLgate[lgateIndex].password
                row.option = 'update_csv_to_lgate'
            } else {
                row.option = 'add_csv_to_lgate'
            }

            if (skippedUser >= 0 && !row.classSourcedId) {
                const cekSkipedClass = getListSkipedClass.findIndex((item)=> item.sourcedId == redisSkippedData[skippedUser].classSourcedId)
                row.lgateEnrollmentId = cekSkipedClass >= 0 ? redisSkippedData[skippedUser].classSourcedId : null;
                row.lgateClassesId = cekSkipedClass >= 0 ? redisSkippedData[skippedUser].classSourcedId : null;
            }

            if (row.submited === 0) {
                if (row.classSourcedId && !row.importClassUsers) {
                    row.option = 'skip_csv_to_lgate'
                    row.isParentSkiped = 1;
                } else {
                    row.isParentSkiped = 0;
                }
            } else if (row.submited === 1) {
                let isParentSkiped = row.isParentSkiped || 0;

                if (((row.classSourcedId && row.importClassUsers && prevOption === 'skip_csv_to_lgate') || (!row.classSourcedId && row.lgateClassesId))) {
                    if (row.isParentSkiped === 1) {
                        isParentSkiped = 0;
                    } else {
                        row.option = 'skip_csv_to_lgate';
                    }
                } else if (((row.classSourcedId && !row.importClassUsers && prevOption !== 'skip_csv_to_lgate') || (!row.classSourcedId && !row.lgateClassesId))) {
                    row.option = 'skip_csv_to_lgate'
                    isParentSkiped = 1;
                }
                row.isParentSkiped = isParentSkiped;
                if (isParentSkiped === 0) {
                    updateParentSkiped['skiped0'].push(row.sourcedId);
                } else if (isParentSkiped === 1) {
                    updateParentSkiped['skiped1'].push(row.sourcedId);
                }
            }

            // skip enrollment process
            const arrUserEnr = row.classSourcedId ? row.classSourcedId.split(',') : [];
            const arrUserEnrSubmited = row.submitedClassSourcedId ? row.submitedClassSourcedId.split(',') : [];
            const arrUserEnrOpt = row.importEnrollmentOption ? row.importEnrollmentOption.split(',') : [];
            const arrUserClassEnr = row.importClassUsers ? row.importClassUsers.split(',') : [];
            const arrUCEnr = {};
            for (let uce = 0; uce < arrUserClassEnr.length; uce++) {
                if (arrUserClassEnr[uce]) {
                    const expUserClassEnr = arrUserClassEnr[uce].split(":");
                    if (expUserClassEnr.length > 1) {
                        arrUCEnr[expUserClassEnr[0]] = expUserClassEnr[1]
                    }
                }
            }
            let totalUserEnrollment = 0;
            for (let ue = 0; ue < arrUserEnr.length; ue++) {
                if (!arrUserEnrOpt.includes(arrUserEnr[ue]+":skip_csv_to_lgate:0")) {
                    const enrParentSkiped = arrUCEnr[arrUserEnr[ue]] ? 0 : 1;
                    updateParentEnrSkiped['skiped'+enrParentSkiped].push({
                        classSourcedId: arrUserEnr[ue],
                        userSourcedId: row.sourcedId
                    })
                    updateParentLEnrSkiped['skiped'+enrParentSkiped].push({
                        school_class_uuid: arrUserEnr[ue],
                        userOldSourcedId: row.sourcedId
                    })
                    if (enrParentSkiped === 0) {
                        totalUserEnrollment++;
                    }
                }
            }
            if (row.importClassUsers && row.importOrgsId && totalUserEnrollment === 0) {
                row.option = 'skip_csv_to_lgate';
                row.isParentSkiped = 1;
                updateParentSkiped['skiped1'].push(row.sourcedId);
            }
            if (skippedUser >= 0) {
                redisSkippedData[skippedUser].isParentSkiped = row.isParentSkiped;
            }
            if (!row.classSourcedId) {
                if (!row.userIdLgate) row.option = 'add_csv_to_lgate'
                if (row.importOrgsId) {
                    if (unregisteredUsers[row.importOrgsId]) {
                        unregisteredUsers[row.importOrgsId].total++;
                    } else {
                        unregisteredUsers[row.importOrgsId] = {
                            'total': 1,
                            'registered': 0
                        };
                    }

                    if (row.lgateEnrollmentId && row.isParentSkiped === 0) {
                        unregisteredUsers[row.importOrgsId].registered++;
                    }
                }
            }
            row.role = row?.roleRelation ? row.roleRelation : row.role

            if (row.importClassUsers && row.importOrgsId) {
                if (row.role === "administrator" || row.role === "teacher") {
                    if (!adminTeacherUsers[row.importOrgsId]) {
                        adminTeacherUsers[row.importOrgsId] = {
                            'total': 1,
                            'registered': 0
                        };
                    } else {
                        adminTeacherUsers[row.importOrgsId].total++;
                    }
                    if (row.role === "administrator") {
                        if (!adminUsers[row.importOrgsId]) {
                            adminUsers[row.importOrgsId] = {
                                'total': 1,
                                'registered': 0
                            };
                        } else {
                            adminUsers[row.importOrgsId].total++;
                        }
                    }
                    if (row.submited === 1) {
                        adminTeacherUsers[row.importOrgsId].registered++;
                        if (row.role === "administrator") adminUsers[row.importOrgsId].registered++;
                    }
                }
                if (row.role === "student") {
                    if (!studentUsers[row.importOrgsId]) {
                        studentUsers[row.importOrgsId] = {
                            'total': 1,
                            'registered': 0
                        };
                    } else {
                        studentUsers[row.importOrgsId].total++;
                    }
                    if (row.submited === 1) {
                        studentUsers[row.importOrgsId].registered++;
                    }
                }
                if (row.role === "student" || row.role === "teacher") {
                    for (let key in arrUCEnr) {
                    if (arrUCEnr[key] === "homeroom") {
                        if (!enrollClassUsers[row.importOrgsId]) {
                            enrollClassUsers[row.importOrgsId] = {};
                        }
                        if (!enrollClassUsers[row.importOrgsId][key]) {
                            enrollClassUsers[row.importOrgsId][key] = {
                                'total': 1,
                                'registered': 0
                            };
                        } else {
                            enrollClassUsers[row.importOrgsId][key].total++;
                        }
                        if (arrUserEnrSubmited.includes(key+":1")) {
                            enrollClassUsers[row.importOrgsId][key].registered++;
                        }
                    } else if (arrUCEnr[key] === "scheduled") {
                        if (!enrollGroupUsers[row.importOrgsId]) {
                            enrollGroupUsers[row.importOrgsId] = {};
                        }
                        if (!enrollGroupUsers[row.importOrgsId][key]) {
                            enrollGroupUsers[row.importOrgsId][key] = {
                                'total': 1,
                                'registered': 0
                            };
                        } else {
                            enrollGroupUsers[row.importOrgsId][key].total++;
                        }
                        if (arrUserEnrSubmited.includes(key+":1")) {
                            enrollGroupUsers[row.importOrgsId][key].registered++;
                        }
                    }
                    }
                }
            }
            return row
        }));
        console.log(enrollClassUsers)
        console.log(enrollGroupUsers)
        await redisClient.set(`SKIPPED_USERS_${municipalId}`, JSON.stringify(redisSkippedData));

        for (let vp = 0; vp <= 1; vp++) {
            if (updateParentEnrSkiped['skiped'+vp].length > 0) {
                await db[municipalId].importEnrollments.update(
                    {
                        option: vp === 0 ? 'update_csv_to_lgate' : 'skip_csv_to_lgate',
                        isParentSkiped: vp
                    },
                    {
                        where: {
                            [Op.or]: updateParentEnrSkiped['skiped'+vp]
                        }
                    }
                );
            }
            if (updateParentLEnrSkiped['skiped'+vp].length > 0) {
                await db[municipalId].lgateEnrollments.update(
                    {
                        isParentSkiped: vp
                    },
                    {
                        where: {
                            [Op.or]: updateParentLEnrSkiped['skiped'+vp]
                        }
                    }
                );
            }
            if (updateParentSkiped['skiped'+vp].length > 0) {
                await db[municipalId].lgateUsers.update(
                    {
                        isParentSkiped: vp
                    },
                    { 
                        where: {
                            oldSourcedId: { [Op.in]: updateParentSkiped['skiped'+vp] },
                        }
                    }
                );
        
                await db[municipalId].lgateEnrollments.update(
                    {
                        isParentSkiped: vp
                    },
                    {
                        where: {
                            userOldSourcedId: { [Op.in]: updateParentSkiped['skiped'+vp] },
                        }
                    }
                );
            }
        }

        // ubah progress unregistered users
        const cekProgressProcess = await db[municipalId].importTaskProgress.findAll({
            where: {
                type: { [Op.in]: [ADMIN_TEACHER_COLLATION, USER_ASSIGNMENT_SCREEN, STUDENT_COLLATION, ADMINISTRATOR_COLLATION, CLASS_ATENDANCE_COLLATION, OTHER_ATENDANCE_COLLATION] },
                municipalId: municipalId
            },
        });
        const cekProgressProcessDetail = await db[municipalId].importTaskProgressDetail.findAll({
          where: {
              type: { [Op.in]: [ADMIN_TEACHER_COLLATION, USER_ASSIGNMENT_SCREEN, STUDENT_COLLATION, ADMINISTRATOR_COLLATION, CLASS_ATENDANCE_COLLATION, OTHER_ATENDANCE_COLLATION] },
              municipalId: municipalId
          },
        });
        const progressChange = [];
        const insTaskProgressDetail = [];
        const idxProgressAdmTea = cekProgressProcess.findIndex((item) => item.type === ADMIN_TEACHER_COLLATION)
        const idxProgressUnregist = cekProgressProcess.findIndex((item) => item.type === USER_ASSIGNMENT_SCREEN)
        const idxProgressStudent = cekProgressProcess.findIndex((item) => item.type === STUDENT_COLLATION)
        const idxProgressAdmin = cekProgressProcess.findIndex((item) => item.type === ADMINISTRATOR_COLLATION)
        const idxProgressEnrolClass = cekProgressProcess.findIndex((item) => item.type === CLASS_ATENDANCE_COLLATION)
        const idxProgressEnrolGroup = cekProgressProcess.findIndex((item) => item.type === OTHER_ATENDANCE_COLLATION)
        if (cekProgressProcess.length) {
            if (cekProgressProcess[idxProgressUnregist] && cekProgressProcess[idxProgressUnregist].id && cekProgressProcess[idxProgressUnregist].importStatus === 1) {
                let totalAllRegist = 0;
                let totalAllRPercent = 0;
                if (Object.keys(unregisteredUsers).length) {
                    for (let key in unregisteredUsers) {
                        totalAllRegist = totalAllRegist + unregisteredUsers[key].registered;
                        const percentROrgs = unregisteredUsers[key].registered < 1 ? 0 : (adminTeacherUsers[key].registered/unregisteredUsers[key].total)*100;
                        totalAllRPercent += percentROrgs;

                        if (key) {
                            let idxPdRegist = -1;
                            if (cekProgressProcessDetail.length > 0) { 
                                idxPdRegist = cekProgressProcessDetail.findIndex((item) => item.type === USER_ASSIGNMENT_SCREEN && item.orgSourcedId === key);
                            }
                            if (idxPdRegist < 0) {
                                insTaskProgressDetail.push({
                                    id: `${cekProgressProcess[idxProgressUnregist].municipalId}_${key}_${USER_ASSIGNMENT_SCREEN}`,
                                    importTaskProgressId: cekProgressProcess[idxProgressUnregist].id,
                                    municipalId: cekProgressProcess[idxProgressUnregist].municipalId,
                                    type: USER_ASSIGNMENT_SCREEN, 
                                    status: STATUS_COMPLETED,
                                    progress: percentROrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            } else if (idxPdRegist >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdRegist].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdRegist].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdRegist].municipalId,
                                    type: cekProgressProcessDetail[idxPdRegist].type,
                                    status: cekProgressProcessDetail[idxPdRegist].status,
                                    progress: percentROrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }
                let percentProgress = (totalAllRegist === 0) ? 0 : (totalAllRPercent/(Object.keys(unregisteredUsers).length * 100)) * 100;
                if (!Object.keys(unregisteredUsers).length) percentProgress = 100;
                if (cekProgressProcess[idxProgressUnregist].progress != percentProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressUnregist].id,
                        municipalId: cekProgressProcess[idxProgressUnregist].municipalId,
                        type: cekProgressProcess[idxProgressUnregist].type,
                        userId: cekProgressProcess[idxProgressUnregist].userId,
                        status: cekProgressProcess[idxProgressUnregist].status,
                        importStatus: cekProgressProcess[idxProgressUnregist].importStatus,
                        progress: percentProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
            if (cekProgressProcess[idxProgressAdmTea] && cekProgressProcess[idxProgressAdmTea].id && cekProgressProcess[idxProgressAdmTea].importStatus === 1) {
                let totalAllATRegist = 0;
                let totalAllATPercent = 0;
                if (Object.keys(adminTeacherUsers).length) {
                    for (let key in adminTeacherUsers) {
                        totalAllATRegist = totalAllATRegist + adminTeacherUsers[key].registered;
                        const percentATOrgs = adminTeacherUsers[key].registered < 1 ? 0 : (adminTeacherUsers[key].registered/adminTeacherUsers[key].total)*100;
                        totalAllATPercent += percentATOrgs;

                        if (key) {
                            let idxPdAdminT = -1;
                            if (cekProgressProcessDetail.length > 0) { 
                                idxPdAdminT = cekProgressProcessDetail.findIndex((item) => item.type === ADMIN_TEACHER_COLLATION && item.orgSourcedId === key);
                            }
                            if (idxPdAdminT < 0) {
                                insTaskProgressDetail.push({
                                    id: `${cekProgressProcess[idxProgressAdmTea].municipalId}_${key}_${ADMIN_TEACHER_COLLATION}`,
                                    importTaskProgressId: cekProgressProcess[idxProgressAdmTea].id,
                                    municipalId: cekProgressProcess[idxProgressAdmTea].municipalId,
                                    type: ADMIN_TEACHER_COLLATION, 
                                    status: STATUS_COMPLETED,
                                    progress: percentATOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            } else if (idxPdAdminT >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdAdminT].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdAdminT].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdAdminT].municipalId,
                                    type: cekProgressProcessDetail[idxPdAdminT].type,
                                    status: cekProgressProcessDetail[idxPdAdminT].status,
                                    progress: percentATOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }
                let percentATProgress = (totalAllATRegist === 0) ? 0 : (totalAllATPercent/(Object.keys(adminTeacherUsers).length * 100)) * 100;
                if (!Object.keys(adminTeacherUsers).length) percentATProgress = 100;
                if (cekProgressProcess[idxProgressAdmTea].progress != percentATProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressAdmTea].id,
                        municipalId: cekProgressProcess[idxProgressAdmTea].municipalId,
                        type: cekProgressProcess[idxProgressAdmTea].type,
                        userId: cekProgressProcess[idxProgressAdmTea].userId,
                        status: cekProgressProcess[idxProgressAdmTea].status,
                        importStatus: cekProgressProcess[idxProgressAdmTea].importStatus,
                        progress: percentATProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
            if (cekProgressProcess[idxProgressStudent] && cekProgressProcess[idxProgressStudent].id && cekProgressProcess[idxProgressStudent].importStatus === 1) {
                let totalAllSRegist = 0;
                let totalAllSPercent = 0;
                if (Object.keys(studentUsers).length) {
                    for (let key in studentUsers) {
                        totalAllSRegist = totalAllSRegist + studentUsers[key].registered;

                        const percentASOrgs = studentUsers[key].registered < 1 ? 0 : (studentUsers[key].registered/studentUsers[key].total)*100;
                        totalAllSPercent += percentASOrgs;

                        if (key) {
                            let idxPdStudent = -1;
                            if (cekProgressProcessDetail.length > 0) { 
                                idxPdStudent = cekProgressProcessDetail.findIndex((item) => item.type === STUDENT_COLLATION && item.orgSourcedId === key);
                            }
                            if (idxPdStudent < 0) {
                                insTaskProgressDetail.push({
                                    id: `${cekProgressProcess[idxProgressStudent].municipalId}_${key}_${STUDENT_COLLATION}`,
                                    importTaskProgressId: cekProgressProcess[idxProgressStudent].id,
                                    municipalId: cekProgressProcess[idxProgressStudent].municipalId,
                                    type: STUDENT_COLLATION, 
                                    status: STATUS_COMPLETED,
                                    progress: percentASOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            } else if (idxPdStudent >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdStudent].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdStudent].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdStudent].municipalId,
                                    type: cekProgressProcessDetail[idxPdStudent].type,
                                    status: cekProgressProcessDetail[idxPdStudent].status,
                                    progress: percentASOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }
                let percentSProgress = (totalAllSRegist === 0) ? 0 : (totalAllSPercent / (Object.keys(studentUsers).length * 100)) * 100;
                if (!Object.keys(studentUsers).length) percentSProgress = 100;
                if (cekProgressProcess[idxProgressStudent].progress != percentSProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressStudent].id,
                        municipalId: cekProgressProcess[idxProgressStudent].municipalId,
                        type: cekProgressProcess[idxProgressStudent].type,
                        userId: cekProgressProcess[idxProgressStudent].userId,
                        status: cekProgressProcess[idxProgressStudent].status,
                        importStatus: cekProgressProcess[idxProgressStudent].importStatus,
                        progress: percentSProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
            if (cekProgressProcess[idxProgressAdmin] && cekProgressProcess[idxProgressAdmin].id && cekProgressProcess[idxProgressAdmin].importStatus === 1) {
                let totalAllARegist = 0;
                let totalAllAPercent = 0;
                if (Object.keys(adminUsers).length) {
                    for (let key in adminUsers) {
                        totalAllARegist = totalAllARegist + adminUsers[key].registered;
                        const percentAOrgs = adminUsers[key].registered < 1 ? 0 : (adminUsers[key].registered/adminUsers[key].total)*100;
                        totalAllAPercent += percentAOrgs;
                        
                        if (key) {
                            let idxPdAdmin = -1;
                            if (cekProgressProcessDetail.length > 0) { 
                                idxPdAdmin = cekProgressProcessDetail.findIndex((item) => item.type === ADMINISTRATOR_COLLATION && item.orgSourcedId === key);
                            }
                            if (idxPdAdmin < 0) {
                                insTaskProgressDetail.push({
                                    id: `${cekProgressProcess[idxProgressAdmin].municipalId}_${key}_${ADMINISTRATOR_COLLATION}`,
                                    importTaskProgressId: cekProgressProcess[idxProgressAdmin].id,
                                    municipalId: cekProgressProcess[idxProgressAdmin].municipalId,
                                    type: ADMINISTRATOR_COLLATION, 
                                    status: STATUS_COMPLETED,
                                    progress: percentAOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            } else if (idxPdAdmin >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdAdmin].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdAdmin].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdAdmin].municipalId,
                                    type: cekProgressProcessDetail[idxPdAdmin].type,
                                    status: cekProgressProcessDetail[idxPdAdmin].status,
                                    progress: percentAOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }

                let percentAProgress = (totalAllARegist === 0) ? 0 : (totalAllAPercent/(Object.keys(adminUsers).length * 100)) * 100;
                if (!Object.keys(adminUsers).length) percentAProgress = 100;
                if (cekProgressProcess[idxProgressAdmin].progress != percentAProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressAdmin].id,
                        municipalId: cekProgressProcess[idxProgressAdmin].municipalId,
                        type: cekProgressProcess[idxProgressAdmin].type,
                        userId: cekProgressProcess[idxProgressAdmin].userId,
                        status: cekProgressProcess[idxProgressAdmin].status,
                        importStatus: cekProgressProcess[idxProgressAdmin].importStatus,
                        progress: percentAProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
            if (cekProgressProcess[idxProgressEnrolClass] && cekProgressProcess[idxProgressEnrolClass].id && cekProgressProcess[idxProgressEnrolClass].importStatus === 1) {
                let totalAllECClass = 0;
                let totalAllECRegist = 0;
                let totalAllECPercent = 0;
                if (Object.keys(enrollClassUsers).length) {
                    for (let key in enrollClassUsers) {
                        const totalECOrgsClass = Object.keys(enrollClassUsers[key]).length;
                        totalAllECClass += totalECOrgsClass;
                        let totalPercentECOrgs = 0;
                        for (let subkey in enrollClassUsers[key]) {
                            totalAllECRegist += enrollClassUsers[key][subkey].registered;
                            const percentECOrgs = enrollClassUsers[key][subkey].registered < 1 ? 0 : (enrollClassUsers[key][subkey].registered/enrollClassUsers[key][subkey].total)*100;
                            totalPercentECOrgs += percentECOrgs;
                            totalAllECPercent += percentECOrgs;
                        }
                        const percentECOrgs = (totalPercentECOrgs / (totalECOrgsClass*100)) * 100
                        if (key && cekProgressProcessDetail.length > 0) { 
                            const idxPdEC = cekProgressProcessDetail.findIndex((item) => item.type === CLASS_ATENDANCE_COLLATION && item.orgSourcedId === key && !item.classSourceId);

                            if (idxPdEC >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdEC].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdEC].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdEC].municipalId,
                                    type: cekProgressProcessDetail[idxPdEC].type,
                                    status: cekProgressProcessDetail[idxPdEC].status,
                                    progress: percentECOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }
                let percentECProgress = (totalAllECRegist === 0) ? 0 : (totalAllECPercent/(totalAllECClass*100)) * 100;
                if (!Object.keys(enrollClassUsers).length) percentECProgress = 100;
                if (cekProgressProcess[idxProgressEnrolClass].progress != percentECProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressEnrolClass].id,
                        municipalId: cekProgressProcess[idxProgressEnrolClass].municipalId,
                        type: cekProgressProcess[idxProgressEnrolClass].type,
                        userId: cekProgressProcess[idxProgressEnrolClass].userId,
                        status: cekProgressProcess[idxProgressEnrolClass].status,
                        importStatus: cekProgressProcess[idxProgressEnrolClass].importStatus,
                        progress: percentECProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
            
            if (cekProgressProcess[idxProgressEnrolGroup] && cekProgressProcess[idxProgressEnrolGroup].id && cekProgressProcess[idxProgressEnrolGroup].importStatus === 1) {
                let totalAllEGClass = 0;
                let totalAllEGRegist = 0;
                let totalAllEGPercent = 0;
                if (Object.keys(enrollGroupUsers).length) {
                    for (let key in enrollGroupUsers) {
                        const totalEGOrgsClass = Object.keys(enrollGroupUsers[key]).length;
                        totalAllEGClass += totalEGOrgsClass;
                        let totalPercentEGOrgs = 0;
                        for (let subkey in enrollGroupUsers[key]) {
                            totalAllEGRegist += enrollGroupUsers[key][subkey].registered;
                            const percentEGOrgs = enrollGroupUsers[key][subkey].registered < 1 ? 0 : (enrollClassUsers[key][subkey].registered/enrollClassUsers[key][subkey].total)*100;
                            totalPercentEGOrgs += percentEGOrgs;
                            totalAllEGPercent += percentEGOrgs;
                        }
                        const percentEGOrgs = (totalPercentEGOrgs / (totalEGOrgsClass*100)) * 100
                        if (key && cekProgressProcessDetail.length > 0) { 
                            const idxPdEG = cekProgressProcessDetail.findIndex((item) => item.type === OTHER_ATENDANCE_COLLATION && item.orgSourcedId === key && !item.classSourceId);

                            if (idxPdEG >= 0) {
                                insTaskProgressDetail.push ({
                                    id: cekProgressProcessDetail[idxPdEG].id,
                                    importTaskProgressId: cekProgressProcessDetail[idxPdEG].importTaskProgressId,
                                    municipalId: cekProgressProcessDetail[idxPdEG].municipalId,
                                    type: cekProgressProcessDetail[idxPdEG].type,
                                    status: cekProgressProcessDetail[idxPdEG].status,
                                    progress: percentEGOrgs,
                                    lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                                    orgSourcedId:key
                                });
                            }
                        }
                    }
                }
                let percentEGProgress = (totalAllEGRegist === 0) ? 0 : (totalAllEGPercent/(totalAllEGClass*100)) * 100;
                if (!Object.keys(enrollGroupUsers).length) percentEGProgress = 100;
                if (cekProgressProcess[idxProgressEnrolGroup].progress != percentEGProgress) {
                    progressChange.push({
                        id: cekProgressProcess[idxProgressEnrolGroup].id,
                        municipalId: cekProgressProcess[idxProgressEnrolGroup].municipalId,
                        type: cekProgressProcess[idxProgressEnrolGroup].type,
                        userId: cekProgressProcess[idxProgressEnrolGroup].userId,
                        status: cekProgressProcess[idxProgressEnrolGroup].status,
                        importStatus: cekProgressProcess[idxProgressEnrolGroup].importStatus,
                        progress: percentEGProgress,
                        lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss")
                    });
                }
            }
        }
        if (progressChange.length) {
            await db[municipalId].importTaskProgress.bulkCreate(progressChange, { updateOnDuplicate: ["progress","lastUpdated"] });
        }
        if (insTaskProgressDetail.length) {
            await db[municipalId].importTaskProgressDetail.bulkCreate(insTaskProgressDetail, { updateOnDuplicate: ["progress","lastUpdated"] });
        }

        let insetData = JSON.parse(JSON.stringify(queryMerged))
        return await db[municipalId].importUsers.bulkCreate( insetData, { updateOnDuplicate: ["role","userIdLgate","userLgateName","userLgatePassword","option","isDelta","isParentSkiped"] } )
    } else {
        return true;
    }
}

/**
 * Process to update field 'status' becomes 'tobedeleted' on courses and enrollments table
 * @constructor
 */
const tobedeletedChild = async (class_ids, municipalId) => {
    await Promise.all(
        class_ids.map( async (class_id) => {
            await db[municipalId].courses.update({
            status : 'tobedeleted',
            dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
            },{
            where : {
                classesId : class_id
            }
            })

            await db[municipalId].enrollments.update({
            status : 'tobedeleted',
            isToBeDeleted: true, 
            dateLastModified: `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
            },{
            where : {
                classSourcedId : class_id
            }
            })
        })
    )
}

const attr = [
    "id",
    "sourcedId",
    "uuid",
    "status",
    "dateLastModified",
    "title",
    "grades",
    "courseSourcedId",
    "classCode",
    "classType",
    "location",
    "schoolSourcedId",
    "termSourcedIds",
    "subjects",
    "subjectCodes",
    "periods",
    "municipalId",
    "yearId",
    "metadataJpSpecialNeeds"
  ];

let step = ['import_table_update','update_tobedeleted','count_all_data_import','import_merge_data']
// let step = ['count_all_data_import','import_table_update','import_merge_data']

/**
 * Processing bull job for submited data from classes import process
 * @constructor
 */
class SubmitClasses {
    onProcess = async (job,done,initData = null,stepIndex=0, limit=100, offset=0) => {
        const param = job.data

        if(!initData){
            initData = {
                bulkDeleteCsv : [],
                bulkCourseDeleteCsv : [],
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
        let bulkCourseDeleteCsv = [];
        let data;
        let dataCourse;
        let lgateSubmit = [];
        let importSubmited = [];
        let rowstart = 0;
        let rowend = 0;

        switch(step[stepIndex]){
            case 'import_table_update': 
                initData.startInsertTime = moment()
            
                let importData = param.data
                const importUpdateData = importData.map((item) => {
                  let data = JSON.parse(JSON.stringify(item));
                  
                  if (data.option == "skip_csv_to_lgate" && data.option_init === "add_from_lgate") {
                    data = JSON.parse(JSON.stringify({ ...item, ...item.lgate_data }));
                    data.option = "delete_add_from_lgate";
                  }
                  data.submited = 0
                  data.isDelta = 0
                  return data;
                });

                let attrImport = [];
                for (let key in importUpdateData[0]) {
                    attrImport.push(key);
                }

                let exclude = ["courseSourcedId","schoolSourcedId","termSourcedIds"]
                let attrUpdate = await excludeArrayValue(exclude,attrImport)
                await db[param.municipalId].importClasses.bulkCreate(importUpdateData, { updateOnDuplicate: attrUpdate }).then((item) => {
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                })  

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.csv_import_data_updated'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});

                ++stepIndex
            break;

            case 'import_merge_data':
                initData.startInsertTime = moment()
                let filter = param?.schoolSourcedId ? ` AND (rel_orgs.rosterSourcedId = '${param?.schoolSourcedId}' OR rel_orgs.importSourcedId = '${param?.schoolSourcedId}') ` : ``;

                const query = `
                    SELECT
                        import_classes.*,
                        import_courses.sourcedId AS'import_courses.sourcedId', 
                        import_courses.status AS'import_courses.status', 
                        import_courses.dateLastModified AS'import_courses.dateLastModified', 
                        import_courses.schoolYearSourcedId AS'import_courses.schoolYearSourcedId', 
                        import_courses.title AS'import_courses.title', 
                        import_courses.courseCode AS'import_courses.courseCode', 
                        import_courses.grades AS'import_courses.grades', 
                        import_courses.orgSourcedId AS'import_courses.orgSourcedId', 
                        import_courses.subjects AS'import_courses.subjects', 
                        import_courses.subjectCodes AS'import_courses.subjectCodes',
                        rel_orgs.rosterSourcedId AS 'orgs.sourcedId',
                        orgs.name AS 'orgs.name',
                        rel_academic_sessions.rosterSourcedId AS 'academic_sessions.sourcedId',
                        academic_sessions.title AS 'academic_sessions.itle',
                        classes.id AS 'classes.id',
                        classes.sourcedId AS 'classes.sourcedId',
                        classes.uuid AS 'classes.uuid',
                        classes.status AS 'classes.status',
                        classes.dateLastModified AS 'classes.dateLastModified',
                        courses.id AS 'courses.id',
                        courses.sourcedId AS 'courses.sourcedId',
                        courses.uuid AS 'courses.uuid',
                        courses.status AS 'courses.status',
                        courses.dateLastModified AS 'courses.dateLastModified'
                    FROM
                        import_classes
                    LEFT JOIN import_courses ON import_classes.courseSourcedId = import_courses.sourcedId
                    INNER JOIN rel_orgs ON import_classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
                    INNER JOIN rel_academic_sessions ON import_classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                    INNER JOIN academic_sessions ON rel_academic_sessions.rosterSourcedId = academic_sessions.sourcedId
                    LEFT JOIN orgs ON rel_orgs.rosterSourcedId = orgs.sourcedId
                    LEFT JOIN classes ON import_classes.classesIdLgate = classes.sourcedId 
                    LEFT JOIN courses ON classes.courseSourcedId = courses.sourcedId 
                    WHERE
                        import_classes.classType = 'homeroom'
                        AND import_classes.submited = 0
                        AND import_classes.isParentSkiped = 0
                        AND import_classes.municipalId = '${param.municipalId}'
                        ${filter}
                        LIMIT ${limit}
                `;
                
                const queryResult = await db[param.municipalId].query(query).then((item) => {
                    return item[0]
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 

                if(queryResult.length){
                    let queryResultMap = await mappingQueryArrayReturn(queryResult)
                    let importCsvData = [];
                    let importDataCourses = [];
                    let lgateData = [];
                    let lgateDataCourse = [];
                    let insertRel = [];
                    let insertRelCourses = [];
                    let lgateSubmit = [];
                    let tobedeletedSourcedId = [];
                    
                    await Promise.all(queryResultMap.map(async (item)=> {
                        importCsvData.push({
                            sourcedId : item.sourcedId,
                            status : item.status,
                            dateLastModified : item.dateLastModified,
                            title : item.title,
                            grades : item.grades,
                            courseSourcedId : item.courseSourcedId,
                            classCode : item.classCode,
                            classType : item.classType,
                            location : item.location,
                            schoolSourcedId : item.schoolSourcedId,
                            termSourcedIds : item.termSourcedIds,
                            subjects : item.subjects,
                            subjectCodes : item.subjectCodes,
                            periods : item.periods,
                            metadataJpSpecialNeeds : item.metadataJpSpecialNeeds,
                            municipalId : param.municipalId,
                            classesIdLgate : item.classesIdLgate,
                            classLgateName : item.classLgateName,
                            option : item.option,
                            submited : item.submited,
                            academic_session : {title : item.academic_sessions[0].title, sourcedId : item.academic_sessions[0].sourcedId},
                            org : {name : item.orgs[0].name, sourcedId : item.orgs[0].sourcedId}
                        })

                        if(item.classes?.length){
                            lgateData.push({
                                id : item.classes[0].id,
                                sourcedId : item.classes[0].sourcedId,
                                uuid : item.classes[0].uuid,
                                status : item.classes[0].status,
                                dateLastModified : item.classes[0].dateLastModified,
                                title : item.title,
                                grades : item.grades,
                                courseSourcedId : item.courseSourcedId,
                                classCode : item.classCode,
                                classType : item.classType,
                                location : item.location,
                                schoolSourcedId : item.orgs[0].sourcedId,
                                termSourcedIds : item.academic_sessions[0].sourcedId,
                                subjects : item.subjects,
                                subjectCodes : item.subjectCodes,
                                periods : item.periods,
                                municipalId : param.municipalId,
                                yearId : item.academic_sessions[0].sourcedId,
                                toBeDeleted : 0
                            })
                        }

                        if(item.courses?.length){
                            lgateDataCourse.push({
                                id : item.courses[0].id,
                                sourcedId : item.courses[0].sourcedId,
                                uuid : item.courses[0].uuid,
                                status : item.courses[0].status,
                                dateLastModified : item.courses[0].dateLastModified,
                                schoolYearSourcedId : item.courses[0].schoolYearSourcedId,
                                title : item.title,
                                courseCode : item.courseCode,
                                grade : item.grade,
                                orgSourcedId : item.orgs[0].sourcedId,
                                subjects : item.subjects,
                                subjectCodes : item.subjectCodes,
                                municipalId : param.municipalId,
                                yearId : item.academic_sessions[0].sourcedId,
                                classId : item.classes[0].sourcedId,
                                toBeDeleted : 0,
                            })
                        }
                        
                        await Promise.all(item.import_courses.map(async (item_courses,index_courses) => {
                            if (item_courses.sourcedId != null) {
                                importDataCourses.push({
                                    sourcedId : item_courses.sourcedId,
                                    status : item_courses.status,
                                    dateLastModified : item_courses.dateLastModified,
                                    schoolYearSourcedId : item_courses.schoolYearSourcedId,
                                    title : item_courses.title,
                                    courseCode : item_courses.courseCode,
                                    grades : item_courses.grades,
                                    orgSourcedId : item_courses.orgSourcedId,
                                    subjects : item_courses.subjects,
                                    subjectCodes : item_courses.subjectCodes,
                                    municipalId : item_courses.municipalId,
                                    classesId : item.sourcedId,
                                    municipalId : param.municipalId,
                                    submited : item_courses.submited,
                                    yearId : item.academic_sessions[0].sourcedId,
                                })
                            }
                        }))
                    }))
                    
                    await Promise.all(
                        importDataCourses.map(async (item) => {
                            let importClassIndex = importCsvData.findIndex((row) => item.classesId === row.sourcedId && item.sourcedId === row.courseSourcedId);
                            if (importClassIndex >= 0) {
                                let dataClasses = importCsvData[importClassIndex];
                                if (dataClasses.option == 'add_from_lgate' || dataClasses.option == 'update_csv_to_lgate') {
                                    let lgateCourseIndex = lgateDataCourse.findIndex((row) => dataClasses.classesIdLgate === row.classId);
                                    if (lgateCourseIndex >= 0) {
                                        dataCourse = lgateDataCourse[lgateCourseIndex];
                                        let lgateCIndex = lgateData.findIndex((row) => dataClasses.classesIdLgate === row.sourcedId);
                                        let dataClassCourse = lgateData[lgateCIndex];
                                        let returnedTarget = Object.assign(JSON.parse(JSON.stringify(dataCourse)), JSON.parse(JSON.stringify(item)));
                                        returnedTarget.status = item.status ? item.status : dataCourse.status;
    
                                        if(item.dateLastModified) {
                                            returnedTarget.dateLastModified =  item.dateLastModified
                                        } else {
                                            returnedTarget.dateLastModified = `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
                                        } 
    
                                        returnedTarget.isToBeDeleted = 0
    
                                        returnedTarget.sourcedId= dataCourse.sourcedId
                                        returnedTarget.classesId= dataCourse.classesId
                                        returnedTarget.orgSourcedId= dataCourse.orgSourcedId
                                        returnedTarget.schoolYearSourcedId= dataCourse.schoolYearSourcedId || dataClassCourse.termSourcedIds
                                        if(item.isDelta && returnedTarget.status == 'tobedeleted'){
                                          tobedeletedSourcedId.push(returnedTarget.sourcedId)
                                          returnedTarget.isToBeDeleted = true
                                        }
    
                                        const relDataCourses = await db[param.municipalId].relCourses.findAll({
                                          where: {
                                            rosterSourcedId: returnedTarget.sourcedId,
                                            importSourcedId: item.sourcedId,
                                          },
                                        }).then((item) => {
                                            return item
                                        }).catch((err) => {
                                            let validationError = JSON.parse(JSON.stringify(err))?.original
                                            return done({message : validationError?.sqlMessage})
                                        }) ;
    
                                        if (relDataCourses.length == 0) {
                                            insertRelCourses.push({
                                                rosterSourcedId : returnedTarget.sourcedId,
                                                rosterSchoolYearSourcedId : returnedTarget.schoolYearSourcedId,
                                                rosterOrgSourcedId : returnedTarget.orgSourcedId,
                                                importSourcedId : item.sourcedId,
                                                importSchoolYearSourcedId : item.SchoolYearSourcedId || dataClasses.termSourcedIds,
                                                importOrgSourcedId : item.orgSourcedId,
                                                municipalId: item.municipalId,
                                                isTemp: 1,
                                            });
                                        }
                                    }
                                } else if (dataClasses.option == 'add_csv_to_lgate') {    
                                    const relDataCourses = await db[param.municipalId].relCourses.findAll({
                                      where: {
                                        rosterSourcedId: item.sourcedId,
                                        importSourcedId: item.sourcedId,
                                      },
                                    }).then((item) => {
                                        return item
                                    }).catch((err) => {
                                        let validationError = JSON.parse(JSON.stringify(err))?.original
                                        return done({message : validationError?.sqlMessage})
                                    });

                                    if (relDataCourses.length == 0) {
                                      insertRelCourses.push({
                                        rosterSourcedId : item.sourcedId,
                                        rosterSchoolYearSourcedId : item.schoolYearSourcedId || dataClasses.termSourcedIds,
                                        rosterOrgSourcedId : item.orgSourcedId,
                                        importSourcedId : item.sourcedId,
                                        importSchoolYearSourcedId : item.SchoolYearSourcedId || dataClasses.termSourcedIds,
                                        importOrgSourcedId : item.orgSourcedId,
                                        municipalId: item.municipalId,
                                        isTemp: 1,
                                      });
                                    }
                                } else if (dataClasses.option == 'skip_csv_to_lgate' || dataClasses.option == 'delete_add_from_lgate') {
                                    bulkCourseDeleteCsv.push(item.sourcedId);
                                }
                            }
                        })
                    )
                    
                    await Promise.all(
                        importCsvData.map(async (item) => {
                            item.submited = 1;
                            if (item.option !== 'delete_add_from_lgate') {
                                importSubmited.push(JSON.parse(JSON.stringify(item)));
                            }

                            if (item.option == 'add_from_lgate' || item.option == 'update_csv_to_lgate') {
                                let lgateIndex = lgateData.findIndex((row) => item.classesIdLgate === row.sourcedId);
                                if (lgateIndex >= 0) {
                                    data = lgateData[lgateIndex];
                                    let returnedTarget = Object.assign(JSON.parse(JSON.stringify(data)), JSON.parse(JSON.stringify(item)));
                                    returnedTarget.status = item.status ? item.status : data.status;

                                    if(item.dateLastModified) {
                                        returnedTarget.dateLastModified =  item.dateLastModified
                                    } else {
                                        returnedTarget.dateLastModified = `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`
                                    } 

                                    returnedTarget.isToBeDeleted = 0

                                    returnedTarget.sourcedId= data.sourcedId
                                    returnedTarget.courseSourcedId= data.courseSourcedId
                                    returnedTarget.schoolSourcedId= data.schoolSourcedId
                                    returnedTarget.termSourcedIds= data.termSourcedIds
                                    if(item.isDelta && returnedTarget.status == 'tobedeleted'){
                                      tobedeletedSourcedId.push(returnedTarget.sourcedId)
                                      returnedTarget.isToBeDeleted = true
                                    }

                                    let submitSetting = JSON.parse(param.submitSetting);
                                    if (submitSetting.length > 0) {
                                      for (var i = 0; i < submitSetting.length; i++) {
                                        switch(submitSetting[i]){
                                          case SS_CLASS_NAME:
                                            returnedTarget.name = data.name;
                                          break;
                                        }
                                      }
                                    }

                                    let grades = item.grades.split(',');
                                    if (config.IMPORT_TO_LGATE) {
                                        lgateSubmit.push({
                                            term_uuid : returnedTarget.termSourcedIds,
                                            grade_code : !item.grades || grades.length>1 ? 'zz' : item.grades,
                                            name : item.title,
                                            organization_uuid : returnedTarget.schoolSourcedId,
                                            option : 'update',
                                            municipalId : item.municipalId,
                                            classType : item.classType,
                                            oldSourcedId : returnedTarget.sourcedId

                                        });
                                    }

                                    const relData = await db[param.municipalId].relClasses.findAll({
                                      where: {
                                        rosterSourcedId: returnedTarget.sourcedId,
                                        importSourcedId: item.sourcedId,
                                      },
                                    }).then((item) => {
                                        return item
                                    }).catch((err) => {
                                        let validationError = JSON.parse(JSON.stringify(err))?.original
                                        return done({message : validationError?.sqlMessage})
                                    }) ;

                                    if (relData.length == 0) {
                                        insertRel.push({
                                            rosterSourcedId : returnedTarget.sourcedId,
                                            rosterCourseSourcedId : returnedTarget.courseSourcedId,
                                            rosterSchoolSourcedId : returnedTarget.schoolSourcedId,
                                            rosterTermSourcedIds : returnedTarget.termSourcedIds,
                                            importSourcedId : item.sourcedId,
                                            importCourseSourcedId : item.courseSourcedId,
                                            importSchoolSourcedId : item.schoolSourcedId,
                                            importTermSourcedIds : item.termSourcedIds,
                                            municipalId: item.municipalId,
                                            isTemp: 1,
                                        });
                                    }
                                }
                            } else if (item.option == 'add_csv_to_lgate') {
                                let grades = item.grades.split(',');
                                if (config.IMPORT_TO_LGATE) {
                                    lgateSubmit.push({
                                        term_uuid : item.academic_session.sourcedId,
                                        grade_code : !item.grades || grades.length>1 ? 'zz' : item.grades,
                                        name : item.title,
                                        organization_uuid : item.org.sourcedId,
                                        option : 'insert',
                                        municipalId : item.municipalId,
                                        classType : item.classType,
                                        oldSourcedId : item.sourcedId

                                    });
                                }

                                const relData = await db[param.municipalId].relClasses.findAll({
                                  where: {
                                    rosterSourcedId: item.sourcedId,
                                    importSourcedId: item.sourcedId,
                                  },
                                }).then((item) => {
                                    return item
                                }).catch((err) => {
                                    let validationError = JSON.parse(JSON.stringify(err))?.original
                                    return done({message : validationError?.sqlMessage})
                                }) ;
                                if (relData.length == 0) {
                                  insertRel.push({
                                    rosterSourcedId : item.sourcedId,
                                    rosterCourseSourcedId : item.courseSourcedId,
                                    rosterSchoolSourcedId : item.org.sourcedId,
                                    rosterTermSourcedIds : item.academic_session.sourcedId,
                                    importSourcedId : item.sourcedId,
                                    importCourseSourcedId : item.courseSourcedId,
                                    importSchoolSourcedId : item.schoolSourcedId,
                                    importTermSourcedIds : item.termSourcedIds,
                                    municipalId: item.municipalId,
                                    isTemp: 1,
                                  });
                                }
                            } else if (item.option == 'skip_csv_to_lgate' || item.option == 'delete_add_from_lgate') {
                                bulkDeleteCsv.push(item.sourcedId);
                            }
                        })
                    );

                    Array.prototype.push.apply(initData.bulkDeleteCsv,bulkDeleteCsv);  
                    Array.prototype.push.apply(initData.bulkCourseDeleteCsv,bulkCourseDeleteCsv);  
                    
                    if(insertRel.length){
                        await db[param.municipalId].relClasses.bulkCreate(insertRel).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;
                    }
                    
                    if(insertRelCourses.length){
                        await db[param.municipalId].relCourses.bulkCreate(insertRelCourses).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;
                    }
                
                    if (bulkDeleteCsv.length) {
                        await db[param.municipalId].importClasses.destroy({
                            where: {
                            sourcedId: { [Op.in]: bulkDeleteCsv },
                            },
                        }).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) ;

                        await db[param.municipalId].lgateClasses.destroy({
                            where: {
                                oldSourcedId: { [Op.in]: bulkDeleteCsv },
                            },
                        })
                        
                        await db[param.municipalId].relClasses.destroy({
                          where: {
                            importSourcedId: { [Op.in]: bulkDeleteCsv },
                            isTemp: 1
                          },
                        })

                        if (bulkCourseDeleteCsv.length) {
                            await db[param.municipalId].relCourses.destroy({
                                where: {
                                    importSourcedId: { [Op.in]: bulkCourseDeleteCsv },
                                },
                            })
                        }
                    }

                    if(lgateSubmit.length){
                        await db[param.municipalId].lgateClasses.bulkCreate(lgateSubmit).then((item) => {
                        }).catch((err) => {
                            let validationError = JSON.parse(JSON.stringify(err))?.original
                            return done({message : validationError?.sqlMessage})
                        }) 
                    }
                    
                    let attrImportSubmited = [];
                    if (importSubmited.length) {
                    for (let key in importSubmited[0]) {
                        attrImportSubmited.push(key);
                    }
                    let exclude = ["courseSourcedId","schoolSourcedId","termSourcedIds"]
                    let attrUpdate = await excludeArrayValue(exclude,attrImportSubmited)
                    importSubmited = await convertDateForInsert(importSubmited,'dateLastModified');

                    await db[param.municipalId].importClasses.bulkCreate(importSubmited, { updateOnDuplicate: attrUpdate }).then((item) => {
                    }).catch((err) => {
                        let validationError = JSON.parse(JSON.stringify(err))?.original
                        return done({message : validationError?.sqlMessage})
                    }) ;
                    }
                    
                    if (bulkDeleteCsv.length) {
                        await deleteUsersImport(param.municipalId);
                    }

                    let filter = param?.schoolSourcedId ? ` AND (rel_orgs.rosterSourcedId = '${param?.schoolSourcedId}' OR rel_orgs.importSourcedId = '${param?.schoolSourcedId}') ` : ``;
                    const queryImportCsvDataSubmited = `
                        SELECT 
                            import_classes.sourcedId
                        FROM 
                            import_classes
                            INNER JOIN rel_academic_sessions ON import_classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                            INNER JOIN rel_orgs ON import_classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
                        WHERE 
                            import_classes.classType = 'homeroom'
                            AND import_classes.municipalId = '${param.municipalId}'
                            AND import_classes.submited = 1
                            AND import_classes.option != 'skip_csv_to_lgate'
                            AND import_classes.option != 'delete_add_from_lgate'
                            ${filter}
                    `;
                    const resultImportCsvDataSubmited = await db[param.municipalId].query(queryImportCsvDataSubmited).then((item) => {
                        return item[0]
                    }).catch((err) => {
                        let validationError = JSON.parse(JSON.stringify(err))?.original
                        return done({message : validationError?.sqlMessage})
                    }) 
                    initData.progress = resultImportCsvDataSubmited.length
                    await job.progress({total_row:initData.importCsvDataAll,progress_row:initData.progress,is_calculating:true})
                    
                    rowstart = ((offset*limit)+1)
                    rowend = ((offset+1)*limit)
                    rowend = initData.importCsvDataAll < rowend ? initData.importCsvDataAll : rowend
                    
                    initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                    initData.logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.csv_data_merged_process').replace('%ROW_START%',rowstart).replace('%ROW_END%',rowend), executionTime : initData.insertTime}
                    LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});

                } else {
                    ++stepIndex
                    offset = 0
                }
            break;
            
            case 'update_tobedeleted': 
                initData.startInsertTime = moment()
                
                let bulkTobeDeleted = [];
                let lgateSubmit = [];

                let filterTobeDeleted = '';
                if (param.schoolSourcedId) filterTobeDeleted += ` AND (rel_orgs.rosterSourcedId = '${param?.schoolSourcedId}' OR rel_orgs.importSourcedId = '${param?.schoolSourcedId}') `;
            
                const queryTobeDeleted = `
                    SELECT
                        classes.* 
                    FROM
                        classes
                        INNER JOIN rel_orgs ON classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
                        INNER JOIN rel_academic_sessions ON classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                        LEFT JOIN import_classes ON import_classes.classesIdLgate = classes.sourcedId
                    WHERE
                        import_classes.sourcedId IS NULL
                        AND classes.status = 'active'
                        AND classes.classType = 'homeroom'
                        AND classes.municipalId = '${param.municipalId}'
                        ${filterTobeDeleted}
                `;
                
                const tobedeletedData = await db[param.municipalId].query(queryTobeDeleted).then((item) => {
                    return item[0]
                }).catch((err) => {
                    console.log(err)
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 
            
                await Promise.all(
                    tobedeletedData.map(async (item) => {
                      bulkTobeDeleted.push(item.id);

                      if (config.IMPORT_TO_LGATE) {
                            // lgateSubmit.push({
                            //     term_uuid : item.termSourcedIds,
                            //     grade_code : item.grades,
                            //     name : item.title,
                            //     organization_uuid : item.schoolSourcedId,
                            //     option : 'delete',
                            //     municipalId : item.municipalId,
                            //     oldSourcedId : item.sourcedId

                            // });
                        }
                    })
                  );
              
                  if (bulkTobeDeleted.length) {
                    await db[param.municipalId].classes.update(
                      {isToBeDeleted: 1, dateLastModified : `${moment.utc().format("YYYY-MM-DD HH:mm:ss.SSS")}`},
                      { where: { id: { [Op.in]: bulkTobeDeleted } } 
                    }).then((item) => {
                    }).catch((err) => {
                        let validationError = JSON.parse(JSON.stringify(err))?.original
                        return done({message : validationError?.sqlMessage})
                    }) ;
                  }

                  if(lgateSubmit.length){
                    await db[param.municipalId].lgateClasses.bulkCreate(lgateSubmit).then((item) => {
                    }).catch((err) => {
                        let validationError = JSON.parse(JSON.stringify(err))?.original
                        return done({message : validationError?.sqlMessage})
                    }) 
                  }
                
                ++stepIndex

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.roster_data_status_tobedeleted'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
                
            break;
            
            case 'count_all_data_import' :
                initData.startInsertTime = moment()

                let filterAll = param?.schoolSourcedId ? ` AND (rel_orgs.rosterSourcedId = '${param?.schoolSourcedId}' OR rel_orgs.importSourcedId = '${param?.schoolSourcedId}') ` : ``;

                const queryImportCsvDataAll = `
                    SELECT 
                        import_classes.sourcedId
                    FROM 
                        import_classes
                        INNER JOIN rel_academic_sessions ON import_classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                        INNER JOIN rel_orgs ON import_classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
                    WHERE 
                        import_classes.classType = 'homeroom'
                        AND import_classes.municipalId = '${param.municipalId}'
                        AND import_classes.option != 'skip_csv_to_lgate'
                        AND import_classes.option != 'delete_add_from_lgate'
                        ${filterAll}
                `;
            
                const resultImportCsvDataAll = await db[param.municipalId].query(queryImportCsvDataAll).then((item) => {
                    return item[0]
                }).catch((err) => {
                    let validationError = JSON.parse(JSON.stringify(err))?.original
                    return done({message : validationError?.sqlMessage})
                }) 
                initData.importCsvDataAll = resultImportCsvDataAll.length
                if (initData.importCsvDataAll != initData.progress) {
                    initData.progress = initData.importCsvDataAll
                }
                await job.progress({total_row:initData.importCsvDataAll,progress_row:initData.progress,is_calculating:true})
                ++stepIndex

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.count_all_csv_import_data'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
            break;
            
            default:
                initData.startInsertTime = moment()
                await mergedUsers(param.municipalId,["teacher", "student","administrator"],"homeroom")

                initData.insertTime = moment().diff(initData.startInsertTime,"seconds",true)
                initData.logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.matching_csv_data'), executionTime : initData.insertTime}
                LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData:initData.logData});
                
                return done(null,initData.data)
        }
        await this.onProcess(job,done,initData,stepIndex,limit,offset);
    }

    onActive = async (job, jobPromise) => {
        let logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.submit_merged_start')}
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
        const importTaskProgressId = `${job.data.municipalId}_${CLASS_COLLATION}`

        // HANDLE IF HALFT DATA PER ORG PROGRESSBAR -- start
        if(job.data && job.data.schoolSourcedId){
            const queryOrg = `
                SELECT 
                    import_classes.sourcedId,
                    import_classes.submited
                FROM 
                    import_classes
                    INNER JOIN rel_academic_sessions ON import_classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                    INNER JOIN rel_orgs ON import_classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
                WHERE 
                    import_classes.classType = 'homeroom'
                    AND import_classes.option != 'skip_csv_to_lgate'
                    AND import_classes.option != 'delete_add_from_lgate'
                AND import_classes.schoolSourcedId = '${job.data.schoolSourcedId}' 
            `;
            const [result_org] = await db[job.data.municipalId].query(queryOrg)

            // IF BULK BASED ON ORG ID AND !SUPERADMIN
            resultOrgSubmited = result_org.filter((item)=>item.submited == 1)
            if (result_org.length && resultOrgSubmited.length) {
                percent = (resultOrgSubmited.length / result_org.length) * 100;
            } else {
                percent = 100;
            }

            await db[job.data.municipalId].importTaskProgressDetail.upsert({
                id: `${job.data.municipalId}_${job.data.schoolSourcedId}_${CLASS_COLLATION}`,
                importTaskProgressId: importTaskProgressId,
                municipalId: job.data.municipalId,
                type: CLASS_COLLATION, 
                status: percent == 100 ? STATUS_COMPLETED : STATUS_PROCESSING,
                progress: percent,
                lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
                orgSourcedId:job.data.schoolSourcedId
            });
        }
        // HANDLE IF HALFT DATA PER ORG PROGRESSBAR -- end

        const queryall = `
            SELECT 
                import_classes.sourcedId,
                import_classes.submited
            FROM 
                import_classes
                INNER JOIN rel_academic_sessions ON import_classes.termSourcedIds IN (rel_academic_sessions.importSourcedId,rel_academic_sessions.rosterSourcedId)
                INNER JOIN rel_orgs ON import_classes.schoolSourcedId IN (rel_orgs.importSourcedId,rel_orgs.rosterSourcedId)
            WHERE 
                import_classes.classType = 'homeroom'
                AND import_classes.option != 'skip_csv_to_lgate'
                AND import_classes.option != 'delete_add_from_lgate'
                AND import_classes.municipalId = '${job.data.municipalId}'
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
            const [classAlreadyToSubmit] = await db[job.data.municipalId].query(
                    `SELECT COUNT(sourcedId) as count FROM import_classes WHERE municipalId = '${job.data.municipalId}' and classType='homeroom' and submited='1' and isParentSkiped='0' LIMIT 1`
            )
            const [classHaveToSubmit] = await db[job.data.municipalId].query(
                    `SELECT COUNT(sourcedId) as count FROM import_classes WHERE municipalId = '${job.data.municipalId}' and classType='homeroom' and isParentSkiped='0' LIMIT 1`
            )
        
            const countClassSubmited = parseInt(classAlreadyToSubmit[0]?.count || 0)
            const countClassImport = parseInt(classHaveToSubmit[0]?.count || 0)
    
            percent = (countClassSubmited/countClassImport)*100
        }

        // HANDLE PARENT AND CHILD PROGRESS BAR -- end
        
        await db[job.data.municipalId].importTaskProgress.upsert({
            id: importTaskProgressId,
            municipalId: job.data.municipalId,
            type: CLASS_COLLATION,
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

        let logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.submit_merged_finish')}
        LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
        console.log('completeds',job.id, result)
    }

    onFailed = async (job, err) => {
        console.log('failed',job.id)
        
        let logData = {logFor: CLASS_COLLATION,message:lang.t('submit_classes.message.submit_merged_failed').replace('%MESSAGE%',err.message)}
        LOG.create({type: LOG_TYPE_SUBMIT_MATCHING, logData});
    }
    
}

/**
 * Create export variable to running function SubmitClasses
 * @constructor
 */
const SubmitClassesProcess = new SubmitClasses()

export default SubmitClassesProcess