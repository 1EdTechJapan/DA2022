package com.group.oneroster.service;

import com.group.oneroster.persistence.domain.FileErrorEntity;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

@Slf4j
@Service
public class OneRosterCsvService {

    private static final String MANIFEST_FILE_NAME = "manifest";
    private static final String DOT_CSV = ".csv";

    private final String[] EXPECTEDMANIFESTPROPERTIES = {"manifest.version", "oneroster.version", "file.academicSessions", "file.categories", "file.classes", "file.classResources", "file.courses", "file.courseResources", "file.demographics", "file.enrollments", "file.lineItemLearningObjectiveIds", "file.lineItems", "file.lineItemScoreScales", "file.orgs", "file.resources", "file.resultLearningObjectiveIds", "file.results", "file.resultScoreScales", "file.roles", "file.scoreScales", "file.userProfiles", "file.userResources", "file.users", "source.systemName", "source.systemCode"};


    public Map<String, String> validateManifest(ZipFile zipFile, File manifestFile, List<FileErrorEntity> errors) {
        Map<String, String> manifestData = new HashMap<>();

        try (CSVParser parser = new CSVParser(new FileReader(manifestFile), CSVFormat.DEFAULT)) {
            Set<String> declaredFiles = new HashSet<>();

            for (CSVRecord record : parser) {

                String propertyName = record.get(0);
                String value = record.get(1);
                if (record.getRecordNumber() == 1) {
                    if (!propertyName.equals("propertyName")) {
                        errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage(String.format("Invalid propertyName column name: %s", propertyName)).build());
                        log.error("Invalid property: {}", propertyName);
                    }
                    if (!value.equals("value")) {
                        errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage(String.format("Invalid value column name: %s", value)).build());
                        log.error("Invalid property: {}", value);
                    }
                    continue;
                }
                if (Arrays.asList(EXPECTEDMANIFESTPROPERTIES).contains(propertyName)) {
                    if (propertyName.equals("manifest.version")) {
                        validateManifestVersion(value, errors);
                    } else if (propertyName.equals("oneroster.version")) {
                        validateOneRosterVersion(value, errors);
                    } else if (propertyName.startsWith("file.")) {
                        validateFile(propertyName, value, declaredFiles, zipFile, errors);
                    } else if (propertyName.startsWith("source.")) {
                        // source properties are optional and do not require validation
                    } else {
                        log.error("Unknown property: {}", propertyName);
                    }
                    manifestData.put(propertyName, value);
                } else {
                    errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage(String.format("Invalid property: %s", propertyName)).build());
                    log.error("Invalid property: {}", propertyName);
                }
            }

        } catch (IOException e) {
            log.error("IOException: {}", e.getMessage());
        }
        return manifestData;

    }

    private void validateManifestVersion(String value, List<FileErrorEntity> errors) {
        if (!value.equals("1.0")) {
            errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName("manifest.version").errorMessage("manifest.version is invalid. Format must be X.X OR X.X.X. The initial value must be 1.0").build());
            log.error("Invalid manifest version: {}", value);
        }
    }

    private void validateOneRosterVersion(String value, List<FileErrorEntity> errors) {
        if (!value.equals("1.2")) {
            errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName("oneroster.version").errorMessage("Oneroster.version is invalid.").build());
            log.error("Invalid OneRoster version: {}", value);
        }
    }

    private void validateFile(String propertyName, String value, Set<String> declaredFiles, ZipFile zipFile, List<FileErrorEntity> errors) {
        String fileName = propertyName.substring(5).concat(DOT_CSV);

        if (!value.equals("absent") && !value.equals("bulk") && !value.equals("delta")) {
            errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage("Invalid file processing mode: " + value).build());
            log.error("Invalid file processing mode: {}", value);
        } else if (value.equals("absent")) {
            ZipEntry fileEntry = zipFile.getEntry(fileName);
            if (fileEntry != null) {
                errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage(String.format("An existing file contains absent (%s)", fileName)).build());
                log.error("An existing file contains absent ({})", fileName);
            }
        } else {
            declaredFiles.add(fileName);
            ZipEntry fileEntry = zipFile.getEntry(fileName);
            if (fileEntry == null) {
                errors.add(FileErrorEntity.builder().fileCsvName(MANIFEST_FILE_NAME).fieldName(propertyName).errorMessage("Missing file: " + fileName).build());
                log.error("Missing file: {}", fileName);
            }
        }
    }


}
