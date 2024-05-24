import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;

/*******************************************************************************
 * LTIレスポンス格納用DTO
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * ※SSOにおいて使用しない項目はコメントアウト
 * </pre>
 ******************************************************************************/

@Slf4j
@Getter
@Setter
public class LTI3RequestDto {

  private String iss;
  private String aud;
  private Date iat;
  private Date exp;
  private String sub;
  private String azp;

//  https://purl.imsglobal.org/spec/lti/claim/message_type
  private String ltiMessageType;
//  https://purl.imsglobal.org/spec/lti/claim/version
  private String ltiVersion;
//  https://purl.imsglobal.org/spec/lti/claim/deployment_id
  private String ltiDeploymentId;

//  given_name
  private String ltiGivenName;
//  family_name
  private String ltiFamilyName;
//  middle_name
  private String ltiMiddleName;
//  picture
  private String ltiPicture;
//  email
  private String ltiEmail;
//  name
  private String ltiName;

//  https://purl.imsglobal.org/spec/lti/claim/roles
  private List<String> ltiRoles;
//  https://purl.imsglobal.org/spec/lti/claim/role_scope_mentor
  private List<String> ltiRoleScopeMentor;
//  https://purl.imsglobal.org/spec/lti/claim/resource_link
  private Map<String, Object> ltiResourceLink;
//    private String ltiLinkId;
//    private String ltiLinkTitle;
//    private String ltiLinkDescription;

//  https://purl.imsglobal.org/spec/lti/claim/context
  private Map<String, Object> ltiContext;
//    private String ltiContextId;
//    private String ltiContextTitle;
//    private String ltiContextLabel;
//    private List<String> ltiContextType;

//  https://purl.imsglobal.org/spec/lti/claim/tool_platform
  private Map<String, Object> ltiToolPlatform;
//    private String ltiToolPlatformName;
//    private String ltiToolPlatformContactEmail;
//    private String ltiToolPlatformDesc;
//    private String ltiToolPlatformUrl;
//    private String ltiToolPlatformFamilyCode;
//    private String ltiToolPlatformVersion;
//    private String ltiToolPlatformGuid;

//  https://purl.imsglobal.org/spec/lti-ags/claim/endpoint
  private Map<String, Object> ltiEndpoint;
//    private List<String> ltiEndpointScope;
//    private String ltiEndpointLineItems;

//  https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice
  private Map<String, Object> ltiNamesRoleService;
//    private String ltiNamesRoleServiceContextMembershipsUrl;
//    private List<String> ltiNamesRoleServiceVersions;

//  https://purl.imsglobal.org/spec/lti-ces/claim/caliper-endpoint-service
  private Map<String, Object> ltiCaliperEndpointService;
//    private List<String> ltiCaliperEndpointServiceScopes;
//    private String ltiCaliperEndpointServiceUrl;
//    private String ltiCaliperEndpointServiceSessionId;

  private String nonce;
  private String locale;

//  https://www.example.com/extension
  private Map<String, Object> ltiExtension;
//  https://purl.imsglobal.org/spec/lti/claim/custom
  private Map<String, Object> ltiCustom;
  // LTI実証実験では以下の値をoptionalで定義
  // grade 学習eポータル上でユーザーごとに登録された学年コード
  // classname 学習eポータル上でユーザーごとに割り当てられた主所属クラスの文字列

//  https://purl.imsglobal.org/spec/lti/claim/target_link_uri
  private String ltiTargetLinkUrl;

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
  public LTI3RequestDto() {
  }

