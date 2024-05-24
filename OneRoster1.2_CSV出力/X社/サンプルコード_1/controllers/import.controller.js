import {
  extractFile,
  checkManifest,
  checkAcademicSession,
  checkClasses,
  checkCourses,
  checkEnrollments,
  checkOrgs,
  checkUsers,
  checkRoles,
  readCsv,
  checkDemographics,
  checkUserProfiles
} from "../helpers/import.js";
import { existsSync } from "fs";
import moment from "moment";
import Bull from "bull";
import { startImportQueue,getJobImportQueue } from "../job/queues/ImportQueue.js";
import {
  TABLE_NAME_ACADEMIC_SESSIONS,
  TABLE_NAME_ORGS,
  TABLE_NAME_COURSES,
  TABLE_NAME_CLASSES,
  TABLE_NAME_USERS,
  TABLE_NAME_ROLES,
  TABLE_NAME_ENROLLMENTS,
  YEAR_COLLATION,
  SCHOOL_COLLATION,
  CLASS_COLLATION,
  OTHER_CLASS_COLLATION,
  COURSES_COLLATION,
  ADMINISTRATOR_COLLATION,
  CLASS_ATENDANCE_COLLATION,
  OTHER_ATENDANCE_COLLATION,
  USER_ASSIGNMENT_SCREEN,
  USER_CONFIRMATION_SCREEN,
  MANIFEST_FILE_VALUE_DELTA,
  SKIPED_USER_COLLATION,
  STATUS_PROCESSING,
  IMPORT_CSV,
  IMPORT_EMPTY_DELTA,
  IMPORT_DELTA_MERGE,
  FILL_USER_PRIMARY_ORGS,
  CHECK_SOURCED_ID
} from "../constants/constans.js";
import { db } from "../models/index.js";
import config from "../config/config.js";
import { submitJob, getJobQueue } from "../job/queues/SubmitToLgate.js";
import { submitJobSkiped, getJobSkipedQueue } from "../job/queues/SubmitSkipedToLgate.js";
import redisClient from "../redisClient.js";
import QueryTypes from "sequelize";

let ImportTaskProgress, ImportTaskProgressDetail,  Import, importDraftTask, ImportAcademicSessions, ImportOrgs, ImportClasses, ImportCourses, ImportUsers, ImportRoles, ImportEnrollments, LgateOrganization, LgateClasses, LgateUsers, LgateEnrollments, LgateRole, ImportTaskJob = false;
let SkipedImportUsers, SkipedImportEnrollments, AcademicSessions, Orgs, Courses, Classes, Users, Roles, Enrollments, Op, relAcademicSessions, relOrgs, relClasses, relCourses, relUsers, relEnrollments = false;
let currMunicipalDB = false;
let rawMunicipalDb = false;

/**
 * Setting db connection to selected municipal
 * @constructor
 */
const initMunicipalDb = (municipalId) => {
  if (municipalId) {
    if (currMunicipalDB != municipalId) {
      currMunicipalDB = municipalId;
      ImportTaskProgress = db[municipalId].importTaskProgress
      ImportTaskProgressDetail = db[municipalId].importTaskProgressDetail
      ImportTaskJob = db[municipalId].importTaskJob
      Import = db[municipalId].import
      importDraftTask = db[municipalId].importDraftTask;
      ImportAcademicSessions = db[municipalId].importAcademicSessions;
      ImportOrgs = db[municipalId].importOrgs;
      ImportClasses = db[municipalId].importClasses;
      ImportCourses = db[municipalId].importCourses;
      ImportUsers = db[municipalId].importUsers;
      ImportRoles = db[municipalId].importRoles;
      ImportEnrollments = db[municipalId].importEnrollments;
      LgateOrganization = db[municipalId].lgateOrganization;
      LgateClasses = db[municipalId].lgateClasses;
      LgateUsers = db[municipalId].lgateUsers;
      LgateEnrollments = db[municipalId].lgateEnrollments;
      LgateRole = db[municipalId].lgateRole;
      AcademicSessions = db[municipalId].academicSessions;
      Orgs = db[municipalId].orgs;
      Courses = db[municipalId].courses;
      Classes = db[municipalId].classes;
      Users = db[municipalId].users;
      Roles = db[municipalId].roles;
      Enrollments = db[municipalId].enrollments;
      Op = db[municipalId].Sequelize.Op;
      relAcademicSessions = db[municipalId].relAcademicSessions;
      relOrgs = db[municipalId].relOrgs;
      relClasses = db[municipalId].relClasses;
      relCourses = db[municipalId].relCourses;
      relUsers = db[municipalId].relUsers;
      relEnrollments = db[municipalId].relEnrollments;
      SkipedImportUsers = db[municipalId].skipedImportUsers;
      SkipedImportEnrollments = db[municipalId].skipedImportEnrollments;
      relEnrollments = db[municipalId].relEnrollments;
      rawMunicipalDb = db[municipalId];
    }
  }else{
    console.log("INIT MUNICIPAL NULL import.controller ", municipalId);
  }
};

