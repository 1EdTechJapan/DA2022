package com.group.oneroster.web.dto;


import lombok.Data;
import lombok.RequiredArgsConstructor;

@Data
@RequiredArgsConstructor
public class FileErrorDto {
    Long id;

    String errorCode;

    String errorMessage;

}
