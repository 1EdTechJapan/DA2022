package com.group.oneroster.web.dto;


import lombok.AccessLevel;
import lombok.Data;
import lombok.experimental.FieldDefaults;
import org.apache.logging.log4j.util.Strings;

import java.util.Optional;

@Data
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserDto {
    Long id;
    String loginId;
    String username;
    String sourceId;
    String email;
    String familyName;
    String givenName;
    String role;
    String identifier;
    String orgSourcedIds;
    String name;
    String grades;
    String classSourcedId;
    String title;
    String fileUploadId;

    public String getAvatarText() {
        return Strings.toRootUpperCase(String.valueOf(Optional.of(username.charAt(0)).orElse(randomCharacters())));
    }

    public String getFullName() {
        return String.format("%s %s", givenName, familyName);
    }

    public String getAvatarColor() {
        String[] array = {"danger", "warning", "success", "dark", "primary", "info"};
        return array[(int) (Math.random() * array.length)];
    }

    private Character randomCharacters() {
        return (char) (Math.random() * 26 + 'A');
    }
}
