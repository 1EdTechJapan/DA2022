import fs, { existsSync, mkdirSync, unlinkSync } from "fs";
import path from "path";
import csv from "csv-parser";
import fsExtra from "fs-extra";
import Joi from "joi";
import extract from "extract-zip";
import {  manifestValidation, 
          manifestValidationV12, 
          academicSessionsValidation, 
          classesValidation, 
          coursesValidation, 
          enrollmentValidation, 
          orgsValidation, 
          usersValidation, 
          usersValidationV12, 
          rolesValidation,
          demographicsValidation,
          userProfilesValidation 
        } from "./importValidation.js";

const OR_V11 = '1.1';
const OR_V12 = '1.2';
const allowedORVersion = [OR_V11,OR_V12];

/**
 * Process to extract files of imported zip file
 * @constructor
 */
export const extractFile = async (file, removeRawFile = true) => {
  /* extract file */
  try {
    await extract(file?.path, { dir: path.resolve(file?.destination) });
    let currentFolder = `${file?.destination}${file?.filename.split(".")[0]}/`;
    /* copy file */
    await copyFiles(currentFolder, file?.destination);
    /* remove existing folder */
    if (existsSync(currentFolder)) fsExtra.removeSync(currentFolder);
    /* if raw file is remove */
    if (removeRawFile) {
      if (existsSync(file?.path)) unlinkSync(file?.path);
    }
  } catch (err) {
    console.error("helper/import extractFile =>>>>" + err);
  }
};

/**
 * Process to copy files to another folder destination
 * @constructor
 */
export const copyFiles = async (currentFolder, destination) => {
  try {
    fsExtra.copySync(currentFolder, destination);
  } catch (err) {
    console.error("helper/import copy file =>>>>" + err);
  }
};

/**
 * Process to read data from csv file
 * @constructor
 */
export const readCsv = (path, options, rowProcessor) => {
  return new Promise((resolve, reject) => {
    const data = [];
    let inputStream = fs.createReadStream(path, "utf8");

    inputStream
      .pipe(csv())
      .on("error", (error) => {
        console.log("ERROR");
        console.log(error);
        reject(error);
      })
      .on("data", (row) => {
        const obj = rowProcessor(row);
        /* push data with new array */
        if (obj) data.push(row);
      })
      .on("end", () => {
        resolve(data);
      });
  });
};

/**
 * Process to check data from manifest file
 * @constructor
 */
export const checkManifest = async (pathFile) => {
  let errors = [];
  let data = {};
  if (!existsSync(pathFile)) {
    errors.push("manifest.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    /* refactor object */
    if (dataCsv.length > 0) {

      if (dataCsv[0].propertyName == undefined) {
        errors.push("manifest.csv header propertyName is unknown"); 
        return { errors, data };
      }

      if (dataCsv[0].value == undefined) {
        errors.push("manifest.csv header value is unknown"); 
        return { errors, data };
      }

      let newObjManifest = {};
      dataCsv.forEach((item) => {
        return (newObjManifest[item.propertyName] = item.value);
      });

      if (newObjManifest['oneroster.version'] !== undefined) {
        let schema = false;
        if (newObjManifest['oneroster.version'] == OR_V11) {
          schema = manifestValidation;
        }else if(newObjManifest['oneroster.version'] == OR_V12){
          schema = manifestValidationV12;
        }

        if (schema) {
          const { error } = schema.validate(newObjManifest, { abortEarly: false });
          if (error?.details) {
            let mapError = error?.details.map((item) => `manifest.csv item row value ${item?.message}`);
            errors.push(...mapError);
          }

          data = newObjManifest;
        }else{
          errors.push("manifest.csv item oneroster.version is not valid");
        }
      }else{
        errors.push("manifest.csv oneroster.version column is unknown");
      }
    }else{
      errors.push("manifest.csv content is empty");
    }
  }

  return { errors, data };
};

/**
 * Process to check same value of 2 arrays with same key
 * @constructor
 */
function arrayEquals(a, b) {
  let eq = true;
  for (var i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) {
      eq = false;
      i = a.length;
    }
  }
  return eq;
}

/**
 * Process to validating data from academic session csv file
 * @constructor
 */
