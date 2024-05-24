import JJoi from "joi";
import JoiDate from "@joi/date";

const Joi = JJoi.extend(JoiDate);

const string = Joi.string();
const number = Joi.number();
const date = Joi.date().format("YYYY-MM-DD").raw();
const year = Joi.date().format("YYYY");

/**
 * Validation rules for data from manifest csv file
 * @constructor
 */
export const manifestValidation = Joi.object({
  "manifest.version": string.valid("1.0").required(),
  "oneroster.version": string.required(),
  "file.academicSessions": string.valid("absent", "bulk", "delta").required(),
  "file.categories": string.valid("absent", "bulk", "delta").required(),
  "file.classes": string.valid("absent", "bulk", "delta").required(),
  "file.classResources": string.valid("absent", "bulk", "delta").required(),
  "file.courses": string.valid("absent", "bulk", "delta").required(),
  "file.courseResources": string.valid("absent", "bulk", "delta").required(),
  "file.demographics": string.valid("absent", "bulk", "delta").required(),
  "file.enrollments": string.valid("absent", "bulk", "delta").required(),
  "file.lineItems": string.valid("absent", "bulk", "delta").required(),
  "file.orgs": string.valid("absent", "bulk", "delta").required(),
  "file.resources": string.valid("absent", "bulk", "delta").required(),
  "file.results": string.valid("absent", "bulk", "delta").required(),
  "file.users": string.valid("absent", "bulk", "delta").required(),
  "source.systemName": string.allow("", null),
  "source.systemCode": string.allow("", null),
  "digitalkoumu.oneroster.version" : Joi.alternatives().try(Joi.string(), Joi.number()).allow("", null),
});

/**
 * Validation rules for data from manifest csv file version 1.2
 * @constructor
 */
export const manifestValidationV12 = Joi.object({
  "manifest.version": string.valid("1.0").required(),
  "oneroster.version": string.required(),
  "file.academicSessions": string.valid("absent", "bulk", "delta").required(),
  "file.categories": string.valid("absent", "bulk", "delta").required(),
  "file.classes": string.valid("absent", "bulk", "delta").required(),
  "file.classResources": string.valid("absent", "bulk", "delta").required(),
  "file.courses": string.valid("absent", "bulk", "delta").required(),
  "file.courseResources": string.valid("absent", "bulk", "delta").required(),
  "file.demographics": string.valid("absent", "bulk", "delta").required(),
  "file.enrollments": string.valid("absent", "bulk", "delta").required(),
  "file.lineItemLearningObjectiveIds": string.valid("absent", "bulk", "delta").required(),
  "file.lineItems": string.valid("absent", "bulk", "delta").required(),
  "file.lineItemScoreScales": string.valid("absent", "bulk", "delta").required(),
  "file.orgs": string.valid("absent", "bulk", "delta").required(),
  "file.resources": string.valid("absent", "bulk", "delta").required(),
  "file.resultLearningObjectiveIds": string.valid("absent", "bulk", "delta").required(),
  "file.results": string.valid("absent", "bulk", "delta").required(),
  "file.resultScoreScales": string.valid("absent", "bulk", "delta").required(),
  "file.roles": string.valid("absent", "bulk", "delta").required(),
  "file.scoreScales": string.valid("absent", "bulk", "delta").required(),
  "file.userProfiles": string.valid("absent", "bulk", "delta").required(),
  "file.userResources": string.valid("absent", "bulk", "delta").required(),
  "file.users": string.valid("absent", "bulk", "delta").required(),
  "source.systemName": string.allow("", null),
  "source.systemCode": string.allow("", null),
  "digitalkoumu.oneroster.version" : Joi.alternatives().try(Joi.string(), Joi.number()).allow("", null),
});

/**
 * Validation rules for data from academicSessions csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const academicSessionsValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    title: string.required().pattern(/^[0-9]{4}年度+$/, { name: "rule" }),
    type: string.valid('schoolYear').required(),
    startDate: date.required(),
    endDate: date.required(),
    parentSourcedId: string.required(),
    schoolYear: year.required(),
  });

/**
 * Validation rules for data from classes csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const classesValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    title: string.required().pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }),
    grades: string.valid('P1','P2','P3','P4','P5','P6','J1','J2','J3','zz','01','02','03','04','05','06','07','08','09','10','H1','H2','H3','H4').allow("", null),
    courseSourcedId: string.required(),
    classCode: string.allow("", null),
    classType: string.valid('homeroom','scheduled','ext:special').required(),
    location: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "rule" }).allow("", null),
    schoolSourcedId: string.required(),
    termSourcedIds: string.required(),
    subjects: string.allow("", null),
    subjectCodes: string.allow("", null),
    periods: string.allow("", null),
    "metadata.jp.specialNeeds": string.valid('true','false').allow("", null),
  });

/**
 * Validation rules for data from courses csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const coursesValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    schoolYearSourcedId: string.allow("", null),
    title: string.required().pattern(/^[0-9]{4}年度[一-龠ぁ-ゔァ-ヴー々〆〤a-zA-Z0-9 ]+$/, { name: "rule" }),
    courseCode: string.valid("").allow(null),
    grades: string.valid('P1','P2','P3','P4','P5','P6','J1','J2','J3','zz','01','02','03','04','05','06','07','08','09','10','H1','H2','H3','H4').allow("", null),
    orgSourcedId: string.required(),
    subjects: string.allow("", null),
    subjectCodes: string.allow("", null),
  });

/**
 * Validation rules for data from enrollments csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const enrollmentValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    classSourcedId: string.required(),
    schoolSourcedId: string.required(),
    userSourcedId: string.required(),
    role: string.valid('administrator','student','teacher','proctor','guardian','districtAdministrator','ext:demonstrator').required(),
    primary: Joi.when('role', {
      is: 'student',
      then: string.valid('false'),
      otherwise: string.valid('true','false')
    }),
    beginDate: date.allow("", null),
    endDate: date.allow("", null),
    "metadata.jp.ShussekiNo": string.allow("", null),
    "metadata.jp.PublicFlg": string.allow("", null)
  });

/**
 * Validation rules for data from orgs csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const orgsValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    name: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "rule" }).required(),
    type: string.valid('department','school','district','local','state','national','ext:technicalCollege').required(),
    identifier: Joi.when('type', {
      is: 'district',
      then: string.valid('A').allow("", null),
      otherwise: string.valid('P','J','PJ','JH','H','U','S','A').allow("", null)
    }),
    parentSourcedId: string.allow("", null)
  });

/**
 * Validation rules for data from users csv file
 * @constructor
 */
