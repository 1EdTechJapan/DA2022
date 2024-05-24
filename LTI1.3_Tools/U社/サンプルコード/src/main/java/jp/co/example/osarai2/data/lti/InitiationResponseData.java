package jp.co.example.osarai2.data.lti;

import java.util.UUID;

import org.springframework.beans.BeanUtils;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import lombok.Data;
import lombok.EqualsAndHashCode;




/**
 * LTI初期処理レスポンスデータ
 */
@Data
@EqualsAndHashCode(callSuper = false)
@JsonIgnoreProperties(ignoreUnknown = true)
public class InitiationResponseData extends InitiationBaseData {

    private String response_type = "id_token";

    private String response_mode = "form_post";

    private String scope = "openid";

    private String prompt = "none";

    private String redirect_uri;

    private String state;

    private String nonce = "testware_default_nonce";



    //------------------------------------------------------------------
    //- コンストラクタ
    //------------------------------------------------------------------

    /**
     * LtiOidcAuthDataを作成します。
     *
     * @param data LtiInitiationData
     */
    public InitiationResponseData(InitiationRequestData data) {
        BeanUtils.copyProperties(data, this);
        redirect_uri = data.getTarget_link_uri();
        state        = createUUIDString();
    }



    //------------------------------------------------------------------
    //- private methods
    //------------------------------------------------------------------

    /**
     * UUID文字列を作成します
     *
     * @return UUID文字列
     */
    private String createUUIDString() {
        return UUID.randomUUID().toString();
    }


}
