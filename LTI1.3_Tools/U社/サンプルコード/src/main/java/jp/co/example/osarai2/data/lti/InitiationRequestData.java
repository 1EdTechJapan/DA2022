package jp.co.example.osarai2.data.lti;

import javax.validation.constraints.NotEmpty;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import lombok.Data;
import lombok.EqualsAndHashCode;




/**
 * LTI初期処理リクエストデータ
 */
@Data
@EqualsAndHashCode(callSuper = false)
@JsonIgnoreProperties(ignoreUnknown = false)
public class InitiationRequestData extends InitiationBaseData {

    @NotEmpty
    private String iss;

    @NotEmpty
    private String target_link_uri;

    private String lti_deployment_id;

}
