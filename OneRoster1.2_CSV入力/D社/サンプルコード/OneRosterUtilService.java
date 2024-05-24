package com.servername.bridge.util;

import com.servername.services.exception.HttpNotAllowedException;
import com.servername.services.util.ConstantsBase;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * Utility functions for OneRoster uploads
 */
public class OneRosterUtilService {
    // DATEFORMAT_BSON_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
    private static DateFormat bsonFormat = new SimpleDateFormat(ConstantsBase.DATEFORMAT_BSON_PATTERN);
    // DATEFORMAT_SHORT_PATTERN = "yyyy-MM-dd";
    private static DateFormat dateFormat = new SimpleDateFormat(ConstantsBase.DATEFORMAT_SHORT_PATTERN);
    private static Set<String> validGrades = new HashSet<>(Arrays.asList("P1", "P2", "P3", "P4", "P5", "P6", "J1", "J2", "J3", "H1", "H2", "H3", "E1", "E2", "E3"));
    private static Set<String> validSubjectCodes = new HashSet<>(Arrays.asList("P010", "P020", "P030", "P040", "P050", "P060", "P070", "P080", "P090", "P100", "J010", "J020", "J030", "J040", "J050", "J060", "J070", "J080", "J090"));

    /**
     * Validate that a CSV file has the expected header values in the expected order
     *
     * @param parser         A CSVParser parsing the file to be validated
     * @param fileName       The name of the file
     * @param expectedFields The expected headers in the expected order
     */
    public void validateHeaderValues(CSVParser parser, String fileName, String... expectedFields) {
        if (parser.getHeaderNames().size() != expectedFields.length) {
            throw new HttpNotAllowedException("Wrong number of header fields");
        }
        for (int i = 0; i < expectedFields.length; i++) {
            String expected = expectedFields[i];
            String actual = parser.getHeaderNames().get(i);
            if (!expected.equals(actual)) {
                throw new HttpNotAllowedException("Incorrect or misordered header field in " + fileName + ": " + actual + "; expected " + expected);
            }
        }
    }

    /**
     * Validate that the status and updateDate values in a CSV record are either valid or absent. These fields shouldn't actually exist
     * in bulk updates, but MEXCBT wants them validated when they're there anyway.
     *
     * @param parser
     * @param record
     * @param fileName
     */
    public void validateStatusAndUpdateDate(CSVParser parser, CSVRecord record, String fileName) {
        //These fields shouldn't even exist in bulk updates, but MEXCBT wants them validated when they're there anyway
        if (parser.getHeaderNames().contains("status")) {
            String status = record.get("status");
            if (status != null && !status.isEmpty() && !status.equals("active") && !status.equals("tobedeleted")) {
                throw new HttpNotAllowedException("Illegal status value " + status + " in " + fileName);
            }
        }
        if (parser.getHeaderNames().contains("dateLastModified")) {
            String dateString = record.get("dateLastModified");
            if (dateString != null && !dateString.isEmpty()) {
                validateDateTimeFormat(dateString, fileName, "dateLastModified");
            }
        }
    }

    /**
     * Validate that a string expected to contain a datetime is properly formatted
     *
     * @param dateString
     * @param fileName
     * @param fieldName
     */
    public void validateDateTimeFormat(String dateString, String fileName, String fieldName) {
        try {
            bsonFormat.parse(dateString);
        } catch (ParseException e) {
            throw new HttpNotAllowedException("Invalid datetime format in " + fileName + ", column " + fieldName + ": " + dateString + " (expected yyyy-MM-tt'T'HH:mm:ss.SSS'Z'");
        }
    }

    /**
     * Validate that a string expected to contain a date (but no time) is properly formatted
     *
     * @param dateString
     * @param fileName
     * @param fieldName
     */
    public void validateDateFormat(String dateString, String fileName, String fieldName) {
        try {
            dateFormat.parse(dateString);
        } catch (ParseException e) {
            throw new HttpNotAllowedException("Invalid date format in " + fileName + ", column " + fieldName + ": " + dateString + " (expected yyyy-MM-dd");
        }
    }

    /**
     * Validate that a grade string is one of the expected values
     *
     * @param gradeString
     */
    public void validateGrades(String gradeString) {
        if (gradeString == null || gradeString.isEmpty()) {
            return;
        }
        for (String grade : gradeString.split(",")) {
            if (!validGrades.contains(grade.toUpperCase())) {
                throw new HttpNotAllowedException("Invalid grade value in grades " + gradeString);
            }
        }
    }

    /**
     * Validate that a subject code string is one of the expected values
     *
     * @param codesString
     */
    public void validateSubjectCodes(String codesString) {
        if (codesString == null || codesString.isEmpty()) {
            return;
        }
        for (String code : codesString.split(",")) {
            if (!validSubjectCodes.contains(code.toUpperCase())) {
                throw new HttpNotAllowedException("Invalid subject code in subjectCodes " + codesString);
            }
        }
    }
}
