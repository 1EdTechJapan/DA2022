package com.group.oneroster.mapper;


import com.group.oneroster.persistence.domain.UserEntity;
import com.group.oneroster.web.dto.UserDto;
import com.group.oneroster.web.dto.UserRecord;
import org.mapstruct.*;

@Mapper(
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE,
        componentModel = "spring",
        nullValueCheckStrategy = NullValueCheckStrategy.ALWAYS,
        nullValueMappingStrategy = NullValueMappingStrategy.RETURN_NULL
)
public interface UserMapper {

    @Mapping(target = "fileUploadId", source = "fileUploadEntity.id")
    @Mapping(target = "role", source = "role.value")
    UserDto entityToDto(UserEntity entity);


    @Mapping(target = "loginId", source = "sourcedId")
    @Mapping(target = "role", ignore = true)
    @Mapping(target = "orgSourcedIds", source = "agentSourcedIds")
    @Mapping(target = "name", ignore = true)
    @Mapping(target = "classSourcedId", ignore = true)
    UserEntity dtoToEntity(UserRecord userRecord);
}