export const checkAcademicSession = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};
  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("academicSessions.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("academicSessions.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "title",
                        "type",
                        "startDate",
                        "endDate",
                        "parentSourcedId",
                        "schoolYear" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = academicSessionsValidation(type);
        dataCsv.forEach((item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            let mapError;
            if (error?.details) {
              mapError = error?.details.map((item) => `academicSessions.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
            if (item.parentSourcedId && item.parentSourcedId != 'NULL' && item.parentSourcedId != NULL) {
              const idxParentSourcedId = dataCsv.findIndex(val => val.sourcedId === item?.parentSourcedId);
              if (idxParentSourcedId < 0) {
                mapError = `academicSessions.csv item row number ${index + 2} "parentSourcedId" not exists in other record of academicSessions data`;
                errors.push(mapError);
              }
            }
          } catch (error) {
            errors.push(`academicSessions.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`academicSessions.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from classes csv file
 * @constructor
 */
export const checkClasses = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};
  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("classes.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("classes.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      const headers = [ "sourcedId",
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
                        "periods" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      console.log("HV ",headerValid);
      if (headerValid) {
        const schema = classesValidation(type);
        dataCsv.forEach((item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            if (error?.details) {
              let mapError = error?.details.map((item) => `classes.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
          } catch (error) {
            errors.push(`classes.csv  item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`classes.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from courses csv file
 * @constructor
 */
export const checkCourses = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("courses.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("courses.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "schoolYearSourcedId",
                        "title",
                        "courseCode",
                        "grades",
                        "orgSourcedId",
                        "subjects",
                        "subjectCodes" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = coursesValidation(type);
        dataCsv.forEach((item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            if (error?.details) {
              let mapError = error?.details.map((item) => `courses.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
          } catch (error) {
            errors.push(`courses.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`courses.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from enrollments csv file
 * @constructor
 */
export const checkEnrollments = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("enrollments.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("enrollments.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "classSourcedId",
                        "schoolSourcedId",
                        "userSourcedId",
                        "role",
                        "primary",
                        "beginDate",
                        "endDate" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = enrollmentValidation(type);
        dataCsv.forEach((item, index) => {
          try {
            if (index == 0) {
              console.log(item);
            }
            const { error } = schema.validate(item, { abortEarly: false });
            if (error?.details) {
              let mapError = error?.details.map((item) => `enrollments.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
          } catch (error) {
            errors.push(`enrollments.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`enrollments.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from orgs csv file
 * @constructor
 */
export const checkOrgs = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("orgs.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("orgs.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "name",
                        "type",
                        "identifier",
                        "parentSourcedId" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = orgsValidation(type);
        dataCsv.forEach((item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            let mapError
            if (error?.details) {
              mapError = error?.details.map((item) => `orgs.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
            
            if (item.parentSourcedId) {
              const idxParentSourcedId = dataCsv.findIndex(val => val.sourcedId === item?.parentSourcedId);
              if (item.type === "district" && idxParentSourcedId >= 0 && dataCsv[idxParentSourcedId].type === "district") {
                mapError = `orgs.csv item row number ${index + 2} "parentSourcedId" value cannot from other school with type 'district'`;
                errors.push(mapError);
              }
              if (idxParentSourcedId < 0) {
                mapError = `orgs.csv item row number ${index + 2} "parentSourcedId" not exists in other record of orgs data`;
                errors.push(mapError);
              }
            }
          } catch (error) {
            errors.push(`orgs.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`orgs.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Suspend the process of a function
 * @constructor
 */
const sleep = (ms) => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
};

/**
 * Process to validating data from users csv file
 * @constructor
 */
export const checkUsers = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (type == "absent" || !allowedORVersion.includes(orVersion)) {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("users.csv file is exist but manifest.csv value is absent");
    }
  } else if (!existsSync(pathFile)) {
    errors.push("users.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true, objectMode: false }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    /* Create schema validation with payload type of export */
    if (type != "absent" && dataCsv.length > 0) {
      let headers = [];
      if (orVersion == OR_V11) {
        headers = [ "sourcedId",
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
                    "password" ];
      }else if(orVersion == OR_V12){
        headers = [ "sourcedId",
                    "status",
                    "dateLastModified",
                    "enabledUser",
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
                    "userMasterIdentifier",
                    "resourceSourcedIds",
                    "preferredGivenName",
                    "preferredMiddleName",
                    "preferredFamilyName",
                    "primaryOrgSourcedId",
                    "pronouns" ];
      }

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        let schema = false;

        if (orVersion == OR_V11) {
          schema = usersValidation(type);
        }else if(orVersion == OR_V12){
          schema = usersValidationV12(type);
        }

        if (schema) {
          const userMasterIdentifierDupe = [];
          dataCsv.forEach(async (item, index) => {
            try {
              const { error } = schema.validate(item, { abortEarly: false });
              let mapError;
              if (error?.details) {
                mapError = error?.details.map((item) => `users.csv item row number ${index + 2} ` + item?.message);
                errors.push(...mapError);
              }
              if (item?.userMasterIdentifier) {
                const checkUserMasterIdentifierIdx = userMasterIdentifierDupe.findIndex(val => val === item?.userMasterIdentifier);
                if (checkUserMasterIdentifierIdx < 0) {
                  userMasterIdentifierDupe.push(item?.userMasterIdentifier)
                } else {
                  mapError = `users.csv item row number ${index + 2} "userMasterIdentifier" have a duplicate value with other data`;
                  errors.push(mapError);
                }
              }
            } catch (error) {
              errors.push(`users.csv item row number ${index + 2} is invalid`);
            }
          });
        }
      }else{
        errors.push(`users.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from roles csv file
 * @constructor
 */
export const checkRoles = async (pathFile, type, orVersion, userProfilesData=[]) => {
  let errors = [];
  let data = {};

  if (!allowedORVersion.includes(orVersion) || orVersion != OR_V12 || type == "absent") {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("roles.csv file is exist but manifest.csv value is absent");
    }
    //do nothing
  } else if (!existsSync(pathFile)) {
    errors.push("roles.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true, objectMode: false }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    
    if (dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "userSourcedId",
                        "roleType",
                        "role",
                        "beginDate",
                        "endDate",
                        "orgSourcedId",
                        "userProfileSourcedId" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = rolesValidation(type);
        dataCsv.forEach(async (item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            let mapError;
            if (error?.details) {
              mapError = error?.details.map((item) => `roles.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }

            // check userProfileId
            if (item.userProfileSourcedId) {
              const idxUserProfile = userProfilesData.findIndex(val => val.sourcedId === item?.userProfileSourcedId);
              if (idxUserProfile < 0) {
                mapError = `roles.csv item row number ${index + 2} "userProfileSourcedId" not exists in record of userProfiles.csv`;
                errors.push(mapError);
              }
            }
          } catch (error) {
            errors.push(`roles.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`roles.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from demographics csv file
 * @constructor
 */
export const checkDemographics = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (!allowedORVersion.includes(orVersion) || orVersion != OR_V12 || type == "absent") {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("demographics.csv file is exist but manifest.csv value is absent");
    }
    //do nothing
  } else if (!existsSync(pathFile)) {
    errors.push("demographics.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true, objectMode: false }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    
    if (dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "birthDate",
                        "sex",
                        "americanIndianOrAlaskaNative",
                        "asian",
                        "blackOrAfricanAmerican",
                        "nativeHawaiianOrOtherPacificIslander",
                        "white",
                        "demographicRaceTwoOrMoreRaces",
                        "hispanicOrLatinoEthnicity",
                        "countryOfBirthCode",
                        "stateOfBirthAbbreviation",
                        "cityOfBirth",
                        "publicSchoolResidenceStatus"];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = demographicsValidation(type);
        dataCsv.forEach(async (item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            if (error?.details) {
              let mapError = error?.details.map((item) => `demographics.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
          } catch (error) {
            errors.push(`demographics.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`demographics.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};

/**
 * Process to validating data from user profiles csv file
 * @constructor
 */
export const checkUserProfiles = async (pathFile, type, orVersion) => {
  let errors = [];
  let data = {};

  if (!allowedORVersion.includes(orVersion) || orVersion != OR_V12 || type == "absent") {
    if (type == "absent" && existsSync(pathFile)){
      errors.push("userProfiles.csv file is exist but manifest.csv value is absent");
    }
    //do nothing
  } else if (!existsSync(pathFile)) {
    errors.push("userProfiles.csv file doest'n exist");
  } else {
    /* read file csv*/
    let dataCsv = [];
    try{
      dataCsv = await readCsv(pathFile, { allowQuotes: false, asObject: true, objectMode: false }, (row) => row);
    } catch (err){
      errors.push(err);
    }
    data = dataCsv;
    
    if (dataCsv.length > 0) {
      const headers = [ "sourcedId",
                        "status",
                        "dateLastModified",
                        "userSourcedId",
                        "profileType",
                        "vendorId",
                        "applicationId",
                        "description",
                        "credentialType",
                        "username",
                        "password" ];

      const headerValid = arrayEquals(headers,Object.keys(dataCsv[0]));
      if (headerValid) {
        const schema = userProfilesValidation(type);
        dataCsv.forEach(async (item, index) => {
          try {
            const { error } = schema.validate(item, { abortEarly: false });
            if (error?.details) {
              let mapError = error?.details.map((item) => `userProfiles.csv item row number ${index + 2} ` + item?.message);
              errors.push(...mapError);
            }
          } catch (error) {
            errors.push(`userProfiles.csv item row number ${index + 2} is invalid`);
          }
        });
      }else{
        errors.push(`userProfiles.csv header is invalid, the header should be contain [${headers.join(", ")}] and have valid order`);
      }
    }
  }

  return { errors, data };
};
