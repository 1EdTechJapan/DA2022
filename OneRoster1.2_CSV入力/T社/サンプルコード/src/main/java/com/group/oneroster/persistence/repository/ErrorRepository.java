package com.group.oneroster.persistence.repository;

import com.group.oneroster.persistence.domain.FileErrorEntity;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ErrorRepository extends PagingAndSortingRepository<FileErrorEntity, Long>, JpaSpecificationExecutor<FileErrorEntity> {
}
