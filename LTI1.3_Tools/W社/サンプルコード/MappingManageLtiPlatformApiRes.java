import lombok.Data;

/**
 * *****************************************************************************
 * LTIプラットフォーム
 *
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * (なし)
 * </pre>
 *****************************************************************************
 */

@Data

public class MappingManageLtiPlatformApiRes {

  /** LTI Platform SK */
  // システム内でのプラットフォーム識別子
  private Integer ltiPlatformKey;

  /** LTI Platform ID */
  private String ltiPlatformId;

  /** LTI Platform 名称 */
  private String ltiPlatformName;

  /** LTI Cliant ID */
  private String ltiClientId;

  /** LTI Deployment ID */
  private String ltiDeploymentId;

  /** LTI Oidc End Point */
  private String ltiOidcEndPoint;

  /** LTI Jwks End Point */
  private String ltiJwksEndPoint;

  /** LTI Oath2 Token Url */
  private String ltiOauth2TokenUrl;

}