const Queue = new Bull('submit_to_lgate', {
  redis: {
      port:config.REDIS_PORT,
      host:config.REDIS_HOST,
      db:config.REDIS_DB_JOB,
      password:config.REDIS_PASSWORD    
  },
})

/**
 * Get list csv import of selected municipal
 * @constructor
 */
export const findImport = async(req, res) => {
  try {
    let municipalId = req.params.id;

    initMunicipalDb(municipalId);
    
    let condition = {};
    if (municipalId && municipalId !== "undefined") condition.municipalId = { [Op.eq]: municipalId };

    let data = await Import.findAll({where: condition });
    let refactorData = data.map(item => ({...item?.dataValues, jobImportID: item?.jobId}))
    res.send(refactorData)
  } catch (error) {
    res.status(500).json({ error: error?.message });
  }
}

/**
 * Process to upload imported csv
 * @constructor
 */
export const uploadFile = async (req, res) => {
    let municipalId = req.body.municipalId;
    let file = req.file;

    initMunicipalDb(municipalId);

    if (!municipalId){
      res
        .status(400)
        .json({ message: "municipalId required" });
    } else if (!file) {
      res
        .status(400)
        .json({ message: "file missing, please attach file to be imported!" });
    } else {
      /* restrict file size max 2mb */
      if (file?.size > 1000000 * config.IMPORT_MAX_FILE_SIZE) {
        return res.status(400).json({ message: `File size not more than ${config.IMPORT_MAX_FILE_SIZE} mb!` });
      }
      /* extract file */
      await extractFile(file);

      
      let errors = [];
      const { errors: manifestErrors, data: manifestData } = await checkManifest(`${file?.destination}manifest.csv`);
      const { errors: academicSessionErrors, data: academicSessionData } = await checkAcademicSession(`${file?.destination}academicSessions.csv`, manifestData?.['file.academicSessions'], manifestData?.['oneroster.version']);
      const { errors: classesErrors, data: classesData } = await checkClasses(`${file?.destination}classes.csv`, manifestData?.['file.classes'], manifestData?.['oneroster.version']);
      const { errors: coursesErrors, data: coursesData } = await checkCourses(`${file?.destination}courses.csv`, manifestData?.['file.courses'], manifestData?.['oneroster.version']);
      const { errors: enrollmentsErrors, data: enrollmentsData } = await checkEnrollments(`${file?.destination}enrollments.csv`, manifestData?.['file.enrollments'], manifestData?.['oneroster.version']);
      const { errors: orgsErrors, data: orgsData } = await checkOrgs(`${file?.destination}orgs.csv`, manifestData?.['file.orgs'], manifestData?.['oneroster.version']);
      const { errors: usersErrors, data: usersData } = await checkUsers(`${file?.destination}users.csv`, manifestData?.['file.users'], manifestData?.['oneroster.version']);
      const { errors: rolesErrors, data: rolesData } = await checkRoles(`${file?.destination}roles.csv`, manifestData?.['file.roles'], manifestData?.['oneroster.version']);
      const { errors: demographicsErrors, data: demographicsData } = await checkDemographics(`${file?.destination}demographics.csv`, manifestData?.['file.demographics'], manifestData?.['oneroster.version']);
      const { errors: userProfilesErrors, data: userProfilesData } = await checkUserProfiles(`${file?.destination}userProfiles.csv`, manifestData?.['file.userProfiles'], manifestData?.['oneroster.version']);

      errors = [...manifestErrors, ...academicSessionErrors, ...classesErrors, ...coursesErrors, ...enrollmentsErrors, ...orgsErrors, ...usersErrors, ...rolesErrors, ...demographicsErrors, ...userProfilesErrors];
      
      if(errors.length > 0){
        return res.status(500).json({message: "Export error, please re-check csv file below", data: errors});
      }

      const clearTableList = [
        ImportAcademicSessions, 
        ImportOrgs, 
        ImportClasses, 
        ImportCourses, 
        ImportUsers, 
        ImportRoles,
        ImportEnrollments,
        ImportTaskProgress, 
        ImportTaskProgressDetail,
        Import, 
        importDraftTask, 
        LgateOrganization, 
        LgateClasses, 
        LgateUsers, 
        LgateEnrollments, 
        LgateRole
      ];

      await Promise.all(
        clearTableList.map(async (table) => {
          await clearTable(table, municipalId);
        })
      );

      let manifestFiles = [
        "file.academicSessions",
        "file.categories",
        "file.classes",
        "file.classResources",
        "file.courses",
        "file.courseResources",
        "file.demographics",
        "file.enrollments",
        "file.lineItems",
        "file.orgs",
        "file.resources",
        "file.results",
        "file.users",
        "file.roles"
      ];
      
      let manifest = await readCsv(`${file?.destination}manifest.csv`, { headers: true }, (row) => manifestFiles.includes(row.propertyName) && row.value != 'absent');  
      let manifestAbsent = await readCsv(`${file?.destination}manifest.csv`, { headers: true }, (row) => manifestFiles.includes(row.propertyName) && row.value === 'absent');  

      let payload = {
        jobs : []
      }
      let importData = {
        type : IMPORT_CSV,
        municipalId : req.body.municipalId,
        data : []
      }
      let classCsv,coursesClassCsv;

      
      let importSourcedIdCheck
      let fileExists = []
      let csverr = []
      importSourcedIdCheck = 0
  
      importSourcedIdCheck += await relAcademicSessions.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
      importSourcedIdCheck += await relOrgs.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
      importSourcedIdCheck += await relClasses.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
      importSourcedIdCheck += await relClasses.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
      importSourcedIdCheck += await relUsers.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
  
      importSourcedIdCheck += await relAcademicSessions.count({
          where : {
              municipalId : { [Op.eq] : municipalId }
          }
      });
  
      const autoImportTable = {};
      const importedTable = {};
      await Promise.all(manifestAbsent.map(async (item) => {
        switch (item.propertyName) {
          case "file.academicSessions":
            autoImportTable[TABLE_NAME_ACADEMIC_SESSIONS] = 1;
            break;
      
          case "file.orgs":
            autoImportTable[TABLE_NAME_ORGS] = 1;
            break;
      
          case "file.classes":
            autoImportTable[TABLE_NAME_CLASSES] = 1;
            break;
        }
      }));
      await Promise.all(manifest.map(async (item) => {
        fileExists.push(item.propertyName)
        switch (item.propertyName) {
          case "file.academicSessions":

            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}academicSessions.csv`)){
                importData.data.push({
                  table : TABLE_NAME_ACADEMIC_SESSIONS,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_ACADEMIC_SESSIONS] = 1;
              }
            }
            break;
      
          case "file.orgs":
            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}orgs.csv`)){
                importData.data.push({
                  table : TABLE_NAME_ORGS,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_ORGS] = 1;
              }
            }
            break;
        
          case "file.classes":
            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}classes.csv`)){
                importData.data.push({
                  table : TABLE_NAME_CLASSES,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_CLASSES] = 1;
              }
            }
            break;
        
          case "file.courses":
            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}courses.csv`) && existsSync(`${file?.destination}classes.csv`)){
                importData.data.push({
                  table : TABLE_NAME_COURSES,
                  csv : coursesClassCsv,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_COURSES] = 1;
              }
            }

            break;
        
          case "file.users":
            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}users.csv`)){
                importData.data.push({
                  table : TABLE_NAME_USERS,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_USERS] = 1;
              }
            }
            break;

          case "file.roles":
            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
              csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}roles.csv`)){
                importData.data.push({
                  table : TABLE_NAME_ROLES,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_ROLES] = 1;
              }
            }
            break;
        
          case "file.enrollments":

            if(item.value == MANIFEST_FILE_VALUE_DELTA && importSourcedIdCheck == 0){
                csverr.push(`${item.propertyName} must bulk first before import delta`);
            } else {
              if(existsSync(`${file?.destination}enrollments.csv`)){
                importData.data.push({
                  table : TABLE_NAME_ENROLLMENTS,
                  path : file?.destination,
                  output : item.value
                })
                importedTable[TABLE_NAME_ENROLLMENTS] = 1;
              }
            }
            break;
        }
      }))

      if(csverr.length){
        return res.status(500).send({data : csverr, message : `csv import must bulk first before import delta` });
      } else {
      
        if(
          (importedTable[TABLE_NAME_CLASSES] && !importedTable[TABLE_NAME_COURSES]) ||
          (!importedTable[TABLE_NAME_CLASSES] && importedTable[TABLE_NAME_COURSES]) ||
          (importedTable[TABLE_NAME_USERS] && !importedTable[TABLE_NAME_ROLES] && manifestData?.['oneroster.version'] === "1.2") ||
          (!importedTable[TABLE_NAME_USERS] && importedTable[TABLE_NAME_ROLES] && manifestData?.['oneroster.version'] === "1.2")
        ){
          return res.status(500).json({message: "csv import delta doesn't match the package", data: errors});
        }

        payload.jobs.push(importData)
              
        if(Object.keys(autoImportTable).length > 0){
          payload.jobs.push({
            type : IMPORT_EMPTY_DELTA,
            autoImportTable: autoImportTable,
            importedTable: importedTable,
            municipalId : req.body.municipalId
          })
        }
        if(fileExists.includes("file.academicSessions") || (Object.keys(autoImportTable).length > 0 && autoImportTable[TABLE_NAME_ACADEMIC_SESSIONS])){
          payload.jobs.push({
            type : YEAR_COLLATION,
            municipalId : req.body.municipalId
          })
        }
        if(fileExists.includes("file.orgs") || (Object.keys(autoImportTable).length > 0 && autoImportTable[TABLE_NAME_ORGS])){
          payload.jobs.push({
            type : SCHOOL_COLLATION,
            municipalId : req.body.municipalId
          })
        }

        if (manifestData?.['oneroster.version'] === "1.2") {
          payload.jobs.push({
            type : FILL_USER_PRIMARY_ORGS,
            municipalId : req.body.municipalId
          })
        }
        
        if(Object.keys(autoImportTable).length > 0){
          payload.jobs.push({
            type : IMPORT_DELTA_MERGE,
            autoImportTable: autoImportTable,
            importedTable: importedTable,
            municipalId : req.body.municipalId
          })
        }

        payload.jobs.push({
          type : CHECK_SOURCED_ID,
          municipalId : req.body.municipalId
        })
        
        await ImportTaskProgress.destroy({
          where : {
            municipalId : req.body.municipalId
          }
        })

        await ImportTaskProgressDetail.destroy({
          where : {
            municipalId : req.body.municipalId
          }
        })
        
        await importDraftTask.destroy({
          where : {
            municipalId : req.body.municipalId
          }
        })
        file.jobs = await startImportQueue(payload);

        const updateTableList = [
          AcademicSessions, 
          Orgs, 
          Courses, 
          Classes, 
          Users, 
          Roles,
          Enrollments, 
        ];
    
        await Promise.all(
          updateTableList.map(async (table) => {
            await updateIsTobeletedTable(table, municipalId);
          })
        );

        /* Create import list ID by municipal*/
        await Import.upsert({
          id: `${req.body.municipalId}`,
          municipalId: req.body.municipalId,
          jobId: file?.jobs?.[0]?.id,
          status: null,
          lastUpdated: moment().format("YYYY-MM-DD HH:mm:ss"),
        });
    
        
        res.send(file);
      }
    }
};

