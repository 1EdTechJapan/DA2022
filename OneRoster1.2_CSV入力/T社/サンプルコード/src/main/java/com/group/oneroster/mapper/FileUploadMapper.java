package com.group.oneroster.mapper;


import com.group.oneroster.persistence.domain.FileErrorEntity;
import com.group.oneroster.persistence.domain.FileUploadEntity;
import com.group.oneroster.web.dto.FileDto;
import com.group.oneroster.web.dto.FileErrorDto;
import org.mapstruct.Mapper;
import org.mapstruct.NullValueCheckStrategy;
import org.mapstruct.NullValueMappingStrategy;
import org.mapstruct.NullValuePropertyMappingStrategy;

@Mapper(
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE,
        componentModel = "spring",
        nullValueCheckStrategy = NullValueCheckStrategy.ALWAYS,
        nullValueMappingStrategy = NullValueMappingStrategy.RETURN_NULL
)
public interface FileUploadMapper {
    FileDto entityToDto(FileUploadEntity source);

    FileErrorDto fileErrorEntityToDto(FileErrorEntity source);
}
