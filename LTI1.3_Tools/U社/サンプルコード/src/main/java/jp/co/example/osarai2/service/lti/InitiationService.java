package jp.co.example.osarai2.service.lti;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.databind.ObjectMapper;

import jp.co.example.osarai2.data.lti.InitiationRequestData;
import jp.co.example.osarai2.data.lti.InitiationResponseData;

/**
 * LTIログイン初期処理Service
 */
@Service
public class InitiationService {

    @Autowired
    private ObjectMapper mapper;

    /**
     * ログイン初期処理Mapを作成します
     *
     * @param data
     * @return ログイン初期処理Map
     */
    @SuppressWarnings("unchecked")
    public Map<String, String> createResponse(InitiationRequestData data) {
        InitiationResponseData response = new InitiationResponseData(data);
        return mapper.convertValue(response, Map.class);
    }



}
