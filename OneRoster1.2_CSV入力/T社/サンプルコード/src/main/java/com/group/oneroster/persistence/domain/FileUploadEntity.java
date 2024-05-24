package com.group.oneroster.persistence.domain;


import lombok.*;
import lombok.experimental.FieldDefaults;

import javax.persistence.*;
import java.util.List;

@Entity
@Table(name = "file_upload")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Builder
public class FileUploadEntity extends AuditableEntity<String> {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    Long id;

    @Column(name = "file_name")
    String fileName;

    @Column(name = "file_size")
    Long fileSize;

    @Column(name = "type")
    String type;

    @Column(name = "status")
    String status;

    @Column(name = "valid")
    Boolean valid;

    @Lob
    private byte[] data;

    @Column(name = "time_processed")
    Long timeProcessed;

    @OneToMany(mappedBy = "fileUploadEntity", cascade = CascadeType.ALL)
    List<UserEntity> users;

    @OneToMany(mappedBy = "fileUploadEntity", cascade = CascadeType.ALL)
    List<FileErrorEntity> errors;
}
