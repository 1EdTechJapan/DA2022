import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.Security;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.apache.commons.lang3.time.DateUtils;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.util.UriComponentsBuilder;

import com.google.common.hash.Hashing;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
// 独自処理import
import lombok.extern.slf4j.Slf4j;

/**
 * *****************************************************************************
 * OIDCログイン開始Service実装クラス
 *
 * <pre>
 * [機能説明]
  * 1.OIDCから呼び出され、プラットフォームに求められる認証情報を返却する。
 * [注意事項]
 * (なし)
 * </pre>
 *****************************************************************************
 */

@Slf4j
@Service
public class OIDCServiceImpl implements OIDCService{

  /**
   * ***************************************************************************
   * OIDCログインを開始する
   * <pre>
   * [機能説明]
   * 1.リダイレクトに必要な情報を作成する
   * [注意事項]
   * (なし)
   * </pre>
   * @param oidcLoginInitiationDto OIDC認証用DTO
   * @return リダイレクト情報のmap
   ***************************************************************************
   */
  @Override
  public Map<String, String> initiation(OIDCLoginInitiationDto oidcLoginInitiationDto) throws IOException, GeneralSecurityException {

    // client_id (optional)
    String clientIdValue = oidcLoginInitiationDto.getClientId();
    // deployment_id (optional)
    String deploymentIdValue = oidcLoginInitiationDto.getDeploymentId();

    // 独自処理
    // APIを介して、DBからリクエストに紐づくプラットフォームの情報を取得する
    // clientIdValue、deploymentIdValueの有無によってAPIの引数を変更する
    // 取得結果をMappingManageLtiPlatformApiRes resEntityに格納する
    if (resEntity == null) {
      throw new IllegalStateException("LTI Platform dosen't found");
    }

    // ログインリクエストにclientIdが含まれないとき、APIから取得した値に更新する
    if (StringUtility.isBlankOrNull(clientIdValue)) {
      clientIdValue = resEntity.getLtiClientId();
    }

    // リダイレクト情報のmapを返却する
    return generateAuthRequestPayload(oidcLoginInitiationDto, clientIdValue
        , deploymentIdValue, resEntity.getLtiOidcEndPoint());

  }

  /**
   * ***************************************************************************
   * generateAuthRequestPayload
   * <pre>
   * [機能説明]
   * 1.リダイレクトに必要な情報を生成し、返却する
   * [注意事項]
   * (なし)
   * </pre>
   * @param oidcLoginInitiationDto OIDC認証用DTO
   * @param clientIdValue clientId
   * @param deploymentIdValue deploymentId
   * @param oidcEndpoint リダイレクト先URL
   * @return リダイレクト情報のmap
   ***************************************************************************
   */
  private Map<String, String> generateAuthRequestPayload(OIDCLoginInitiationDto oidcLoginInitiationDto,
      String clientIdValue, String deploymentIdValue, String oidcEndpoint) throws GeneralSecurityException, IOException {
    Map<String, String> authRequestMap = new HashMap<>();

    // nonceの生成
    String nonce = UUID.randomUUID().toString();
    String nonceHash = Hashing.sha256()
            .hashString(nonce, StandardCharsets.UTF_8)
            .toString();
    authRequestMap.put(LtiStringConstants.NONCE, nonce);

    // stateの生成
    String state = generateState(authRequestMap, oidcLoginInitiationDto, clientIdValue, deploymentIdValue);
    authRequestMap.put(LtiStringConstants.STATE, state);

    // redirect_urlの生成
    MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
    queryParams.add(LtiStringConstants.CLIENT_ID, clientIdValue);
    queryParams.add(LtiStringConstants.LOGIN_HINT, oidcLoginInitiationDto.getLoginHint());
    if (!StringUtility.isBlankOrNull(oidcLoginInitiationDto.getLtiMessageHint())) {
      queryParams.add(LtiStringConstants.LTI_MESSAGE_HINT, oidcLoginInitiationDto.getLtiMessageHint());
    }
    queryParams.add(LtiStringConstants.NONCE, nonceHash);
    queryParams.add(LtiStringConstants.PROMPT, "none");//規定値
    queryParams.add(LtiStringConstants.REDIRECT_URL, "{ドメイン}/lti/launches" );// 起動用のURL
    queryParams.add(LtiStringConstants.RESPONSE_MODE, "form_post");//規定値
    queryParams.add(LtiStringConstants.RESPONSE_TYPE, "id_token");//規定値
    queryParams.add(LtiStringConstants.SCOPE, "openid");//規定値
    queryParams.add(LtiStringConstants.STATE, state);


    String url = UriComponentsBuilder
        .fromUriString(oidcEndpoint)
        .queryParams(queryParams)
        .build()
        .encode()
        .toUriString();
    log.info(url);

    authRequestMap.put(LtiStringConstants.OIDC_END_POINT_COMPLETE, url);

    return authRequestMap;

  }