/**
 * Get status of bull job for csv import process
 * @constructor
 */
export const getJobStatus = async (req, res) => {
  try {
    const jobImport = req?.params?.id;
    const jobAcademicSession = jobImport.replace('IMPORT_CSV','YEAR_COLLATION');
    const jobOrgs = jobImport.replace('IMPORT_CSV','SCHOOL_COLLATION'); 
    const jobCekSourcedId = jobImport.replace('IMPORT_CSV','CHECK_SOURCED_ID'); 
    let job1 = await getJobImportQueue(jobImport);
    let job2 = await getJobImportQueue(jobAcademicSession);
    let job3 = await getJobImportQueue(jobOrgs);
    let job4 = await getJobImportQueue(jobCekSourcedId);

    if (job1?.returnvalue?.message === 'COMPLETED'){
      if((job2?.returnvalue?.message != 'COMPLETED' && job2 != null) || (job3?.returnvalue?.message != 'COMPLETED' && job3 != null)) {
        job1.returnvalue.message = 'MERGING';
      }

      if (job4?.returnvalue?.message != 'COMPLETED' && job4 != null) {
        job1.returnvalue = job4?.returnvalue;
        job1.failedReason = job4?.failedReason;
      }
    }

    res.status(200).json(job1);
  } catch (err) {
      res.status(400).send({ error : err.message });
  }
};

