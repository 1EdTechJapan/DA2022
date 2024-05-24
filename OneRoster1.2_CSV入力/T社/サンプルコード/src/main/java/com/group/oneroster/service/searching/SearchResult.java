package com.group.oneroster.service.searching;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.domain.Page;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class SearchResult<T> {
    private Page<T> page;
    private boolean numberFormatException;
}
