package com.group.oneroster.web.dto;

import lombok.Data;
import lombok.RequiredArgsConstructor;

import java.text.DecimalFormat;
import java.time.LocalDateTime;
import java.util.List;

@Data
@RequiredArgsConstructor
public class FileDto {
    Long id;
    String fileName;
    Long fileSize;
    String type;
    String status;
    Boolean valid;
    LocalDateTime updatedAt;
    List<FileErrorDto> errors;

    public String readableFileSize() {
        if (this.fileSize <= 0) return "0";
        final String[] units = new String[]{"B", "kB", "MB", "GB", "TB"};
        int digitGroups = (int) (Math.log10(this.fileSize) / Math.log10(1024));
        return new DecimalFormat("#,##0.#").format(this.fileSize / Math.pow(1024, digitGroups)) + " " + units[digitGroups];
    }

    public String getLinkDownloadLog() {
        return String.format("/api/v1/files/%s/download-log", this.id);
    }

}
