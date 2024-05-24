package jp.co.example.osarai2.data.lti;

import javax.validation.constraints.NotEmpty;

import lombok.Data;




/**
 * LTI初期処理通信基底データ
 */
@Data
public class InitiationBaseData {

    @NotEmpty
    protected String login_hint;

    protected String lti_message_hint;

    protected String client_id;

}