/**
 * Create response for api /dummyApi
 * @constructor
 */
export const dummyApi = async (req, res) => {
    res.status(200).json({
      "is_successful": true,
      "code": 200
    });
}

/**
 * Process submit imported data to lgate
 * @constructor
 */
export const submitLgate = async (req, res) => {
  try {
    let job = await submitJob(req.body)
    return res.status(200).send(job);
  } catch (err) {
    let validationError = JSON.parse(JSON.stringify(err))?.original
    if(validationError?.sqlMessage){
      return res.status(400).send({ error : validationError?.sqlMessage });
    }
    return res.status(400).send({ error : err.message });
  }
}

/**
 * Process submit skipped user to lgate
 * @constructor
 */
export const submitLgateSkipedUser = async (req, res) => {
  initMunicipalDb(req.body.municipalId);
  try {
    const municipalId = req.body.municipalId;
    
    const condition = { 
      [Op.or]: [
        {
          password: {
            [Op.eq]: ''
          }
        },{
          password: {
            [Op.eq]: null
          }
        },
      ]
    };
    if (municipalId && municipalId !== "null") condition.municipalId = { [Op.eq]: municipalId };
    
    const dataResult = await SkipedImportUsers.findAll({
      attributes: ["sourcedId","givenName", "familyName", "middleName", "email","password"],
      include: [
        { model: Orgs, attributes: ["name"] },
      ],
      where: condition,
      order: [['sourcedId', 'ASC']],
    });

    let userPasswordFail = [];
    dataResult.map((item) => {
      userPasswordFail.push(`「${item?.org?.name}」 ${item.familyName} ${item.givenName} はパスワードが設定されない`)
    })

    if(userPasswordFail.length){
      return res.status(400).json({
        status: false,
        message : userPasswordFail
      });
    }

    await ImportTaskJob.destroy({
      where: { municipalId: req.body.municipalId, type: SKIPED_USER_COLLATION }
    });

    let job = await submitJobSkiped(req.body)
    await ImportTaskJob.upsert({
      municipalId: req.body.municipalId,
      type: SKIPED_USER_COLLATION,
      jobId : job.id,
      userId : '1',
      createdDate : moment().format("YYYY-MM-DD HH:mm:ss")
    });
    return res.status(200).send(job);
  } catch (err) {
    let validationError = JSON.parse(JSON.stringify(err))?.original
    if(validationError?.sqlMessage){
      return res.status(400).send({ error : validationError?.sqlMessage });
    }
    return res.status(400).send({ error : err.message });
  }
}

