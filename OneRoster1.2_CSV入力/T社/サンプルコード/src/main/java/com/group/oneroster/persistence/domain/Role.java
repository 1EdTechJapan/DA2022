package com.group.oneroster.persistence.domain;


import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum Role {
    ADMINISTRATOR("Administrator"), TEACHER("Teacher"), STUDENT("Student");

    private final String value;

}
