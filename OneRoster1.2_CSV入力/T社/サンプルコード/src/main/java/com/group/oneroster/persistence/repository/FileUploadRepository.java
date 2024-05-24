package com.group.oneroster.persistence.repository;

import com.group.oneroster.persistence.domain.FileUploadEntity;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FileUploadRepository extends PagingAndSortingRepository<FileUploadEntity, Long>, JpaSpecificationExecutor<FileUploadEntity> {
}
