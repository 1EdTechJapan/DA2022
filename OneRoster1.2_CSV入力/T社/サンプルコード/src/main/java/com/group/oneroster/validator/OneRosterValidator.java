package com.flakworks.oneroster.validator;

import com.flakworks.oneroster.persistence.domain.FileErrorEntity;
import com.flakworks.oneroster.service.dto.Role;
import com.opencsv.CSVParser;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.opencsv.exceptions.CsvValidationException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class OneRosterValidator {

    private final String[] USERS_CSV_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "enabledUser", "username", "userIds", "givenName", "familyName", "middleName", "identifier", "email", "sms", "phone", "agentSourcedIds", "grades", "password", "userMasterIdentifier", "resourceSourcedIds", "preferredGivenName", "preferredMiddleName", "preferredFamilyName", "primaryOrgSourcedId", "pronouns", "metadata.jp.kanaGivenName", "metadata.jp.kanaFamilyName", "metadata.jp.kanaMiddleName", "metadata.jp.homeClass"};
    private final String[] ACADEMIC_SESSIONS_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "title", "type", "startDate", "endDate", "parentSourcedId", "schoolYear"};
    private final String[] CLASS_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "title", "grades", "courseSourcedId", "classCode", "classType", "location", "schoolSourcedId", "termSourcedIds", "subjects", "subjectCodes", "periods", "metadata.jp.specialNeeds"};
    private static final Set<String> PERMITTED_STATUSES = new HashSet<>(Arrays.asList("active", "tobedeleted"));
    private static final Set<String> PERMITTED_ACADEMIC_SESSION_TYPES = new HashSet<>(List.of("schoolYear"));
    private static final Set<String> PERMITTED_CLASS_TYPES = new HashSet<>(Arrays.asList("homeroom", "scheduled"));
    private static final Set<String> PERMITTED_ORG_TYPES = new HashSet<>(Arrays.asList("department", "school", "district", "local", "state", "national"));
    private static final Set<String> PERMITTED_SEX = new HashSet<>(Arrays.asList("male", "female", "unspecified", "other"));
    private static final Set<String> PERMITTED_ROLES = new HashSet<>(Arrays.asList("administrator", "proctor", "student", "teacher"));
    private static final Set<String> PERMITTED_ROLES_TYPES = new HashSet<>(Arrays.asList("primary", "secondary"));
    private static final Set<String> PERMITTED_ROLES_VALUES = new HashSet<>(Arrays.asList("districtAdministrator", "guardian", "principal", "proctor", "siteAdministrator", "student", "systemAdministrator", "teacher"));
    private static final Set<String> PERMITTED_SUBJECT_CODES = new HashSet<>(Arrays.asList("P010", "P020", "P030", "P040", "P050", "P060", "P070", "P080", "P090", "P100", "J010", "J020", "J030", "J040", "J050", "J060", "J070", "J080", "J090"));
    private static final Set<String> PERMITTED_GRADES = new HashSet<>(Arrays.asList("P1", "P2", "P3", "P4", "P5", "P6", "J1", "J2", "J3"));
    private static final Set<String> BOOLEAN = new HashSet<>(Arrays.asList("true", "false"));
    private static final String JAPAN_YEAR_REGEX = "\\d{4}年度";
    private static final String COURSE_TITLE_REGEX = "\\d{4}年度.*";
    private static final String COURSE_TITLE_REGEX1 = "^[\\d{4}年度]+[ァ-ヶーァ-ヶー 0-9]+$";
    private static final String DATE_TIME_REGEX = "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d{1,9})?[+-]\\d{2}:\\d{2}$";
    private static final String DATE_REGEX = "^\\d{4}-\\d{2}-\\d{2}$";
    private static final String YEAR_REGEX = "^(19|20)\\d{2}$";
    private static final String GUID_REGEX = "^(?:\\{{0,1}(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\\}{0,1})$";
    private static final String UUIDV4_REGEX = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$";
    private static final String ORG_IDENTIFIER_REGEX = "^([A-Z]\\d{12}|\\d{6})$";
    private static final String FULL_WIDTH_KATAKANA_REGEX = "^[ぁ-んァ-ンa-zA-Z 0-9]+$";
    private static final String USER_IDS_REGEX = "^\\{((Koumu|MS|Google|Apple|AD):)?\\d+\\}(,\\{((Koumu|MS|Google|Apple|AD):)?\\d+\\})*$";
    //    private static final String HALF_WIDTH_KATAKANA_REGEX = "^[\\uFF65-\\uFF9F]+$";
    private static final String LOCATION_CLASS_REGEX = "[\uFF61-\uFF9F]+(都|道|府|県)(市|区|町|村)";
    private static final String BOLEAN_REGEX = "^(true|false)$";
    private static final String[] COURSES_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "schoolYearSourcedId", "title", "courseCode", "grades", "orgSourcedId", "subjects", "subjectCodes"};
    private static final String[] DEMOGRAPHICS_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "birthDate", "sex", "americanIndianOrAlaskaNative", "asian", "blackOrAfricanAmerican", "nativeHawaiianOrOtherPacificIslander", "white", "demographicRaceTwoOrMoreRaces", "hispanicOrLatinoEthnicity", "countryOfBirthCode", "stateOfBirthAbbreviation", "cityOfBirth", "publicSchoolResidenceStatus"};
    private static final String[] ENROLLMENTS_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "classSourcedId", "schoolSourcedId", "userSourcedId", "role", "primary", "beginDate", "endDate", "metadata.jp.ShussekiNo", "metadata.jp.PublicFlg"};
    private static final String[] ORGS_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "name", "type", "identifier", "parentSourcedId"};
    private static final String[] ROLES_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "userSourcedId", "roleType", "role", "beginDate", "endDate", "orgSourcedId", "userProfileSourcedId"};
    private static final String[] USER_PROFILES_EXPECTED_HEADERS = {"sourcedId", "status", "dateLastModified", "userSourcedId", "profileType", "vendorId", "applicationId", "description", "credentialType", "username", "password"};


    private final CSVParser csvParser;
    public void validator(File file, List<FileErrorEntity> errors, String mode, String fileName) throws CsvValidationException, IOException {
        switch (fileName) {
            case "users.csv":
                if (validateHeader(file, errors, USERS_CSV_EXPECTED_HEADERS, "users"))
                    validateContentUsers(file, errors, mode);
                break;
            case "academicSessions.csv":
                if (validateHeader(file, errors, ACADEMIC_SESSIONS_EXPECTED_HEADERS, "academicSessions"))
                    validateContentAcademicSessions(file, errors, mode);
                break;
            case "classes.csv":
                if (validateHeader(file, errors, CLASS_EXPECTED_HEADERS, "classes"))
                    validateContentClasses(file, errors, mode);
                break;
            case "courses.csv":
                if (validateHeader(file, errors, COURSES_EXPECTED_HEADERS, "courses"))
                    validateContentCourses(file, errors, mode);
                break;
            case "demographics.csv":
                if (validateHeader(file, errors, DEMOGRAPHICS_EXPECTED_HEADERS, "demographics"))
                    validateContentDemographics(file, errors, mode);
                break;
            case "enrollments.csv":
                if (validateHeader(file, errors, ENROLLMENTS_EXPECTED_HEADERS, "enrollments"))
                    validateContentEnrollments(file, errors, mode);
                break;
            case "orgs.csv":
                if (validateHeader(file, errors, ORGS_EXPECTED_HEADERS, "orgs"))
                    validateContentOrgs(file, errors, mode);

                break;
            case "roles.csv":
                if (validateHeader(file, errors, ROLES_EXPECTED_HEADERS, "roles"))
                    validateContentRoles(file, errors, mode);

                break;
            case "userProfiles.csv":
                if (validateHeader(file, errors, USER_PROFILES_EXPECTED_HEADERS, "userProfiles"))
                    validateContentUserProfiles(file, errors, mode);

                break;
            default:


        }
    }

    private void validateContentUserProfiles(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int userSourcedIdIndex = Arrays.asList(header).indexOf("userSourcedId");
            int profileTypeIndex = Arrays.asList(header).indexOf("profileType");
            int vendorIdIndex = Arrays.asList(header).indexOf("vendorId");
            int credentialTypeIndex = Arrays.asList(header).indexOf("credentialType");
            int usernameIndex = Arrays.asList(header).indexOf("username");
            int descriptionIndex = Arrays.asList(header).indexOf("description");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String userSourcedId = line[userSourcedIdIndex];
                String profileType = line[profileTypeIndex];
                String vendorId = line[vendorIdIndex];
                String credentialType = line[credentialTypeIndex];
                String username = line[usernameIndex];
                String description = line[descriptionIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "userProfiles");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "userProfiles");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "userProfiles");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "userProfiles");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "userProfiles");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "userProfiles");
                }

                validateGUID("userSourcedId", userSourcedId, sourcedId, lineNumber, errors, "userProfiles");

                validateRequiredField("profileType", profileType, lineNumber, errors, "userProfiles");
                validateRequiredField("vendorId", vendorId, lineNumber, errors, "userProfiles");
                validateRequiredField("credentialType", credentialType, lineNumber, errors, "userProfiles");
                validateRequiredField("username", username, lineNumber, errors, "userProfiles");

                if (description != null && !description.isBlank() && !description.equalsIgnoreCase("null")) {
                    if (!description.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid description value: %s for userProfiles with sourcedId %s", description, sourcedId);
                        errors.add(createFileErrorEntity("description", message, lineNumber, "userProfiles"));
                        log.error(message);
                    }
                }

            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void validateContentRoles(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int userSourcedIdIndex = Arrays.asList(header).indexOf("userSourcedId");
            int roleTypeIndex = Arrays.asList(header).indexOf("roleType");
            int roleIndex = Arrays.asList(header).indexOf("role");
            int beginDateIndex = Arrays.asList(header).indexOf("beginDate");
            int endDateIndex = Arrays.asList(header).indexOf("endDate");
            int orgSourcedIdIndex = Arrays.asList(header).indexOf("orgSourcedId");
            int userProfileSourcedIdIndex = Arrays.asList(header).indexOf("userProfileSourcedId");

            List<Role> roles = new ArrayList<>();

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String userSourcedId = line[userSourcedIdIndex];
                String roleType = line[roleTypeIndex];
                String role = line[roleIndex];
                String beginDate = line[beginDateIndex];
                String endDate = line[endDateIndex];
                String orgSourcedId = line[orgSourcedIdIndex];
                String userProfileSourcedId = line[userProfileSourcedIdIndex];

                roles.add(new Role(userSourcedId, role, roleType));
                validateSourcedId(sourcedId, lineNumber, errors, "roles");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "roles");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "roles");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "roles");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "roles");
                }
                validateGUID("userSourcedId", userSourcedId, sourcedId, lineNumber, errors, "roles");

                if (roleType == null || roleType.isEmpty()) {
                    errors.add(createFileErrorEntity("roleType", roleType, lineNumber, "roles"));
                } else {
                    validateEnumeration("roleType", roleType, PERMITTED_ROLES_TYPES, sourcedId, lineNumber, errors, "roles");
                }

                if (role == null || role.isEmpty()) {
                    errors.add(createFileErrorEntity("role", role, lineNumber, "roles"));
                } else {
                    validateEnumeration("role", role, PERMITTED_ROLES_VALUES, sourcedId, lineNumber, errors, "roles");
                }

                if (beginDate != null && !beginDate.isEmpty())
                    validateDate(beginDate, "beginDate", sourcedId, lineNumber, errors, "roles");

                if (endDate != null && !endDate.isEmpty())
                    validateDate(endDate, "endDate", sourcedId, lineNumber, errors, "roles");

                validateGUID("orgSourcedId", orgSourcedId, sourcedId, lineNumber, errors, "roles");

                if (userProfileSourcedId != null && !userProfileSourcedId.isEmpty())
                    validateGUID("userProfileSourcedId", userProfileSourcedId, sourcedId, lineNumber, errors, "roles");

            }

            AtomicInteger lineNumber1 = new AtomicInteger(1);
            roles.forEach(role -> {
                if ((role.getRole().equals("districtAdministrator") && role.getRoleType().equals("secondary"))
                        || (role.getRole().equals("siteAdministrator") && role.getRoleType().equals("secondary"))
                        || (role.getRole().equals("principal") && role.getRoleType().equals("secondary"))
                        && !validRole(roles, role.getId())) {
                    String message = String.format("Invalid role, roleType value: %s, %s because missing role teacher and roleType primary", role.getRole(), role.getRoleType());
                    errors.add(createFileErrorEntity("role", message, lineNumber1.get(), "roles"));
                    lineNumber1.getAndIncrement();
                    log.error(message);
                }
            });


        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private boolean validRole(List<Role> roles, String id) {
        return roles.stream()
                .anyMatch(role -> role.getId().equals(id) && role.getRole().equals("teacher") && role.getRoleType().equals("primary"));
    }


    private void validateContentOrgs(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int nameIndex = Arrays.asList(header).indexOf("name");
            int typeIndex = Arrays.asList(header).indexOf("type");
            int parentSourcedIdIndex = Arrays.asList(header).indexOf("parentSourcedId");
            int identifierIndex = Arrays.asList(header).indexOf("identifier");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String name = line[nameIndex];
                String type = line[typeIndex];
                String parentSourcedId = line[parentSourcedIdIndex];
                String identifier = line[identifierIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "orgs");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "orgs");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "orgs");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "orgs");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "orgs");
                }

                if (validateRequiredField("name", name, lineNumber, errors, "orgs")) {
                    if (!name.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid name value: %s for orgs with sourcedId %s", name, sourcedId);
                        errors.add(createFileErrorEntity("name", message, lineNumber, "orgs"));
                        log.error(message);
                    }
                }

                if (type == null || type.isBlank()) {
                    errors.add(createFileErrorEntity("type", "There is no value found for field: " + "type", lineNumber, "orgs"));
                } else {
                    validateEnumeration("type", type, PERMITTED_ORG_TYPES, sourcedId, lineNumber, errors, "orgs");
                }
                if (!"district".equalsIgnoreCase(type) && parentSourcedId != null && !parentSourcedId.isBlank() && !parentSourcedId.equalsIgnoreCase("null"))
                    validateGUID("parentSourcedId", parentSourcedId, sourcedId, lineNumber, errors, "orgs");

                if ("district".equalsIgnoreCase(type) && !"null".equalsIgnoreCase(parentSourcedId) && !parentSourcedId.isBlank()) {
                    String message = String.format("Invalid parentSourcedId value: %s for orgs with sourcedId %s", parentSourcedId, sourcedId);
                    errors.add(createFileErrorEntity("parentSourcedId", message, lineNumber, "orgs"));
                    log.error(message);
                }

                if (identifier != null && !identifier.isBlank() && !identifier.matches(ORG_IDENTIFIER_REGEX)) {
                    String message = String.format("Invalid identifier value: %s for orgs with sourcedId %s", identifier, sourcedId);
                    errors.add(createFileErrorEntity("identifier", message, lineNumber, "orgs"));
                    log.error(message);
                }

            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void validateContentEnrollments(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int classSourcedIdIndex = Arrays.asList(header).indexOf("classSourcedId");
            int schoolSourcedIdIndex = Arrays.asList(header).indexOf("schoolSourcedId");
            int userSourcedIdIndex = Arrays.asList(header).indexOf("userSourcedId");
            int roleIndex = Arrays.asList(header).indexOf("role");
            int primaryIndex = Arrays.asList(header).indexOf("primary");
            int beginDateIndex = Arrays.asList(header).indexOf("beginDate");
            int endDateIndex = Arrays.asList(header).indexOf("endDate");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String classSourcedId = line[classSourcedIdIndex];
                String schoolSourcedId = line[schoolSourcedIdIndex];
                String userSourcedId = line[userSourcedIdIndex];
                String role = line[roleIndex];
                String primary = line[primaryIndex];
                String beginDate = line[beginDateIndex];
                String endDate = line[endDateIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "enrollments");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "enrollments");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "enrollments");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "enrollments");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "enrollments");
                }

                validateGUID("classSourcedId", classSourcedId, sourcedId, lineNumber, errors, "enrollments");
                validateGUID("schoolSourcedId", schoolSourcedId, sourcedId, lineNumber, errors, "enrollments");
                validateGUID("userSourcedId", userSourcedId, sourcedId, lineNumber, errors, "enrollments");
                if (role == null || role.isBlank()) {
                    errors.add(createFileErrorEntity("role", "There is no value found for field: " + "role", lineNumber, "enrollments"));
                } else {
                    validateEnumeration("role", role, PERMITTED_ROLES, sourcedId, lineNumber, errors, "enrollments");
                    if (role.equalsIgnoreCase("student") && primary.equals("true")) {
                        errors.add(createFileErrorEntity("role", "Role is student but primary true", lineNumber, "enrollments"));
                    }
                }
                if (primary == null || primary.isBlank()) {
                    errors.add(createFileErrorEntity("primary", "There is no value found for field: " + "primary", lineNumber, "enrollments"));
                } else {
                    validateEnumeration("primary", primary, BOOLEAN, sourcedId, lineNumber, errors, "enrollments");
                }
                if (beginDate != null && !beginDate.isBlank())
                    validateDate(beginDate, "beginDate", sourcedId, lineNumber, errors, "enrollments");
                if (endDate != null && !endDate.isBlank())
                    validateDate(endDate, "endDate", sourcedId, lineNumber, errors, "enrollments");

            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void validateContentDemographics(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int birthDateIndex = Arrays.asList(header).indexOf("birthDate");
            int sexIndex = Arrays.asList(header).indexOf("sex");
            int americanIndianOrAlaskaNativeIndex = Arrays.asList(header).indexOf("americanIndianOrAlaskaNative");
            int asianIndex = Arrays.asList(header).indexOf("asian");
            int blackOrAfricanAmericanIndex = Arrays.asList(header).indexOf("blackOrAfricanAmerican");
            int nativeHawaiianOrOtherPacificIslanderIndex = Arrays.asList(header).indexOf("nativeHawaiianOrOtherPacificIslander");
            int whiteIndex = Arrays.asList(header).indexOf("white");
            int demographicRaceTwoOrMoreRacesIndex = Arrays.asList(header).indexOf("demographicRaceTwoOrMoreRaces");
            int hispanicOrLatinoEthnicityIndex = Arrays.asList(header).indexOf("hispanicOrLatinoEthnicity");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String birthDate = line[birthDateIndex];
                String sex = line[sexIndex];
                String americanIndianOrAlaskaNative = line[americanIndianOrAlaskaNativeIndex];
                String asian = line[asianIndex];
                String blackOrAfricanAmerican = line[blackOrAfricanAmericanIndex];
                String nativeHawaiianOrOtherPacificIslander = line[nativeHawaiianOrOtherPacificIslanderIndex];
                String white = line[whiteIndex];
                String demographicRaceTwoOrMoreRaces = line[demographicRaceTwoOrMoreRacesIndex];
                String hispanicOrLatinoEthnicity = line[hispanicOrLatinoEthnicityIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "demographics");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "demographics");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "demographics");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "demographics");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "demographics");
                }

                if (birthDate != null && !birthDate.isBlank())
                    validateDate(birthDate, "birthDate", sourcedId, lineNumber, errors, "demographics");
                if (sex != null && !sex.isBlank())
                    validateEnumeration("sex", sex, PERMITTED_SEX, sourcedId, lineNumber, errors, "demographics");
                if (americanIndianOrAlaskaNative != null && !americanIndianOrAlaskaNative.isBlank())
                    validateEnumeration("americanIndianOrAlaskaNative", americanIndianOrAlaskaNative, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (asian != null && !asian.isBlank())
                    validateEnumeration("asian", asian, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (blackOrAfricanAmerican != null && !blackOrAfricanAmerican.isBlank())
                    validateEnumeration("blackOrAfricanAmerican", blackOrAfricanAmerican, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (nativeHawaiianOrOtherPacificIslander != null && !nativeHawaiianOrOtherPacificIslander.isBlank())
                    validateEnumeration("nativeHawaiianOrOtherPacificIslander", nativeHawaiianOrOtherPacificIslander, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (white != null && !white.isBlank())
                    validateEnumeration("white", white, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (demographicRaceTwoOrMoreRaces != null && !demographicRaceTwoOrMoreRaces.isBlank())
                    validateEnumeration("demographicRaceTwoOrMoreRaces", demographicRaceTwoOrMoreRaces, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
                if (hispanicOrLatinoEthnicity != null && !hispanicOrLatinoEthnicity.isBlank())
                    validateEnumeration("hispanicOrLatinoEthnicity", hispanicOrLatinoEthnicity, BOOLEAN, sourcedId, lineNumber, errors, "demographics");
            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void validateEnumeration(String key, String value, Set<String> permittedSet, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (!permittedSet.contains(value)) {
            String message = String.format("Invalid %s value: %s with sourcedId %s", key, value, sourcedId);
            errors.add(createFileErrorEntity(key, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateContentCourses(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int titleIndex = Arrays.asList(header).indexOf("title");
            int orgSourcedIdIndex = Arrays.asList(header).indexOf("orgSourcedId");
            int schoolYearSourcedIdIndex = Arrays.asList(header).indexOf("schoolYearSourcedId");
            int subjectCodesIndex = Arrays.asList(header).indexOf("subjectCodes");
            int courseCodeIndex = Arrays.asList(header).indexOf("courseCode");
            int gradesIndex = Arrays.asList(header).indexOf("grades");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String title = line[titleIndex];
                String orgSourcedId = line[orgSourcedIdIndex];
                String schoolYearSourcedId = line[schoolYearSourcedIdIndex];
                String subjectCodes = line[subjectCodesIndex];
                String courseCode = line[courseCodeIndex];
                String grades = line[gradesIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "courses");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "courses");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "courses");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "courses");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "courses");
                }
//                validateTitle(title, sourcedId, lineNumber, errors, "courses");
                validateGUID("orgSourcedId", orgSourcedId, sourcedId, lineNumber, errors, "courses");

                if (schoolYearSourcedId != null && !schoolYearSourcedId.isBlank() && !schoolYearSourcedId.matches(GUID_REGEX)) {
                    String message = String.format("Invalid schoolYearSourcedId value: %s", schoolYearSourcedId);
                    errors.add(createFileErrorEntity("schoolYearSourcedId", message, lineNumber, "courses"));
                    log.error(message);
                }

                if (subjectCodes != null && !subjectCodes.isBlank()) {
                    String[] subjectCodeList = subjectCodes.split(",");
                    if (!PERMITTED_SUBJECT_CODES.containsAll(List.of(subjectCodeList))) {
                        String message = String.format("Invalid subjectCode value: %s", subjectCodes);
                        errors.add(createFileErrorEntity("subjectCode", message, lineNumber, "courses"));
                        log.error(message);
                    }
                }

                if (title == null || title.isBlank()) {
                    String message = String.format("There is no value found for field: title for classes with sourcedId %s", sourcedId);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "courses"));
                    log.error(message);
                } else if (!title.matches(COURSE_TITLE_REGEX1)) {
                    String message = String.format("Invalid title value: %s", title);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "courses"));
                    log.error(message);
                }

                if (courseCode == null || !courseCode.isBlank()) {
                    String message = String.format("Invalid courseCode value: %s", courseCode);
                    errors.add(createFileErrorEntity("courseCode", message, lineNumber, "courses"));
                    log.error(message);
                }
                if (grades != null && !grades.isBlank()) {
                    String[] gradeList = grades.split(",");
                    if (!PERMITTED_GRADES.containsAll(List.of(gradeList))) {
                        String message = String.format("Invalid grades value: %s", grades);
                        errors.add(createFileErrorEntity("grades", message, lineNumber, "courses"));
                        log.error(message);
                    }
                }

            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }

    }

    private void validateContentClasses(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReader(new FileReader(file))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int titleIndex = Arrays.asList(header).indexOf("title");
            int courseSourcedIdIndex = Arrays.asList(header).indexOf("courseSourcedId");
            int classTypeIndex = Arrays.asList(header).indexOf("classType");
            int schoolSourcedIdIndex = Arrays.asList(header).indexOf("schoolSourcedId");
            int termSourcedIdsIndex = Arrays.asList(header).indexOf("termSourcedIds");
            int metadataJpSpecialNeedsIndex = Arrays.asList(header).indexOf("metadata.jp.specialNeeds");
            int locationIndex = Arrays.asList(header).indexOf("location");
            int subjectCodesIndex = Arrays.asList(header).indexOf("subjectCodes");
            int gradesIndex = Arrays.asList(header).indexOf("grades");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String title = line[titleIndex];
                String courseSourcedId = line[courseSourcedIdIndex];
                String classType = line[classTypeIndex];
                String schoolSourcedId = line[schoolSourcedIdIndex];
                String termSourcedIds = line[termSourcedIdsIndex];
                String metadataJpSpecialNeeds = line[metadataJpSpecialNeedsIndex];
                String location = line[locationIndex];
                String subjectCodes = line[subjectCodesIndex];
                String grades = line[gradesIndex];

                validateSourcedId(sourcedId, lineNumber, errors, "classes");
                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "classes");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "classes");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "classes");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "classes");
                }
