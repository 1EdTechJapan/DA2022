/**
 * *****************************************************************************
 * LTI用constantsクラス
 * <pre>
 * [機能説明]
 * 1.LTIで使用する固定値を定義する。
 * [注意事項]
 * (なし)
 * </pre>
 *
 *****************************************************************************
 */

public class LtiStringConstants {

  /**
   * インスタンスを生成する。
   * <pre>
   * [機能説明]
   * 1.外部からインスタンス化されることを防ぐため、private宣言する。
   * [注意事項]
   * (なし)
   * </pre>
   */
  private LtiStringConstants() {
  }


  /**
   * LTIに使用されるstateを保持するcookie名
   */
  public static final String LTI_STATE_COOKIE = "lti_state_cookie";

  /**
   * LTIに使用されるnonceを保持するcookie名
   */
  public static final String LTI_NONCE_COOKIE = "lti_nonce_cookie";


  /**
   * リダイレクトに使用するパラメータ(Claim)
   */

  /**
   * iss
   */
  public static final String ISS = "iss";

  /**
   * client_id
   */
  public static final String CLIENT_ID = "client_id";

  /**
   * lti_deployment_id
   */
  public static final String LTI_DEPLOYMENT_ID = "lti_deployment_id";

  /**
   * login_hint
   */
  public static final String LOGIN_HINT = "login_hint";

  /**
   * target_link_uri
   */
  public static final String TARGET_LINK_URL = "target_link_uri";

  /**
   * lti_message_hint
   */
  public static final String LTI_MESSAGE_HINT = "lti_message_hint";

  /**
   * nonce
   */
  public static final String NONCE = "nonce";

  /**
   * prompt
   */
  public static final String PROMPT = "prompt";

  /**
   * redirect_uri
   */
  public static final String REDIRECT_URL = "redirect_uri";

  /**
   * response_mode
   */
  public static final String RESPONSE_MODE = "response_mode";

  /**
   * response_type
   */
  public static final String RESPONSE_TYPE = "response_type";

  /**
   * scope
   */
  public static final String SCOPE = "scope";

  /**
   * state
   */
  public static final String STATE = "state";

  /**
   * oidc_endpoint
   */
  public static final String OIDC_END_POINT = "oidc_endpoint";

  /**
   * oidc_endpoint_complete
   */
  public static final String OIDC_END_POINT_COMPLETE = "oidc_endpoint_complete";

  /**
   * kid
   */
  public static final String KID = "kid";

  /**
   * typ
   */
  public static final String TYP = "typ";

  /**
   * original_iss
   */
  public static final String ORIGINAL_ISS = "original_iss";

  /**
   * controller
   */
  public static final String CONTROLLER = "controller";



  /**
   * リソース起動時に使用するパラメータ(Claim)
   */

  /**
   * id_token
   */
  public static final String ID_TOKEN = "id_token";

  /**
   * https://purl.imsglobal.org/spec/lti/claim/version
   */
  public static final String LTI_VERSION = "1.3.0";

  /**
   * https://purl.imsglobal.org/spec/lti/claim/message_type
   */
  public static final String LTI_MESSAGE_TYPE = "LtiResourceLinkRequest";

}
