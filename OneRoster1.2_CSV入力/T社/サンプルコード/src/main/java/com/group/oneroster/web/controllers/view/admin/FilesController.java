package com.group.oneroster.web.controllers.view.admin;

import com.group.oneroster.service.FileService;
import com.group.oneroster.service.searching.SearchParameters;
import com.group.oneroster.web.dto.UploadFileResponseDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

@Slf4j
@Controller
@RequestMapping("/adminPage")
@RequiredArgsConstructor
public class FilesController {

    private final FileService fileService;

    private static final List<String> files = List.of(
            "manifest",
            "users",
            "academicSessions",
            "classes",
            "courses",
            "demographics",
            "enrollments",
            "orgs",
            "roles",
            "userProfiles");

    @GetMapping("/files")
    public ModelAndView getFiles(ModelAndView modelAndView, SearchParameters searchParams) {
        modelAndView = fileService.filter(modelAndView, searchParams);
        modelAndView.setViewName("adminPage/file/files");
        return modelAndView;
    }

    @GetMapping("/files/errors")
    public ModelAndView getErrors(ModelAndView modelAndView) {
        modelAndView.setViewName("adminPage/file/errors");
        return modelAndView;
    }

    @PostMapping("/files/upload")
    public String uploadFile(@RequestParam("file") MultipartFile file, RedirectAttributes attributes) {
        try {
            UploadFileResponseDto responseDto = fileService.handleUploadFiles(file);
            if (Objects.nonNull(responseDto.getErrors())) {
                attributes.addFlashAttribute("fileName", file.getOriginalFilename());
                for (String fileName : files) {
                    attributes.addFlashAttribute(fileName + "Errors", responseDto.getErrors().stream().filter(fileErrorEntity -> fileErrorEntity.getFileCsvName().equals(fileName)).collect(Collectors.toList()));
                }
                return "redirect:/adminPage/files/errors";
            } else {
                attributes.addFlashAttribute("message", String.format("Imported %s users", responseDto.getSuccessRecords()));
            }
        } catch (Exception e) {
            attributes.addFlashAttribute("error", e.getMessage());
        }
        return "redirect:/adminPage/files";
    }
}