//                validateTitle(title, sourcedId, lineNumber, errors, "classes");
                if (title == null || title.isBlank()) {
                    String message = String.format("There is no value found for field: title for classes with sourcedId %s", sourcedId);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "classes"));
                    log.error(message);
                } else if (!title.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                    String message = String.format("Invalid title value: %s", title);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "classes"));
                    log.error(message);
                }
                validateCourseSourcedId(courseSourcedId, lineNumber, errors, "classes");
                validateClassType(classType, sourcedId, lineNumber, errors, "classes");
                validateGUID("schoolSourcedId", schoolSourcedId, sourcedId, lineNumber, errors, "classes");
//                validateRequiredField("termSourcedIds", termSourcedIds, lineNumber, errors, "classes");
                validateGUID("termSourcedIds", termSourcedIds, sourcedId, lineNumber, errors, "classes");
                if (metadataJpSpecialNeeds != null && !metadataJpSpecialNeeds.isBlank() && !metadataJpSpecialNeeds.matches(BOLEAN_REGEX)) {
                    String message = String.format("Invalid metadata.jp.specialNeeds value: %s", metadataJpSpecialNeeds);
                    errors.add(createFileErrorEntity("metadata.jp.specialNeeds", message, lineNumber, "classes"));
                    log.error(message);
                }
                if (location != null && !location.isBlank() && !location.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                    String message = String.format("Invalid location value: %s", location);
                    errors.add(createFileErrorEntity("location", message, lineNumber, "classes"));
                    log.error(message);
                }

                if (subjectCodes != null && !subjectCodes.isBlank()) {
                    String[] subjectCodeList = subjectCodes.split(",");
                    if (!PERMITTED_SUBJECT_CODES.containsAll(List.of(subjectCodeList))) {
                        String message = String.format("Invalid subjectCode value: %s", subjectCodes);
                        errors.add(createFileErrorEntity("subjectCode", message, lineNumber, "classes"));
                        log.error(message);
                    }
                }

                if (grades != null && !grades.isBlank()) {
                    String[] gradeList = grades.split(",");
                    if (!PERMITTED_GRADES.containsAll(List.of(gradeList))) {
                        String message = String.format("Invalid grades value: %s", grades);
                        errors.add(createFileErrorEntity("grades", message, lineNumber, "classes"));
                        log.error(message);
                    }
                }

            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void validateGUID(String fieldName, String fieldValue, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (fieldValue == null || fieldValue.isBlank()) {
            errors.add(createFileErrorEntity(fieldName, "There is no value found for field: " + fieldName, lineNumber, fileCsvName));
        } else if (!"null".equalsIgnoreCase(fieldValue) && !fieldValue.matches(GUID_REGEX)) {
            String message = String.format("Invalid %s value: %s with line %d", fieldName, fieldValue, lineNumber);
            errors.add(createFileErrorEntity(fieldName, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateContentAcademicSessions(File file, List<FileErrorEntity> errors, String mode) {
        try (CSVReader reader = new CSVReaderBuilder(new FileReader(file)).withCSVParser(csvParser).withKeepCarriageReturn(false).build()) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int titleIndex = Arrays.asList(header).indexOf("title");
            int typeIndex = Arrays.asList(header).indexOf("type");
            int startDateIndex = Arrays.asList(header).indexOf("startDate");
            int endDateIndex = Arrays.asList(header).indexOf("endDate");
            int schoolYearIndex = Arrays.asList(header).indexOf("schoolYear");
            int parentSourcedIdIndex = Arrays.asList(header).indexOf("parentSourcedId");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                validate(line, lineNumber, errors);
                String sourcedId = line[sourcedIdIndex].replace("\"", "");
                String status = line[statusIndex].replace("\"", "");
                String dateLastModified = line[dateLastModifiedIndex].replace("\"", "");
                String title = line[titleIndex].replace("\"", "");
                String type = line[typeIndex].replace("\"", "");
                String startDate = line[startDateIndex].replace("\"", "");
                String endDate = line[endDateIndex].replace("\"", "");
                String schoolYear = line[schoolYearIndex].replace("\"", "");
                String parentSourcedId = line[parentSourcedIdIndex].replace("\"", "");

                validateSourcedId(sourcedId, lineNumber, errors, "academicSessions");

                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "academicSessions");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "academicSessions");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "academicSessions");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "academicSessions");
                }
                log.info("title xxxxxxx: " + title);
                if (title == null || title.isBlank()) {
                    String message = String.format("There is no value found for field: title for academicSession with sourcedId %s", sourcedId);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "academicSessions"));
                    log.error(message);
                } else if (!title.matches(JAPAN_YEAR_REGEX)) {
                    String message = String.format("Invalid value for title: %s", title);
                    errors.add(createFileErrorEntity("title", message, lineNumber, "academicSessions"));
                    log.error(message);
                }


                validateType(type, sourcedId, lineNumber, errors, "academicSessions");
                validateDate(startDate, "startDate", sourcedId, lineNumber, errors, "academicSessions");
                validateDate(endDate, "endDate", sourcedId, lineNumber, errors, "academicSessions");
                validateSchoolYear(schoolYear, sourcedId, lineNumber, errors, "academicSessions");

                validateGUID("parentSourcedId", parentSourcedId, sourcedId, lineNumber, errors, "academicSessions");
            }
        } catch (CsvValidationException | IOException e) {
            throw new RuntimeException(e);
        }
    }

    private boolean validate(String[] line, int lineNumber, List<FileErrorEntity> errors) {
        boolean isValid = true;
        for (String field : line) {
            if (field.length() > 1 && field.charAt(0) == '"' && field.charAt(field.length() - 1) == '"') {
                isValid &= true;
            } else {
                isValid = false;
                String message = String.format("Field value invalid, data is not in quotes value: %s, line: %s", field, lineNumber);
                errors.add(createFileErrorEntity("title", message, lineNumber, "academicSessions"));
                log.error(message);
            }
        }
        return isValid;
    }

    private void validateDateLastModifiedBulkMode(String dateLastModified, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (dateLastModified != null && !dateLastModified.isBlank()) {
            errors.add(createFileErrorEntity("dateLastModified", "The file is being processed as BULK. As a result, there should be no value for the following field: dateLastModified", lineNumber, fileCsvName));
        }
    }

    private void validateStatusBulkMode(String status, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (status != null && !status.isBlank()) {
            errors.add(createFileErrorEntity("status", "The file is being processed as BULK. As a result, there should be no value for the following field: status", lineNumber, fileCsvName));
        }
    }

    private void validateContentUsers(File userfile, List<FileErrorEntity> errors, String mode) throws IOException, CsvValidationException {
        try (CSVReader reader = new CSVReader(new FileReader(userfile))) {
            String[] header = reader.readNext();
            Set<String> userMasterIdentifierValues = new HashSet<String>();

            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int statusIndex = Arrays.asList(header).indexOf("status");
            int dateLastModifiedIndex = Arrays.asList(header).indexOf("dateLastModified");
            int enabledUserIndex = Arrays.asList(header).indexOf("enabledUser");
            int usernameIndex = Arrays.asList(header).indexOf("username");
            int givenNameIndex = Arrays.asList(header).indexOf("givenName");
            int familyNameIndex = Arrays.asList(header).indexOf("familyName");
            int preferredGivenNameIndex = Arrays.asList(header).indexOf("preferredGivenName");
            int preferredFamilyNameIndex = Arrays.asList(header).indexOf("preferredFamilyName");
            int userMasterIdentifierIndex = Arrays.asList(header).indexOf("userMasterIdentifier");
            int metadataJpKanaGivenNameIndex = Arrays.asList(header).indexOf("metadata.jp.kanaGivenName");
            int metadataJpKanaFamilyNameIndex = Arrays.asList(header).indexOf("metadata.jp.kanaFamilyName");
            int metadataJpHomeClassIndex = Arrays.asList(header).indexOf("metadata.jp.homeClass");
            int userIdsIndex = Arrays.asList(header).indexOf("userIds");
            int primaryOrgSourcedIdIndex = Arrays.asList(header).indexOf("primaryOrgSourcedId");
            int middleNameIndex = Arrays.asList(header).indexOf("middleName");
            int preferredMiddleNameIndex = Arrays.asList(header).indexOf("preferredMiddleName");
            int gradesIndex = Arrays.asList(header).indexOf("grades");
            int metadataJpKanaMiddleNameIndex = Arrays.asList(header).indexOf("metadata.jp.kanaMiddleName");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String status = line[statusIndex];
                String dateLastModified = line[dateLastModifiedIndex];
                String enabledUser = line[enabledUserIndex];
                String username = line[usernameIndex];
                String givenName = line[givenNameIndex];
                String familyName = line[familyNameIndex];
                String preferredGivenName = line[preferredGivenNameIndex];
                String preferredFamilyName = line[preferredFamilyNameIndex];
                String userMasterIdentifier = line[userMasterIdentifierIndex];
                String metadataJpKanaGivenName = line[metadataJpKanaGivenNameIndex];
                String metadataJpKanaFamilyName = line[metadataJpKanaFamilyNameIndex];
                String metadataJpHomeClass = line[metadataJpHomeClassIndex];
                String userIds = line[userIdsIndex];
                String primaryOrgSourcedId = line[primaryOrgSourcedIdIndex];
                String middleName = line[middleNameIndex];
                String preferredMiddleName = line[preferredMiddleNameIndex];
                String grades = line[gradesIndex];
                String metadataJpKanaMiddleName = line[metadataJpKanaMiddleNameIndex];

                if (!userMasterIdentifierValues.add(userMasterIdentifier)) {
                    String message = String.format("Duplicated userMasterIdentifier value: %s for user with sourcedId %s", userMasterIdentifier, sourcedId);
                    errors.add(createFileErrorEntity("userMasterIdentifier", message, lineNumber, "users"));
                    log.error(message);
                }

                validateSourcedId(sourcedId, lineNumber, errors, "users");

                if (mode.equals("delta")) {
                    validateStatus(status, sourcedId, lineNumber, errors, "users");
                    validateDateLastModified(dateLastModified, sourcedId, lineNumber, errors, "users");
                } else {
                    validateStatusBulkMode(status, lineNumber, errors, "users");
                    validateDateLastModifiedBulkMode(dateLastModified, lineNumber, errors, "users");
                }

                if (enabledUser == null || enabledUser.isBlank()) {
                    String message = String.format("There is no value found for field: enabledUser for user with sourcedId %s", sourcedId);
                    errors.add(createFileErrorEntity("enabledUser", message, lineNumber, "users"));
                    log.error(message);
                } else if (!enabledUser.matches("^(true|false)$")) {
                    String message = String.format("Invalid enabledUser value: %s for user with sourcedId %s", enabledUser, sourcedId);
                    errors.add(createFileErrorEntity("enabledUser", message, lineNumber, "users"));
                    log.error(message);
                }
                if (userIds != null && !userIds.isBlank() && !userIds.equalsIgnoreCase("null") &&
                        !userIds.matches(USER_IDS_REGEX)
                ) {
                    String message = String.format("Invalid userIds value: %s for user with sourcedId %s", userIds, sourcedId);
                    errors.add(createFileErrorEntity("userIds", message, lineNumber, "users"));
                    log.error(message);
                }


                if (primaryOrgSourcedId != null && !primaryOrgSourcedId.isBlank())
                    validateGUID("primaryOrgSourcedId", primaryOrgSourcedId, sourcedId, lineNumber, errors, "users");

                validateRequiredField("username", username, lineNumber, errors, "users");

                if (validateRequiredField("givenName", givenName, lineNumber, errors, "users")) {
                    if (!givenName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid givenName value: %s for user with sourcedId %s", givenName, sourcedId);
                        errors.add(createFileErrorEntity("givenName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (validateRequiredField("familyName", familyName, lineNumber, errors, "users")) {
                    if (!familyName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid familyName value: %s for user with sourcedId %s", familyName, sourcedId);
                        errors.add(createFileErrorEntity("familyName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (middleName != null && !middleName.isBlank()) {
                    if (!middleName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid middleName value: %s for user with sourcedId %s", middleName, sourcedId);
                        errors.add(createFileErrorEntity("middleName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (validateRequiredField("preferredGivenName", preferredGivenName, lineNumber, errors, "users")) {
                    if (!preferredGivenName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid preferredGivenName value: %s for user with sourcedId %s", preferredGivenName, sourcedId);
                        errors.add(createFileErrorEntity("preferredGivenName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }
                if (validateRequiredField("preferredFamilyName", preferredFamilyName, lineNumber, errors, "users")) {
                    if (!preferredFamilyName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid preferredFamilyName value: %s for user with sourcedId %s", preferredFamilyName, sourcedId);
                        errors.add(createFileErrorEntity("preferredFamilyName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (preferredMiddleName != null && !preferredMiddleName.isBlank()) {
                    if (!preferredMiddleName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid preferredMiddleName value: %s for user with sourcedId %s", preferredMiddleName, sourcedId);
                        errors.add(createFileErrorEntity("preferredMiddleName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (validateRequiredField("userMasterIdentifier", userMasterIdentifier, lineNumber, errors, "users")) {
                    if (!userMasterIdentifier.matches(UUIDV4_REGEX)) {
                        String message = String.format("Invalid userMasterIdentifier value: %s for user with sourcedId %s", userMasterIdentifier, sourcedId);
                        errors.add(createFileErrorEntity("userMasterIdentifier", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (validateRequiredField("metadata.jp.kanaGivenName", metadataJpKanaGivenName, lineNumber, errors, "users")) {
                    if (!metadataJpKanaGivenName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid metadata.jp.kanaGivenName value: %s for user with sourcedId %s", metadataJpKanaGivenName, sourcedId);
                        errors.add(createFileErrorEntity("metadata.jp.kanaGivenName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (metadataJpKanaMiddleName != null && !metadataJpKanaMiddleName.isBlank()) {
                    if (!metadataJpKanaMiddleName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid metadata.jp.kanaMiddleName value: %s for user with sourcedId %s", metadataJpKanaMiddleName, sourcedId);
                        errors.add(createFileErrorEntity("metadata.jp.kanaMiddleName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }

                if (validateRequiredField("metadata.jp.kanaFamilyName", metadataJpKanaFamilyName, lineNumber, errors, "users")) {
                    if (!metadataJpKanaFamilyName.matches(FULL_WIDTH_KATAKANA_REGEX)) {
                        String message = String.format("Invalid metadata.jp.kanaFamilyName value: %s for user with sourcedId %s", metadataJpKanaFamilyName, sourcedId);
                        errors.add(createFileErrorEntity("metadata.jp.kanaFamilyName", message, lineNumber, "users"));
                        log.error(message);
                    }
                }
                validateRequiredField("metadata.jp.homeClass", metadataJpHomeClass, lineNumber, errors, "users");

                if (grades != null && !grades.isBlank()) {
                    String[] gradeList = grades.split(",");
                    if (!PERMITTED_GRADES.containsAll(List.of(gradeList))) {
                        String message = String.format("Invalid grades value: %s", grades);
                        errors.add(createFileErrorEntity("grades", message, lineNumber, "users"));
                        log.error(message);
                    }
                }
            }
        }
    }

    private boolean validateRequiredField(String fieldName, String fieldValue, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (fieldValue == null || fieldValue.isBlank()) {
            errors.add(createFileErrorEntity(fieldName, "There is no value found for field: " + fieldName, lineNumber, fileCsvName));
            log.error("Record[%d] There is no value found for field: %d", lineNumber, fieldName, fileCsvName);
            return false;
        }
        return true;
    }


    private void validateClassType(String classType, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (classType == null || classType.isBlank()) {
            errors.add(createFileErrorEntity("type", "There is no value found for field: type", lineNumber, fileCsvName));
        } else if (!PERMITTED_CLASS_TYPES.contains(classType)) {
            String message = String.format("Invalid type: %s with sourcedId %s", classType, sourcedId);
            errors.add(createFileErrorEntity(classType, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateSchoolYear(String schoolYear, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (schoolYear == null || schoolYear.isBlank()) {
            String message = String.format("There is no value found for field: schoolYear for academicSession with sourcedId %s", sourcedId);
            errors.add(createFileErrorEntity("schoolYear", message, lineNumber, fileCsvName));
            log.error(message);
        } else if (!schoolYear.matches(YEAR_REGEX)) {
            String message = String.format("Invalid schoolYear value: %s with sourcedId %s", schoolYear, sourcedId);
            errors.add(createFileErrorEntity("schoolYear", message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateDate(String value, String key, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (value == null || value.isBlank()) {
            String message = String.format("There is no value found for field: %s for academicSession with sourcedId %s", key, sourcedId);
            errors.add(createFileErrorEntity(key, message, lineNumber, fileCsvName));
            log.error(message);
        } else if (!value.matches(DATE_REGEX)) {
            String message = String.format("Invalid %s value: %s with sourcedId %s", key, value, sourcedId);
            errors.add(createFileErrorEntity(key, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateType(String type, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (type == null || type.isBlank()) {
            errors.add(createFileErrorEntity("type", "There is no value found for field: type", lineNumber, fileCsvName));
        } else if (!PERMITTED_ACADEMIC_SESSION_TYPES.contains(type)) {
            String message = String.format("Invalid type: %s with sourcedId %s", type, sourcedId);
            errors.add(createFileErrorEntity(type, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateTitle(String title, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (title == null || title.isBlank()) {
            String message = String.format("There is no value found for field: title for academicSession with sourcedId %s", sourcedId);
            errors.add(createFileErrorEntity("title", message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateDateLastModified(String dateLastModified, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (dateLastModified == null || dateLastModified.isBlank()) {
            String message = String.format("There is no value found for field: dateLastModified for user with sourcedId %s", sourcedId);
            errors.add(createFileErrorEntity("dateLastModified", message, lineNumber, fileCsvName));
            log.error(message);
        } else if (!dateLastModified.matches(DATE_TIME_REGEX)) {
            String message = String.format("Invalid dateLastModified value: %s with sourcedId %s", dateLastModified, sourcedId);
            errors.add(createFileErrorEntity("dateLastModified", message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private int indexOfHeader(String[] header, String field) {
        int index = Arrays.asList(header).indexOf(field);
        if (index == -1) {
            throw new IllegalArgumentException("Field not found in header: " + field);
        }
        return index;
    }

    private void validateSourcedId(String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (sourcedId == null || sourcedId.isBlank()) {
            errors.add(createFileErrorEntity("sourcedId", "There is no value found for field: sourcedId", lineNumber, fileCsvName));
        } else if (!sourcedId.matches(GUID_REGEX)) {
            String message = String.format("Invalid sourcedId value: %s with line %d", sourcedId, lineNumber);
            errors.add(createFileErrorEntity("sourcedId", message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private void validateCourseSourcedId(String courseSourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsv) {
        if (courseSourcedId == null || courseSourcedId.isBlank()) {
            errors.add(createFileErrorEntity("courseSourcedId", "There is no value found for field: courseSourcedId", lineNumber, fileCsv));
        } else if (!courseSourcedId.matches(GUID_REGEX)) {
            String message = String.format("Invalid courseSourcedId value: %s with line %d", courseSourcedId, lineNumber);
            errors.add(createFileErrorEntity("courseSourcedId", message, lineNumber, fileCsv));
            log.error(message);
        }
    }

    private void validateStatus(String status, String sourcedId, int lineNumber, List<FileErrorEntity> errors, String fileCsvName) {
        if (status == null || status.isBlank()) {
            errors.add(createFileErrorEntity("status", "There is no value found for field: status", lineNumber, fileCsvName));
        } else if (!PERMITTED_STATUSES.contains(status)) {
            String message = String.format("Invalid status: %s with sourcedId %s", status, sourcedId);
            errors.add(createFileErrorEntity(status, message, lineNumber, fileCsvName));
            log.error(message);
        }
    }

    private boolean validateHeader(File file, List<FileErrorEntity> errors, String[] expectedHeader, String fileName) throws
            IOException, CsvValidationException {
        CSVReader reader = new CSVReader(new FileReader(file));
        String[] header = reader.readNext();
        boolean missingHeader = false;
        boolean headerValid = true;
        if (!new HashSet<>(Arrays.asList(header)).containsAll(Arrays.asList(expectedHeader))) {
            List<String> headerNotInHeaders = Arrays.stream(expectedHeader).filter(s -> !Arrays.asList(header).contains(s)).collect(Collectors.toList());
            errors.add(FileErrorEntity.builder()
                    .fileCsvName(fileName)
                    .fieldName("header")
                    .errorMessage(String.format("%s.csv is missing required fields: %s", fileName, String.join(", ", headerNotInHeaders)))
                    .build());
            log.error("{}.csv is missing required fields.", fileName);
            missingHeader = true;
            headerValid = false;
        }


        // check if the header fields match the expected header
        if (!missingHeader) {
            String headerLine = new BufferedReader(new FileReader(file)).readLine();
            String[] headerFields = headerLine.split(",");
            for (int i = 0; i < expectedHeader.length; i++) {
                if (!headerFields[i].equals(expectedHeader[i])) {
                    if (Arrays.asList(expectedHeader).contains(headerFields[i])) {
                        errors.add(FileErrorEntity.builder()
                                .fileCsvName(fileName)
                                .fieldName(headerFields[i])
                                .errorMessage(String.format("The following header is in the incorrect index/position of the CSV file. Header: %s ; Expected Index: %d ; Actual Index: %d", headerFields[i], Arrays.asList(expectedHeader).indexOf(headerFields[i]) + 1, i + 1))
                                .build());
                        log.error("The following header is in the incorrect index/position of the CSV file. Header: {} ; Expected Index: {} ; Actual Index: {}", headerFields[i], i + 1, headerFields.length - i);
                        headerValid = false;
                    }
                }
            }
        }

        return headerValid;
    }


    FileErrorEntity createFileErrorEntity(String fieldName, String errorMessage, int lineNumber, String fileCsvName) {
        return FileErrorEntity.builder()
                .fileCsvName(fileCsvName)
                .fieldName(fieldName)
                .errorMessage(String.format("Record[%d] %s", lineNumber, errorMessage))
                .build();
    }

    public void validateOrgsExtended(File originalCSV, File orgsCsv, List<FileErrorEntity> errors, String fileName) {
        Map<String, String> orgsMap = new HashMap<>();

        try (CSVReader reader = new CSVReader(new FileReader(orgsCsv))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");
            int typeIndex = Arrays.asList(header).indexOf("type");

            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String sourcedId = line[sourcedIdIndex];
                String type = line[typeIndex];
                orgsMap.put(sourcedId, type);
            }
        } catch (IOException | CsvValidationException e) {
            throw new RuntimeException(e);
        }

        try (CSVReader reader = new CSVReader(new FileReader(originalCSV))) {
            String[] header = reader.readNext();
            int schoolSourcedIdIndex = Arrays.asList(header).indexOf("schoolSourcedId");
            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String schoolSourcedId = line[schoolSourcedIdIndex];
                if (!"school".equals(orgsMap.get(schoolSourcedId))) {
                    String message = String.format("Invalid schoolSourcedId value: %s orgs.type value %s", schoolSourcedId, orgsMap.get(schoolSourcedId));
                    errors.add(createFileErrorEntity("schoolSourcedId", message, lineNumber, fileName));
                    log.error(message);
                }
            }
        } catch (IOException | CsvValidationException e) {
            throw new RuntimeException(e);
        }
    }

    public void validateUsersExtended(File userCsv, File classCsv, List<FileErrorEntity> errors, String fileName) {
        List<String> classesSourceIds = new ArrayList<>();

        try (CSVReader reader = new CSVReader(new FileReader(classCsv))) {
            String[] header = reader.readNext();
            int sourcedIdIndex = Arrays.asList(header).indexOf("sourcedId");

            for (String[] line; (line = reader.readNext()) != null; ) {
                String sourcedId = line[sourcedIdIndex];
                classesSourceIds.add(sourcedId);
            }
        } catch (IOException | CsvValidationException e) {
            throw new RuntimeException(e);
        }

        try (CSVReader reader = new CSVReader(new FileReader(userCsv))) {
            String[] header = reader.readNext();
            int metadataJpHomeClassIndex = Arrays.asList(header).indexOf("metadata.jp.homeClass");
            int lineNumber = 1;
            for (String[] line; (line = reader.readNext()) != null; lineNumber++) {
                String metadataJpHomeClass = line[metadataJpHomeClassIndex];
                if (!classesSourceIds.contains(metadataJpHomeClass)) {
                    String message = String.format("Invalid metadata.jp.homeClass value: %s not matching with classes.sourceId", metadataJpHomeClass);
                    errors.add(createFileErrorEntity("metadata.jp.homeClass", message, lineNumber, fileName));
                    log.error(message);
                }
            }
        } catch (IOException | CsvValidationException e) {
            throw new RuntimeException(e);
        }
    }
}

