package com.group.oneroster.web.dto;

import com.group.oneroster.persistence.domain.FileErrorEntity;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.List;


@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UploadFileResponseDto {

    Boolean fileUploadSuccess;

    Integer successRecords;

    List<FileErrorEntity> errors;

}
