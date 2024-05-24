package com.group.oneroster.service;


import com.group.oneroster.service.searching.SearchParameters;
import com.group.oneroster.service.searching.SearchResult;
import com.group.oneroster.web.paging.Pager;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.web.servlet.ModelAndView;

import static com.group.oneroster.web.paging.InitialPagingSizes.*;
import static org.springframework.data.domain.PageRequest.of;
import static org.springframework.data.domain.Sort.Direction.DESC;

public abstract class BaseService<U> {

    public ModelAndView filter(ModelAndView modelAndView, SearchParameters searchParams) {
        int selectedPageSize = searchParams.getPageSize().orElse(INITIAL_PAGE_SIZE);
        int selectedPage = (searchParams.getPage().orElse(0) < 1) ? INITIAL_PAGE : (searchParams.getPage().get() - 1);
        PageRequest pageRequest = of(selectedPage, selectedPageSize, Sort.by(DESC, "id"));

        if (searchParams.getPropertyValue().isEmpty() || searchParams.getPropertyValue().get().isEmpty()) {

        } else {
            modelAndView.addObject("property", searchParams.getProperty().get());
            modelAndView.addObject("propertyValue", searchParams.getPropertyValue().get());
        }
        SearchResult<U> searchResult = getPage(pageRequest);

        Pager pager = new Pager(searchResult.getPage().getTotalPages(),
                searchResult.getPage().getNumber(),
                BUTTONS_TO_SHOW,
                searchResult.getPage().getTotalElements());
        modelAndView.addObject("pager", pager);
        modelAndView.addObject("items", searchResult.getPage());
        modelAndView.addObject("selectedPageSize", selectedPageSize);
        modelAndView.addObject("pageSizes", PAGE_SIZES);
        return modelAndView;
    }

    public abstract SearchResult<U> getPage(PageRequest pageRequest);
}
