import javax.servlet.http.HttpServletRequest;

import lombok.Getter;
import lombok.Setter;

/*******************************************************************************
 * OIDC認証用DTO
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * (なし)
 * </pre>
 ******************************************************************************/

@Getter
@Setter
public class OIDCLoginInitiationDto{

  private String iss;
  private String loginHint;
  private String targetLinkUri;
  private String ltiMessageHint;
  private String clientId;
  private String deploymentId;

  /**
  * ***************************************************************************
  * インスタンスを生成する。
  * <pre>
  * [機能説明]
  * 1.外部からインスタンス化されることを防ぐため、private宣言する。
  * [注意事項]
  * (なし)
  * </pre>
  ***************************************************************************
  */
  public OIDCLoginInitiationDto() {
  }

  /**
   * ***************************************************************************
   * OIDCLoginInitiationDto
   * <pre>
   * [機能説明]
   * 1.
   * [注意事項]
   * （無し）
   * @param iss
   * @param loginHint
   * @param targetLinkUri
   * @param ltiMessageHint
   * @param clientId
   * @param deploymentId
   * </pre>
   ***************************************************************************
   */
  public OIDCLoginInitiationDto(String iss, String loginHint, String targetLinkUri, String ltiMessageHint, String clientId, String deploymentId) {
      this.iss = iss;
      this.loginHint = loginHint;
      this.targetLinkUri = targetLinkUri;
      this.ltiMessageHint = ltiMessageHint;
      this.clientId = clientId;
      this.deploymentId = deploymentId;
  }

  /**
   * ***************************************************************************
   * OIDCLoginInitiationDto
   * <pre>
   * [機能説明]
   * 1.
   * [注意事項]
   * （無し）
   * @param req リクエスト
   * </pre>
   ***************************************************************************
   */
  public OIDCLoginInitiationDto(HttpServletRequest req) {
    this(req.getParameter("iss"),
            req.getParameter("login_hint"),
            req.getParameter("target_link_uri"),
            req.getParameter("lti_message_hint"),
            req.getParameter("client_id"),
            req.getParameter("lti_deployment_id")
    );
  }
}
