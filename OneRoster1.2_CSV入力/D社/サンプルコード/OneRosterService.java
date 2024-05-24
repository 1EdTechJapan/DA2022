package com.servername.bridge.service.identity;

import com.servername.bridge.util.OneRosterUtilService;
import com.servername.services.exception.HttpNotAllowedException;
import com.servername.services.exception.HttpServerErrorInternalException;
import com.servername.services.identity.Visitor;
import com.servername.services.util.FileUtil;
import com.servername.services.util.Pair;
import com.servername.services.util.StringUtil;
import com.servername.services.util.WithServerLogin;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import javax.inject.Inject;
import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Root class for interpreting OneRoster uploads
 */
public class OneRosterService {
    @Inject
    OrganizationService organizationService;
    @Inject
    ClassService classService;
    @Inject
    AccountService accountService;
    @Inject
    OneRosterUtilService oneRosterUtilService;

    /**
     * Unzip a OneRoster zip file and store the contents as separate CSV files
     *
     * @param fileStream Input stream containing the zip file
     * @return A map of file names to Files
     * @throws IOException
     */
    public Map<String, File> unzipCsvFiles(InputStream fileStream) throws IOException {
        ZipInputStream zipInputStream = new ZipInputStream(fileStream);
        Map<String, File> csvFiles = new HashMap<>();
        byte[] buffer = new byte[2048];
        ZipEntry entry = zipInputStream.getNextEntry();
        while (entry != null) {
            if (!entry.isDirectory()) { //OneRoster zip files shouldn't have directories; ignore them if they're there
                String fileName = entry.getName();
                int len;
                File tempFile = FileUtil.getNewEmptyFile(fileName, ".csv");
                FileOutputStream fos = new FileOutputStream(tempFile);
                while ((len = zipInputStream.read(buffer)) > 0) {
                    fos.write(buffer, 0, len);
                }
                fos.close();
                csvFiles.put(fileName, tempFile);
            }
            entry = zipInputStream.getNextEntry();
        }
        fileStream.close();
        return csvFiles;
    }

    /**
     * Given a OneRoster zip file and a partnerId, parse the roster and save the accounts, classes, and organizations under the specified partner
     *
     * @param fileStream The input stream containing the roster
     * @param partnerId  The partner to associate the uploaded users and schools with
     */
    public void processRoster(InputStream fileStream, int partnerId) {
        new WithServerLogin<Boolean>() {
            public Boolean body(Visitor serverVisitor) {
                try {
                    Map<String, File> csvFiles = unzipCsvFiles(fileStream);
                    // Validate that the manifest is present and valid, and note which files it says are present
                    File manifest = csvFiles.get("manifest.csv");
                    if (manifest == null) {
                        throw new HttpNotAllowedException("manifest.csv missing");
                    }
                    boolean foundOrgs = false;
                    boolean foundCourses = false;
                    boolean foundClasses = false;
                    boolean foundEnrollments = false;
                    boolean foundRoles = false;
                    boolean foundUsers = false;
                    boolean foundManifestVersion = false;
                    boolean foundOneRosterVersion = false;
                    try (CSVParser parser = CSVParser.parse(new FileReader(manifest), CSVFormat.RFC4180.builder().setHeader().build())) {
                        if (!parser.getHeaderNames().contains("propertyName")) {
                            throw new HttpNotAllowedException("propertyName header not found");
                        }
                        if (!parser.getHeaderNames().contains("value")) {
                            throw new HttpNotAllowedException("value header not found");
                        }
                        oneRosterUtilService.validateHeaderValues(parser, "manifest.csv", "propertyName", "value");
                        for (CSVRecord manifestLine : parser) {
                            switch (manifestLine.get("propertyName")) {
                                case "file.orgs":
                                    foundOrgs = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.courses":
                                    foundCourses = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.classes":
                                    foundClasses = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.enrollments":
                                    foundEnrollments = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.roles":
                                    foundRoles = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.users":
                                    foundUsers = validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "file.academicSessions":
                                case "file.demographics":
                                case "file.userProfiles":
                                    //Validate that these are correct even though Your Company doesn't care about the contents
                                    validateFileValue(manifestLine.get("propertyName"), manifestLine.get("value"), csvFiles);
                                    break;
                                case "manifest.version":
                                    if (!manifestLine.get("value").equals("1.0")) {
                                        throw new HttpNotAllowedException("Unrecognized manifest version " + manifestLine.get("value"));
                                    }
                                    foundManifestVersion = true;
                                    break;
                                case "oneroster.version":
                                    if (!manifestLine.get("value").equals("1.2")) {
                                        throw new HttpNotAllowedException("Unrecognized OneRoster version number " + manifestLine.get("value"));
                                    }
                                    foundOneRosterVersion = true;
                            }
                        }
                        if (!foundManifestVersion) {
                            throw new HttpNotAllowedException("manifest.version not found in manifest.csv");
                        }
                        if (!foundOneRosterVersion) {
                            throw new HttpNotAllowedException("oneroster.version not found in manifest.csv");
                        }
                    }
                    Map<String, Integer> orgIdsMap = null;
                    Set<String> districtOrgIds = null;
                    Map<String, Integer> classIdMap = null;
                    if (foundOrgs) {
                        Pair<Map<String, Integer>, Set<String>> orgResults = organizationService.processOneRosterOrganizations(partnerId, csvFiles.get("orgs.csv"));
                        orgIdsMap = orgResults.getFirst();
                        districtOrgIds = orgResults.getSecond();
                    }
                    if (foundClasses) {
                        if (orgIdsMap == null) {
                            throw new HttpNotAllowedException("orgs.csv is required if classes.csv is included");
                        }
                        if (!foundCourses) {
                            throw new HttpNotAllowedException("courses.csv is required if classes.csv is included");
                        }
                        Map<String, Integer> courseIdToOrgMap = getCourseIdToOrgMap(csvFiles.get("courses.csv"), orgIdsMap);
                        classIdMap = classService.processOneRosterClasses(csvFiles.get("classes.csv"), courseIdToOrgMap, districtOrgIds, partnerId);
                    }
                    if (foundUsers) {
                        Map<String, Integer> accountIdsMap = accountService.processOneRosterAccounts(serverVisitor, csvFiles.get("users.csv"), partnerId, classIdMap, orgIdsMap);
                        if (foundEnrollments) {
                            if (!foundClasses || classIdMap == null) {
                                throw new HttpNotAllowedException("classes.csv is required if enrollments.csv is included");
                            }
                            classService.processOneRosterEnrollments(serverVisitor, csvFiles.get("enrollments.csv"), classIdMap, accountIdsMap, orgIdsMap, districtOrgIds);
                        }
                    }
                    return true;
                } catch (IOException e) {
                    throw new HttpServerErrorInternalException("I/O error trying to process OneRoster data", e);
                } catch (Throwable t) {
                    throw t;
                }
            }
        }.run();
    }