/**
 * Get status of bull job for process of submit imported data to lgate 
 * @constructor
 */
export const getJobStatusSubmit = async (req, res) => {
  try { 
    let jobId = req?.params?.id;
    let job = await getJobQueue(jobId);
    res.status(200).json(job);
  } catch (err) {
      res.status(400).send({ error : err.message });
  }
};

/**
 * Get status of bull job for process of submit skipped used to lgate 
 * @constructor
 */
export const getJobStatusSubmitSkiped = async (req, res) => {
  try { 
    let jobId = req?.params?.id;
    let job = await getJobSkipedQueue(jobId);
    res.status(200).json(job);
  } catch (err) {
      res.status(400).send({ error : err.message });
  }
};

/**
 * Process to clear imported data from table and delete bull job from redis
 * @constructor
 */
export const processDiscardImport = async (municipalId, jobId=null) => {
  initMunicipalDb(municipalId);
    
  const clearTableList = [
    ImportAcademicSessions, 
    ImportOrgs, 
    ImportClasses, 
    ImportCourses, 
    ImportUsers, 
    ImportRoles,
    ImportEnrollments, 
    ImportTaskProgress, 
    ImportTaskProgressDetail,
    Import, 
    importDraftTask, 
    LgateOrganization, 
    LgateClasses, 
    LgateUsers, 
    LgateEnrollments, 
    LgateRole
  ];

  const cleareTableRel = [
    relAcademicSessions, 
    relOrgs, 
    relClasses, 
    relCourses, 
    relUsers, 
    relEnrollments, 
  ];

  const updateTableList = [
    AcademicSessions, 
    Orgs, 
    Courses, 
    Classes, 
    Users, 
    Enrollments, 
  ];

  await Promise.all(
    clearTableList.map(async (table) => {
      await clearTable(table, municipalId);
    }),
    cleareTableRel.map(async (table) => {
      await clearTableRel(table, municipalId);
    })
  );

  await redisClient.del(`LOCK_IMPORT_${municipalId}`);
  await redisClient.del(`SKIPPED_USERS_${municipalId}`);
  if(jobId){
    await removeJobQueue(jobId);
  }

  return true;
}

