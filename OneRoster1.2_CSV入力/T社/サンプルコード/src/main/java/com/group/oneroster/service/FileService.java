package com.group.oneroster.service;

import com.group.oneroster.mapper.FileUploadMapper;
import com.group.oneroster.mapper.UserMapper;
import com.group.oneroster.persistence.domain.FileErrorEntity;
import com.group.oneroster.persistence.domain.FileUploadEntity;
import com.group.oneroster.persistence.domain.UserEntity;
import com.group.oneroster.persistence.repository.ErrorRepository;
import com.group.oneroster.persistence.repository.FileUploadRepository;
import com.group.oneroster.persistence.repository.UserRepository;
import com.group.oneroster.service.searching.SearchResult;
import com.group.oneroster.validator.OneRosterValidator;
import com.group.oneroster.web.dto.FileDto;
import com.group.oneroster.web.dto.UploadFileResponseDto;
import com.group.oneroster.web.dto.UserRecord;
import com.opencsv.bean.CsvToBeanBuilder;
import com.opencsv.exceptions.CsvValidationException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

@Slf4j
@Service
@RequiredArgsConstructor
public class FileService extends BaseService<FileDto> {

    private final FileUploadRepository fileUploadRepository;
    private final FileUploadMapper fileUploadMapper;
    private final UserMapper userMapper;
    private final UserRepository userRepository;

    private final OneRosterCsvService oneRosterCsvService;
    private final ErrorRepository errorRepository;

    private final OneRosterValidator oneRosterValidator;

    public Page<FileUploadEntity> getAllFiles(PageRequest pageRequest) {
        return fileUploadRepository.findAll(pageRequest);
    }

