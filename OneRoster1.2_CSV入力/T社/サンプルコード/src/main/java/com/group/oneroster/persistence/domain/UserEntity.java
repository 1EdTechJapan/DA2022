package com.group.oneroster.persistence.domain;

import lombok.*;
import lombok.experimental.FieldDefaults;

import javax.persistence.*;


@Entity
@Table(name = "users")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserEntity extends AuditableEntity<String> {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    Long id;

    @Column(name = "login_id")
    String loginId;

    @Column(name = "username")
    String username;

    @Column(name = "source_id")
    String sourceId;

    @Column(name = "email")
    String email;

    @Column(name = "family_name")
    String familyName;

    @Column(name = "given_name")
    String givenName;
    @Column(name = "role")
    @Enumerated(EnumType.STRING)
    Role role;

    @Column(name = "identifier")
    String identifier;

    @Column(name = "org_sourced_ids")
    String orgSourcedIds;

    @Column(name = "name")
    String name;

    @Column(name = "grades")
    String grades;

    @Column(name = "class_sourced_id")
    String classSourcedId;

    @Column(name = "title")
    String title;

    @ManyToOne
    @JoinColumn(name = "file_upload_id")
    FileUploadEntity fileUploadEntity;

    @Override
    public String toString() {
        return String.format("User [id=%s, loginId=%s, username=%s, sourceId=%s, email=%s, familyName=%s, givenName=%s, role=%s, identifier=%s, orgSourcedIds=%s, name=%s, grades=%s, classSourcedId=%s, title=%s]",
                id != null ? id.toString() : "null",
                loginId != null ? loginId : "null",
                username != null ? username : "null",
                sourceId != null ? sourceId : "null",
                email != null ? email : "null",
                familyName != null ? familyName : "null",
                givenName != null ? givenName : "null",
                role != null && role.getValue() != null ? role.getValue() : "null",
                identifier != null ? identifier : "null",
                orgSourcedIds != null ? orgSourcedIds : "null",
                name != null ? name : "null",
                grades != null ? grades : "null",
                classSourcedId != null ? classSourcedId : "null",
                title != null ? title : "null");
    }
}