  /**
   * ***************************************************************************
   * generateState
   * <pre>
   * [機能説明]
   * 1.stateをJwt形式で作成する
   * [注意事項]
   * (なし)
   * </pre>
   * @param authRequestMap リダイレクト情報のmap
   * @param oidcLoginInitiationDto OIDC認証用DTO
   * @param clientIdValue clientId
   * @param deploymentIdValue deploymentId
   * @return state
   ***************************************************************************
   */
  private String generateState(Map<String, String> authRequestMap, OIDCLoginInitiationDto oidcLoginInitiationDto, String clientIdValue, String deploymentIdValue) throws GeneralSecurityException {
    Date date = DateUtility.getSystemDate();
    // ymlから秘密鍵を取得
    Key issPrivateKey = loadPrivateKey(ApplicationContext.getAppLtiConfig().getPrivatekey());
    // stateに設定する項目は、後のバリデーションチェックでの必要に応じて任意に追加できる。
    String state = Jwts.builder()
            .setHeaderParam(LtiStringConstants.KID, "OWNKEY")
            .setHeaderParam(LtiStringConstants.TYP, "JWT")
            .setIssuer("システム名")
            .setSubject(oidcLoginInitiationDto.getIss())
            .setAudience(clientIdValue)
            .setExpiration(DateUtils.addSeconds(date, 3600))
            .setNotBefore(date)
            .setIssuedAt(date)
            .setId(authRequestMap.get(LtiStringConstants.NONCE))
            .claim(LtiStringConstants.ORIGINAL_ISS, oidcLoginInitiationDto.getIss())
            .claim(LtiStringConstants.LOGIN_HINT, oidcLoginInitiationDto.getLoginHint())
            .claim(LtiStringConstants.LTI_MESSAGE_HINT, oidcLoginInitiationDto.getLtiMessageHint())
            .claim(LtiStringConstants.TARGET_LINK_URL, oidcLoginInitiationDto.getTargetLinkUri())
            .claim(LtiStringConstants.CLIENT_ID, clientIdValue)
            .claim(LtiStringConstants.LTI_DEPLOYMENT_ID, deploymentIdValue)
            .claim(LtiStringConstants.CONTROLLER, "/oidc/login_initiations")
            .signWith(issPrivateKey, SignatureAlgorithm.RS256)  //署名
            .compact();
    log.debug("State: \n {} \n", state);
    return state;
}


  /**
   * ***************************************************************************
   * loadPrivateKey
   * <pre>
   * [機能説明]
   * 1.秘密鍵を生成する
   * [注意事項]
   * (なし)
   * </pre>
   * @param privateKeyPem 秘密鍵(String)
   * @return PrivateKey
   ***************************************************************************
   */
  private static PrivateKey loadPrivateKey(String privateKeyPem) throws GeneralSecurityException {
      // PKCS#8 format
      final String PEM_PRIVATE_START = "-----BEGIN RSA PRIVATE KEY-----";
      final String PEM_PRIVATE_END = "-----END RSA PRIVATE KEY-----";

      Security.addProvider(
          new BouncyCastleProvider()
          );

      if (privateKeyPem.contains(PEM_PRIVATE_START)) { // PKCS#8 format
          privateKeyPem = privateKeyPem.replace(PEM_PRIVATE_START, "").replace(PEM_PRIVATE_END, "");
          privateKeyPem = privateKeyPem.replaceAll("\\s", "");
          byte[] pkcs8EncodedKey = Base64.getDecoder().decode(privateKeyPem);
          KeyFactory factory = KeyFactory.getInstance("RSA");
          return factory.generatePrivate(new PKCS8EncodedKeySpec(pkcs8EncodedKey));
      }

      throw new GeneralSecurityException("Not supported format of a private key");
  }

}
