package com.group.oneroster.web.controllers.view;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;


@Controller
@RequestMapping("")
public class IndexController {

    @GetMapping(value = {"/"})
    public String index() {
        return "redirect:/adminPage/users";
    }

    @GetMapping(value = "/login")
    public String login() {
        return "website/login";
    }

}
