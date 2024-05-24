package com.group.oneroster.web.controllers.view.admin;

import com.group.oneroster.service.UserService;
import com.group.oneroster.service.searching.SearchParameters;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Slf4j
@Controller
@RequestMapping("/adminPage")
@RequiredArgsConstructor
public class UsersController {
    private final UserService userService;

    @GetMapping("/users")
    public ModelAndView getUsers(ModelAndView modelAndView, SearchParameters searchParams) {
        modelAndView = userService.filter(modelAndView, searchParams);
        modelAndView.setViewName("adminPage/user/users");
        return modelAndView;
    }

}