  /**
   * ***************************************************************************
   * LTI3RequestDto
   * <pre>
   * [機能説明]
   * 1.
   * [注意事項]
   * （無し）
   * @param jws id_token
   * </pre>
   ***************************************************************************
   */
  public LTI3RequestDto(Jws<Claims> jws) {
    this.iss = jws.getBody().getIssuer();
    this.aud = jws.getBody().getAudience();
    this.iat = jws.getBody().getIssuedAt();
    this.exp = jws.getBody().getExpiration();
    this.sub = jws.getBody().getSubject();
    this.azp = getStringFromLTIRequest(jws, "azp");
    this.ltiMessageType = getStringFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/message_type");
    this.ltiVersion = getStringFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/version");
    this.ltiDeploymentId = getStringFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/deployment_id");
    this.ltiGivenName = getStringFromLTIRequest(jws, "given_name");
    this.ltiFamilyName = getStringFromLTIRequest(jws, "family_name");
    this.ltiMiddleName = getStringFromLTIRequest(jws, "middle_name");
    this.ltiPicture = getStringFromLTIRequest(jws, "picture");
    this.ltiEmail = getStringFromLTIRequest(jws, "email");
    this.ltiName = getStringFromLTIRequest(jws, "name");
    this.ltiRoles = getListFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/roles");
    this.ltiRoleScopeMentor = getListFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/role_scope_mentor");
    this.ltiResourceLink = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/resource_link");
    this.ltiContext = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/context");
    this.ltiToolPlatform = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/tool_platform");
    this.ltiEndpoint = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint");
    this.ltiNamesRoleService = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice");
    this.ltiCaliperEndpointService = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti-ces/claim/caliper-endpoint-service");
    this.nonce = getStringFromLTIRequest(jws, "nonce");
    this.locale = getStringFromLTIRequest(jws, "locale");
    this.ltiExtension = getMapFromLTIRequest(jws, "https://www.example.com/extension");
    this.ltiCustom = getMapFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/custom");
    this.ltiTargetLinkUrl = getStringFromLTIRequest(jws, "https://purl.imsglobal.org/spec/lti/claim/target_link_uri");
  }

  /**
   * ***************************************************************************
   * getStringFromLTIRequest
   * <pre>
   * [機能説明]
   * 1.id_tokenのclaimからString形式で値を取得する
   * [注意事項]
   * （無し）
   * @param jws id_token
   * @param stringToGet mapのkey
   * </pre>
   ***************************************************************************
   */
  private String getStringFromLTIRequest(Jws<Claims> jws, String stringToGet) {
      if (jws.getBody().containsKey(stringToGet) && jws.getBody().get(stringToGet) != null) {
          return jws.getBody().get(stringToGet, String.class);
      } else {
          return null;
      }
  }

  /**
   * ***************************************************************************
   * getListFromLTIRequest
   * <pre>
   * [機能説明]
   * 1.id_tokenのclaimからList<String>形式で値を取得する
   * [注意事項]
   * （無し）
   * @param jws id_token
   * @param listToGet mapのkey
   * </pre>
   ***************************************************************************
   */
  @SuppressWarnings("unchecked")
  private List<String> getListFromLTIRequest(Jws<Claims> jws, String listToGet) {
      if (jws.getBody().containsKey(listToGet)) {
          try {
              return jws.getBody().get(listToGet, List.class);
          } catch (Exception ex) {
            log.error("No map integer when expected in: " + listToGet + ". Returning null");
              return new ArrayList<>();
          }
      } else {
          return new ArrayList<>();
      }
  }

  /**
   * ***************************************************************************
   * getMapFromLTIRequest
   * <pre>
   * [機能説明]
   * 1.id_tokenのclaimからMap<String, Object>形式で値を取得する
   * [注意事項]
   * （無し）
   * @param jws id_token
   * @param mapToGet mapのkey
   * </pre>
   ***************************************************************************
   */
  @SuppressWarnings("unchecked")
  private Map<String, Object> getMapFromLTIRequest(Jws<Claims> jws, String mapToGet) {
      if (jws.getBody().containsKey(mapToGet)) {
          try {
              return jws.getBody().get(mapToGet, Map.class);
          } catch (Exception ex) {
              log.error("No map integer when expected in: {0}. Returning null", mapToGet);
              return new HashMap<>();
          }
      } else {
          return new HashMap<>();
      }
  }

}