    public File downloadAllLog() throws IOException {
        File zipFile = File.createTempFile("logs", ".zip");
        Iterable<FileUploadEntity> fileUploadEntities = fileUploadRepository.findAll();
        FileOutputStream fos = new FileOutputStream(zipFile);
        ZipOutputStream zos = new ZipOutputStream(fos);
        fileUploadEntities.forEach(fileUploadEntity -> {
            try {
                File file = downloadLogWithFileId(fileUploadEntity.getId());
                FileInputStream fis = new FileInputStream(file);
                ZipEntry zipEntry = new ZipEntry(file.getName());
                zos.putNextEntry(zipEntry);
                // Read bytes from the source file and write them to the ZipOutputStream
                // Create a buffer to read data from the file input stream
                byte[] buffer = new byte[1024];
                int len;
                // Read data from the file input stream and write it to the zip output stream
                while ((len = fis.read(buffer)) > 0) {
                    zos.write(buffer, 0, len);
                }

                fis.close();
                zos.closeEntry();
                zos.flush();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
        zos.close();
        fos.close();
        return zipFile;
    }

    public File downloadLogWithFileId(Long fileId) throws IOException {
        FileUploadEntity fileUploadEntity = fileUploadRepository.findById(fileId).orElseThrow();
        String suffixedFileName = fileUploadEntity.getStatus().equals("SUCCESS") ? ".success.log" : ".errors.log";
        File file = File.createTempFile(fileUploadEntity.getFileName(), suffixedFileName);
        try (FileWriter writer = new FileWriter(file)) {
            writer.write("File Name: " + fileUploadEntity.getFileName() + "\n");

            if (fileUploadEntity.getStatus().equals("SUCCESS")) {
                writer.write(String.format("Import successful %d user!\n", fileUploadEntity.getUsers().size()));
                writer.write(String.format("Total time processing: %d ms\n", fileUploadEntity.getTimeProcessed()));
                fileUploadEntity.getUsers().forEach(userEntity -> {
                    try {
                        writer.write(userEntity.toString() + "\n");
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });
            } else {
                writer.write("File import failed! Has errors! \n");
                writer.write(String.format("Total time processing: %d ms\n", fileUploadEntity.getTimeProcessed()));
                List<FileErrorEntity> fileErrorEntities = fileUploadEntity.getErrors();
                fileErrorEntities.forEach(fileErrorEntity -> {
                    try {
                        writer.write(fileErrorEntity.toString() + "\n");
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });
            }
        } catch (IOException e) {
            log.error(e.getMessage());
        }
        return file;
    }

    public UploadFileResponseDto handleUploadFiles(MultipartFile file) throws Exception {
        ZonedDateTime startTime = LocalDateTime.now().atZone(ZoneOffset.UTC);
        UploadFileResponseDto responseDto = new UploadFileResponseDto();
        File newFile = File.createTempFile(file.getName(), ".zip");
        file.transferTo(newFile);
        var ref = new Object() {
            List<FileErrorEntity> errors = new ArrayList<>();
        };
        Map<String, File> tempFiles = new HashMap<>();

        try (ZipFile zipFile = new ZipFile(newFile)) {
            ZipEntry manifestEntry = null;

            // Extract all CSV files and store them in temporary files
            for (Enumeration<? extends ZipEntry> entries = zipFile.entries(); entries.hasMoreElements(); ) {
                ZipEntry entry = entries.nextElement();
                if (entry.getName().endsWith(".csv")) {
                    File tempFile = File.createTempFile(entry.getName(), "");
                    try (InputStream stream = zipFile.getInputStream(entry)) {
                        Files.copy(stream, tempFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                    }
                    tempFiles.put(entry.getName(), tempFile);
                }
                if (entry.getName().equals("manifest.csv")) {
                    manifestEntry = entry;
                }
            }

            // Validate manifest file if it exists
            if (manifestEntry == null) {
//                throw new IOException("The ZIP file does not contain a manifest file (manifest.csv)");
                String message = "The ZIP file does not contain a manifest file (manifest.csv)";
                ref.errors.add(FileErrorEntity.builder().errorMessage(message).fileCsvName("manifest").build());
            } else {
                Map<String, String> manifestData;
                try (InputStream ignored = zipFile.getInputStream(manifestEntry)) {
                    manifestData = oneRosterCsvService.validateManifest(zipFile, tempFiles.get("manifest.csv"), ref.errors);
                }

                tempFiles.forEach((key, value) -> {
                    try {
                        log.info("validating file: " + key);
                        oneRosterValidator.validator(value, ref.errors, manifestData.get("file." + key.replace(".csv", "")), key);
                    } catch (CsvValidationException | IOException e) {
                        throw new RuntimeException(e);
                    }
                });

//            validate enrollment && orgs
                long orgsErrors = ref.errors.stream().filter(fileErrorEntity -> "orgs".equals(fileErrorEntity.getFileCsvName())).count();
                long enrollmentsErrors = ref.errors.stream().filter(fileErrorEntity -> "enrollments".equals(fileErrorEntity.getFileCsvName())).count();
                long classesErrors = ref.errors.stream().filter(fileErrorEntity -> "classes".equals(fileErrorEntity.getFileCsvName())).count();
                long usersErrors = ref.errors.stream().filter(fileErrorEntity -> "users".equals(fileErrorEntity.getFileCsvName())).count();
                if (tempFiles.get("enrollments.csv") != null && tempFiles.get("orgs.csv") != null
                        && enrollmentsErrors == 0 && orgsErrors == 0)
                    oneRosterValidator.validateOrgsExtended(tempFiles.get("enrollments.csv"), tempFiles.get("orgs.csv"), ref.errors, "enrollments");

                if (tempFiles.get("classes.csv") != null && tempFiles.get("orgs.csv") != null
                        && classesErrors == 0 && orgsErrors == 0)
                    oneRosterValidator.validateOrgsExtended(tempFiles.get("classes.csv"), tempFiles.get("orgs.csv"), ref.errors, "classes");

                if (tempFiles.get("users.csv") != null && tempFiles.get("classes.csv") != null
                        && usersErrors == 0 && classesErrors == 0)
                    oneRosterValidator.validateUsersExtended(tempFiles.get("users.csv"), tempFiles.get("classes.csv"), ref.errors, "users");


            }
        }

        FileUploadEntity fileUploadEntity = FileUploadEntity.builder()
                .fileName(file.getOriginalFilename())
                .fileSize(file.getSize())
                .valid(true)
                .build();

        if (!(ref.errors.size() > 0)) {
            fileUploadEntity.setStatus("SUCCESS");
            ZonedDateTime endTime = LocalDateTime.now().atZone(ZoneOffset.UTC);
            fileUploadEntity.setTimeProcessed(endTime.toInstant().toEpochMilli() - startTime.toInstant().toEpochMilli());
            fileUploadRepository.save(fileUploadEntity);
            List<UserRecord> records = new CsvToBeanBuilder<UserRecord>(new FileReader(tempFiles.get("users.csv")))
                    .withType(UserRecord.class)
                    .withSkipLines(1)
                    .build()
                    .parse();
            List<UserEntity> userEntities = records.stream().map(userRecord -> {
                UserEntity userEntity = userMapper.dtoToEntity(userRecord);
                userEntity.setFileUploadEntity(fileUploadEntity);
                return userEntity;
            }).collect(Collectors.toList());

            userRepository.saveAll(userEntities);
            responseDto.setSuccessRecords(userEntities.size());
        } else {
            fileUploadEntity.setStatus("FAILURE");
            fileUploadEntity.setErrors(ref.errors);
            ZonedDateTime endTime = LocalDateTime.now().atZone(ZoneOffset.UTC);
            fileUploadEntity.setTimeProcessed(endTime.toInstant().toEpochMilli() - startTime.toInstant().toEpochMilli());
            fileUploadRepository.save(fileUploadEntity);
            ref.errors = ref.errors.stream().peek(error -> error.setFileUploadEntity(fileUploadEntity)).collect(Collectors.toList());
            errorRepository.saveAll(ref.errors);
            responseDto.setErrors(ref.errors);
        }
        return responseDto;
    }

    @Override
    public SearchResult<FileDto> getPage(PageRequest pageRequest) {
        Page<FileDto> fileDtoPage = this.getAllFiles(pageRequest).map(fileUploadMapper::entityToDto);
        SearchResult<FileDto> searchResult = new SearchResult<>();
        searchResult.setPage(fileDtoPage);
        return searchResult;
    }
}