    /**
     * Parse and validate a OneRoster courses file. Even if Your Company does not directly record courses, we still need to
     * generate a map of course sourcedIds to their parent organization's ids in our database
     *
     * @param classFile
     * @param orgIdsMap A map of organization sourcedIds to organization ids in our database
     * @return
     * @throws IOException
     */
    private Map<String, Integer> getCourseIdToOrgMap(File classFile, Map<String, Integer> orgIdsMap) throws IOException {
        Map<String, Integer> ids = new HashMap<>();
        try (CSVParser parser = CSVParser.parse(new FileReader(classFile), CSVFormat.RFC4180.builder().setHeader().build())) {
            oneRosterUtilService.validateHeaderValues(parser, "courses.csv", "sourcedId", "status", "dateLastModified", "schoolYearSourcedId", "title", "courseCode", "grades", "orgSourcedId", "subjects", "subjectCodes");
            for (CSVRecord classRecord : parser) {
                String sourcedId = classRecord.get("sourcedId");
                String organizationSourcedId = classRecord.get("orgSourcedId");
                String title = classRecord.get("title");
                String schoolYearSourcedId = classRecord.get("schoolYearSourcedId");
                String courseCode = classRecord.get("courseCode");
                String grades = classRecord.get("grades");
                String subjectCodes = classRecord.get("subjectCodes");
                if (StringUtil.anyEmptyOrNull(sourcedId, organizationSourcedId, title)) {
                    throw new HttpNotAllowedException("Missing required data in courses.csv");
                }
                StringUtil.validateUUIDs(sourcedId, organizationSourcedId, schoolYearSourcedId);
                if (StringUtil.containsHalfWidthKana(title)) {
                    throw new HttpNotAllowedException("Half-width katakana in courses.csv");
                }
                if (courseCode != null && !courseCode.isEmpty()) {
                    throw new HttpNotAllowedException("courseCode must be empty");
                }
                oneRosterUtilService.validateStatusAndUpdateDate(parser, classRecord, "courses.csv");
                oneRosterUtilService.validateGrades(grades);
                oneRosterUtilService.validateSubjectCodes(subjectCodes);
                if (parser.getHeaderNames().contains("subjects") || parser.getHeaderNames().contains("subjectCodes")) {
                    if (!parser.getHeaderNames().contains("subjects") || !parser.getHeaderNames().contains("subjectCodes")) {
                        throw new HttpNotAllowedException("In courses.csv, subjects and subjectCodes must both be present or both absent");
                    }
                    String subjects = classRecord.get("subjects");
                    int subjectCount = subjects == null || subjects.isEmpty() ? 0 : subjects.split(",").length;
                    int subjectCodeCount = subjectCodes == null | subjectCodes.isEmpty() ? 0 : subjectCodes.split(",").length;
                    if (subjectCount != subjectCodeCount) {
                        throw new HttpNotAllowedException("Invalid subjects/subjectCodes in courses.csv");
                    }
                }
                Integer orgId = orgIdsMap.get(organizationSourcedId);
                if (orgId == null) {
                    throw new HttpNotAllowedException("Unrecognized organization id " + organizationSourcedId + " found in courses.csv");
                }
                ids.put(sourcedId, orgId);
            }
            return ids;
        }
    }

    private boolean validateFileValue(String propertyName, String value, Map<String, File> csvFiles) {
        String name = propertyName.replace("file.", "") + ".csv";
        if (value.equals("absent")) {
            if (csvFiles.containsKey(name)) {
                throw new HttpNotAllowedException("File " + name + " should not be present according to manifest, but was found");
            }
            return false;
        } else if (value.equals("bulk")) {
            if (!csvFiles.containsKey(name)) {
                throw new HttpNotAllowedException("File " + name + " should be present according to manifest, but was not found");
            }
            return true;
        } else if (value.equals("delta")) {
            throw new HttpNotAllowedException("Delta csvs not implemented for type " + name);
        }
        throw new HttpNotAllowedException("Unrecognized manifest value " + value + " for " + name);
    }
}