/**
 * Process to call function processDiscardImport to discard imported data
 * @constructor
 */
export const discardImport = async (req, res) => {
  try { 
    let municipalId = req.body.municipalId;
    let jobId = req.body?.jobId;

    await processDiscardImport(municipalId, jobId);

    res.send(true);
  } catch (err) {
    res.status(400).send({ error : err.message });
  }
};

/**
 * Process to clear data from selected table
 * @constructor
 */
export const clearTable = async (table, municipalId) => {
  try {
    return await table.destroy({
      where: { municipalId: municipalId }
    })
  } catch (error) {
    return error;
  }
}

/**
 * Process to clear data from selected rel table
 * @constructor
 */
export const clearTableRel = async (table, municipalId) => {
  try {
    return await table.destroy({
      where: { municipalId: municipalId, isTemp: 1 }
    })
  } catch (error) {
    return error;
  }
}

/**
 * Process to updating field status becomes active from selected table
 * @constructor 
 */
export const updateStatusTable = async (table, municipalId) => {
  try {
    return await table.update(
      { status: 'active' },
      { where: { municipalId: municipalId } }
    )
  } catch (error) {
    return error;
  }
}

/**
 * Process to updating field isToBeDeleted becomes 0 from selected table
 * @constructor
 */
export const updateIsTobeletedTable = async (table, municipalId) => {
  try {
    return await table.update(
      { isToBeDeleted: 0 },
      { where: { municipalId: municipalId } }
    )
  } catch (error) {
    return error;
  }
}

/**
 * Process to delete bull job
 * @constructor
 */
const removeJobQueue = async (jobId) => {
  Queue.getJob(jobId).then((job) => { 
      if(job) {
          return job.remove(); 
      }else {
          return false
      }
  }).catch(()=>{
      return false; 
  })
}