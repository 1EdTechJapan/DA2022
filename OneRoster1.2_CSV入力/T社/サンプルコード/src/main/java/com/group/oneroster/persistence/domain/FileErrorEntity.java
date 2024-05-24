package com.group.oneroster.persistence.domain;


import lombok.*;
import lombok.experimental.FieldDefaults;

import javax.persistence.*;

@Entity
@Table(name = "file_error")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Builder
public class FileErrorEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    Long id;

    @Column(name = "file_csv_name")
    String fileCsvName;

    @Column(name = "field_name")
    String fieldName;

    @Column(name = "error_message")
    String errorMessage;

    @ManyToOne
    @JoinColumn(name = "file_upload_id")
    FileUploadEntity fileUploadEntity;

    @Override
    public String toString() {
        return String.format("fileCsvName=%s, fieldName=%s, hasError=%s", fileCsvName, fieldName, errorMessage);
    }
}
