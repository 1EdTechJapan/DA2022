// OneRoster csv のヘッダー一覧
module.exports.headers = {
    academicSessions: ["sourcedId", "status", "dateLastModified", "title", "type", "startDate", "endDate", "parentSourcedId", "schoolYear"],
    classes: ["sourcedId", "status", "dateLastModified", "title", "grades", "courseSourcedId", "classCode", "classType", "location", "schoolSourcedId", "termSourcedIds", "subjects", "subjectCodes", "periods"],
    courses: ["sourcedId", "status", "dateLastModified", "schoolYearSourcedId", "title", "courseCode", "grades", "orgSourcedId", "subjects", "subjectCodes"],
    enrollments: ["sourcedId", "status", "dateLastModified", "classSourcedId", "schoolSourcedId", "userSourcedId", "role", "primary", "beginDate", "endDate"],
    orgs: ["sourcedId", "status", "dateLastModified", "name", "type", "identifier", "parentSourcedId"],
    roles: ["sourcedId", "status", "dateLastModified", "userSourcedId", "roleType", "role", "beginDate", "endDate", "orgSourcedId", "userProfileSourcedId"],
    users: ["sourcedId", "status", "dateLastModified", "enabledUser", "username", "userIds", "givenName", "familyName", "middleName", "identifier", "email", "sms", "phone", "agentSourcedIds", "grades", "password", "userMasterIdentifier", "resourceSourcedIds", "preferredGivenName", "preferredMiddleName", "preferredFamilyName", "primaryOrgSourcedId", "pronouns"]
}

// OneRoster csv の必須項目
module.exports.requiredHeader = {
    academicSessions: ["sourcedId", "title", "type", "startDate", "endDate", "schoolYear"],
    classes: ["sourcedId", "title", "courseSourcedId", "classType", "schoolSourcedId", "termSourcedIds"],
    courses: ["sourcedId", "title", "orgSourcedId"],
    enrollments: ["sourcedId", "classSourcedId", "schoolSourcedId", "userSourcedId", "role"],
    orgs: ["sourcedId", "name", "type"],
    roles: ["sourcedId", "userSourcedId", "roleType", "role", "orgSourcedId"],
    users: ["sourcedId", "enabledUser", "username", "givenName", "familyName"]   
}

// システムにデータ登録するうえで必須のもの
module.exports.requiredForMyApp = {
    users: ["password"]        
}