/* enum belum di tentukan val nya */
export const usersValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    enabledUser: string.valid('true','false').required(),
    orgSourcedIds: string.required(),
    role: string.valid('administrator','aide','guardian','parent','relative','student','teacher','proctor','districtAdministrator').required(),
    username: string.required(),
    userIds: string.pattern(/^{.*:.*}+$/, { name: "rule" }).allow("", null),
    givenName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    familyName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    middleName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).allow("", null),
    identifier: string.allow("", null),
    email: string.allow("", null),
    sms: string.allow("", null),
    phone: string.allow("", null),
    agentSourcedIds: string.allow("", null),
    grades: string.valid('P1','P2','P3','P4','P5','P6','J1','J2','J3','zz','01','02','03','04','05','06','07','08','09','10','H1','H2','H3','H4').allow("", null),
    password: string.allow("", null),
    "metadata.jp.kanaGivenName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    "metadata.jp.kanaFamilyName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    "metadata.jp.kanaMiddleName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).allow("", null),
    "metadata.jp.homeClass": string.required(),
  });

/**
 * Validation rules for data from users csv file version 1.2
 * @constructor
 */
export const usersValidationV12 = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    enabledUser: string.valid('true','false').required(),
    username: string.required(),
    userIds: string.pattern(/^{.*:.*}+$/, { name: "rule" }).allow("", null),
    givenName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    familyName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    middleName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).allow("", null),
    identifier: string.allow("", null),
    email: string.allow("", null),
    sms: string.allow("", null),
    phone: string.allow("", null),
    agentSourcedIds: string.allow("", null),
    grades: string.valid('P1','P2','P3','P4','P5','P6','J1','J2','J3','zz','01','02','03','04','05','06','07','08','09','10','H1','H2','H3','H4').allow("", null),
    password: string.allow("", null),
    userMasterIdentifier: string.pattern(/^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i, { name: "UUID v4" }).required(),
    resourceSourcedIds: string.allow("", null),
    preferredGivenName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    preferredMiddleName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).allow("", null),
    preferredFamilyName: string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    primaryOrgSourcedId: string.allow("", null),
    pronouns: string.allow("", null),
    "metadata.jp.kanaGivenName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    "metadata.jp.kanaFamilyName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).required(),
    "metadata.jp.kanaMiddleName": string.pattern(/^[ァ-ンa-zA-Z0-9 ]+$/, { name: "Half-width kana" }).allow("", null),
    "metadata.jp.homeClass": string.required()
  });

/**
 * Validation rules for data from roles csv file
 * @constructor
 */
export const rolesValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    userSourcedId: string.required(),
    roleType: string.valid('primary','secondary').required(),
    role: string.valid('student','teacher','administrator','guardian','districtAdministrator','relative','siteAdministrator','principal').required(),
    beginDate: date.allow("", null),
    endDate: date.allow("", null),
    orgSourcedId: string.required(),
    userProfileSourcedId: string.allow("", null)
  });

/**
 * Validation rules for data from demographics csv file
 * @constructor
 */
export const demographicsValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    birthDate: date.allow("", null),
    sex: string.valid('male','female','unspecified','other').allow("", null),
    americanIndianOrAlaskaNative: string.valid('true','false').allow("", null),
    asian: string.valid('true','false').allow("", null),
    blackOrAfricanAmerican: string.valid('true','false').allow("", null),
    nativeHawaiianOrOtherPacificIslander: string.valid('true','false').allow("", null),
    white: string.valid('true','false').allow("", null),
    demographicRaceTwoOrMoreRaces: string.valid('true','false').allow("", null),
    hispanicOrLatinoEthnicity: string.valid('true','false').allow("", null),
    countryOfBirthCode: string.allow("", null),
    stateOfBirthAbbreviation: string.allow("", null),
    cityOfBirth: string.allow("", null),
    publicSchoolResidenceStatus: string.allow("", null)
  });

/**
 * Validation rules for data from userProfiles csv file
 * @constructor
 */
export const userProfilesValidation = (type) =>
  Joi.object({
    sourcedId: string.required(),
    status: type === "delta" ? string.valid('active','tobedeleted').required() : string.valid('active','tobedeleted').allow("", null),
    dateLastModified: type === "delta" ? date.format().iso().required() : date.format().iso().allow("", null),
    userSourcedId: string.required(),
    profileType: string.required(),
    vendorId: string.required(),
    applicationId: string.allow("", null),
    description: string.allow("", null),
    credentialType: string.required(),
    username: string.required(),
    password: string.allow("", null)
  });
