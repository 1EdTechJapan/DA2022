package com.CompanyName.lti.controller;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.oidc.user.DefaultOidcUser;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequiredArgsConstructor
public class IndexController {
    private final Logger log = LoggerFactory.getLogger(IndexController.class);

    @RequestMapping({"/",})
    public String index(Model model) {
        DefaultOidcUser user = (DefaultOidcUser) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        model.addAttribute("user", user);
        log.info("user: {}", user.getName());
        return "index";
    }
}
