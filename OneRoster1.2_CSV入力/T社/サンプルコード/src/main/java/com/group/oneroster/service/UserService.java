package com.group.oneroster.service;

import com.group.oneroster.mapper.UserMapper;
import com.group.oneroster.persistence.domain.UserEntity;
import com.group.oneroster.persistence.repository.UserRepository;
import com.group.oneroster.service.searching.SearchResult;
import com.group.oneroster.web.dto.UserDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService extends BaseService<UserDto> {
    private final UserMapper userMapper;
    private final UserRepository userRepository;

    public Page<UserEntity> getAllUsers(PageRequest pageRequest) {
        return userRepository.findAll(pageRequest);
    }

    public SearchResult<UserDto> getPage(PageRequest pageRequest) {
        Page<UserDto> userDtoPage = this.getAllUsers(pageRequest).map(userMapper::entityToDto);
        SearchResult<UserDto> searchResult = new SearchResult<>();
        searchResult.setPage(userDtoPage);
        return searchResult;
    }
}
