import java.io.IOException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.X509EncodedKeySpec;
import java.text.ParseException;
import java.util.Base64;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.servlet.http.HttpServletRequest;

import com.google.common.hash.Hashing;
import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.jwk.AsymmetricJWK;
import com.nimbusds.jose.jwk.JWK;
import com.nimbusds.jose.jwk.JWKSet;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.JwsHeader;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SigningKeyResolverAdapter;
// 独自処理のimport割愛
import lombok.extern.slf4j.Slf4j;


/**
 * *****************************************************************************
 * LTI用ユーティリティ
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * (なし)
 * </pre>
 *
 *****************************************************************************
 */
@Slf4j
public final class LtiUtility {

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
  private LtiUtility() {
  }

  /**
   * ***************************************************************************
   * validateState
   * <pre>
   * [機能説明]
   * 1.stateをシステムの公開鍵で復号する
   * [注意事項]
   * (なし)
   * @param state リクエストから取得したstate
   * @return 復号したstate
   * </pre>
   ***************************************************************************
   */
  public static Jws<Claims> validateState(String state) {
      return Jwts.parserBuilder().setSigningKeyResolver(new SigningKeyResolverAdapter() {
        @Override
        public Key resolveSigningKey(@SuppressWarnings("rawtypes") JwsHeader header, Claims claims) {
            PublicKey toolPublicKey;
            try {
              // ymlから公開鍵を取得
                toolPublicKey = loadPublicKey(ApplicationContext.getAppLtiConfig().getPublickey());
            } catch (GeneralSecurityException ex) {
                log.error("Error validating the state. Error generating the tool public key", ex);
                return null;
            }
            return toolPublicKey;
        }
    }).build().parseClaimsJws(state);
  }

  /**
   * ***************************************************************************
   * loadPublicKey
   * <pre>
   * [機能説明]
   * 1.公開鍵を生成する
   * [注意事項]
   * (なし)
   * @param key 公開鍵(String)
   * @return RSAPublicKey
   * </pre>
   ***************************************************************************
   */
  private static RSAPublicKey loadPublicKey(String key) throws GeneralSecurityException {
      String publicKeyContent = key.replace("\\n", "").replace("\n", "").replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace(" ", "");
      KeyFactory kf = KeyFactory.getInstance("RSA");
      X509EncodedKeySpec keySpecX509 = new X509EncodedKeySpec(Base64.getDecoder().decode(publicKeyContent));
      return (RSAPublicKey) kf.generatePublic(keySpecX509);
  }

  /**
   * ***************************************************************************
   * validateJWT
   * <pre>
   * [機能説明]
   * 1.id_tokenから取得したjwtを、プラットフォームのキーセットで復号する
   * [注意事項]
   * (なし)
   * @param jwt id_token(String)
   * @param ltiJwksEndPoint キーセットを取得するエンドポイント
   * @return id_token(Jws)
   * </pre>
   ***************************************************************************
   */
  public static Jws<Claims> validateJWT(String jwt, String ltiJwksEndPoint) {


      return Jwts.parserBuilder().setSigningKeyResolver(new SigningKeyResolverAdapter() {

          @Override
          public Key resolveSigningKey(@SuppressWarnings("rawtypes") JwsHeader header, Claims claims) {
              // JWKのエンドポイント
              if (!StringUtility.isBlankOrNull(ltiJwksEndPoint)) {
                  try {
                      JWKSet publicKeys = JWKSet.load(new URL(ltiJwksEndPoint));
                      JWK jwk = publicKeys.getKeyByKeyId(header.getKeyId());
                      return ((AsymmetricJWK) jwk).toPublicKey();
                  } catch (JOSEException | ParseException | IOException
                      ex) {
                      log.error("Error getting the iss public key", ex);
                      return null;
                  } catch (NullPointerException ex) {
                      log.error("Kid not found in header", ex);
                      return null;
                  }
              } else {
                  log.error("The platform configuration must contain a valid JWKS");
                  return null;
              }
          }
      }).build().parseClaimsJws(jwt);
  }

  /**
   * ***************************************************************************
   * varidateRequest
   * <pre>
   * [機能説明]
   * 1.復号したid_tokenのClaimについて、1EdTech Security Frameworkに基づいた入力チェックを行う
   * 2.復号したid_tokenのClaimについて、Learning Tools Interoperability Core Specification と,
   *  LTI実証実験に基づいた入力チェックを行う
   * [注意事項]
   * (なし)
   * @param lti3Request id_tokenから取得したClaimのDTO
   * @param request リクエスト
   * @param ltiPlatformApiRes 独自処理で取得したプラットフォームの情報
   * @see https://www.imsglobal.org/spec/security/v1p0/#id-token
   * @see https://www.imsglobal.org/spec/lti/v1p3
   * </pre>
   ***************************************************************************
   */
  public static void varidateRequest(LTI3RequestDto lti3Request,
        HttpServletRequest request, MappingManageLtiPlatformApiRes ltiPlatformApiRes) {

    // https://www.imsglobal.org/spec/security/v1p0/#id-token
    // 1EdTech Security Frameworkに基づくバリデーションチェック

    // iss
    if (StringUtility.isBlankOrNull(lti3Request.getIss())) {
      throw new IllegalStateException("iss is null");
    }
    if (!StringUtility.isEqual(ltiPlatformApiRes.getLtiPlatformId(), lti3Request.getIss())) {
      throw new IllegalStateException("iss is not the expected value");
    }

    // aud
    if (StringUtility.isBlankOrNull(lti3Request.getAud())) {
      throw new IllegalStateException("aud is null");
    }
    // audにクライアントIDが含まれていない時
    if (!lti3Request.getAud().contains(ltiPlatformApiRes.getLtiClientId())
        // azp(optional)
        && (StringUtility.isBlankOrNull(lti3Request.getAzp())
            || !StringUtility.isEqual(ltiPlatformApiRes.getLtiClientId(), lti3Request.getAzp()))) {
      throw new IllegalStateException("aud or azp is not the expected value");
    }

    // exp
    if (lti3Request.getExp() == null) {
      throw new IllegalStateException("exp is null");
    }

    // iat
    if (lti3Request.getIat() == null) {
      throw new IllegalStateException("iat is null");
    }
    // 独自処理
    // iatが一定時間より前に作られている、または、未来の値が設定されている場合はエラー

    // nonce
    if (StringUtility.isBlankOrNull(lti3Request.getNonce())) {
      throw new IllegalStateException("Nonce = null in the JWT or in the session.");
    }
    String cookieNonce = CookieUtility.getCookieValue(request, LtiStringConstants.LTI_NONCE_COOKIE);
    String cookieNonceHash = Hashing.sha256()
      .hashString(cookieNonce, StandardCharsets.UTF_8)
      .toString();
    if (!StringUtility.isEqual(cookieNonceHash, lti3Request.getNonce())) {
      throw new IllegalStateException("Unknown nonce.");
    }

    // https://www.imsglobal.org/spec/lti/v1p3
    // Learning Tools Interoperability Core Specification と LTI実証実験に基づくバリデーションチェック

    // UUID version4 形式チェック用正規表現(LTI事象実験)
    Pattern pUUID = Pattern.compile("([0-9a-f]{8})-([0-9a-f]{4})-4([0-9a-f]{3})-([0-9a-f]{4})-([0-9a-f]{12})");

    // sub
    if (StringUtility.isBlankOrNull(lti3Request.getSub())) {
      // 本システムでは匿名起動時はエラー画面に遷移するため、sub未設定はエラーとする。
      throw new IllegalStateException("sub is null");
    }
    // sub uuid version4 形式チェック(LTI実証実験)
    Matcher mSub = pUUID.matcher(lti3Request.getSub());
    if (!mSub.find()) {
      throw new IllegalStateException("sub is not UUID version4");
    }

    // lti_version
    if (StringUtility.isBlankOrNull(lti3Request.getLtiVersion())) {
      throw new IllegalStateException("ltiVersion is null");
    }
    if (!StringUtility.isEqual(LtiStringConstants.LTI_VERSION, lti3Request.getLtiVersion())) {
      throw new IllegalStateException("ltiVersion is not the expected value");
    }

    // lti_message_type
    if (StringUtility.isBlankOrNull(lti3Request.getLtiMessageType())) {
      throw new IllegalStateException("messageType is null");
    }
    if (!StringUtility.isEqual(LtiStringConstants.LTI_MESSAGE_TYPE, lti3Request.getLtiMessageType())) {
      throw new IllegalStateException("messageType is not the expected value");
    }

    // lti_deployment_id
    if (StringUtility.isBlankOrNull(lti3Request.getLtiDeploymentId())) {
      throw new IllegalStateException("deploymentId is null");
    }
    String ltiDeploymentIdPrefix = lti3Request.getLtiDeploymentId().split("_")[0];
    // 独自処理
    // LTI実証実験で定義されていデプロイメントIDの接頭辞をDBから取得し、Map<String, String> prefixMapを作成する。
    if (!prefixMap.containsValue(ltiDeploymentIdPrefix)) {
      throw new IllegalStateException("deploymentId is not the expected value");
    }

    // target_link_url
    if (StringUtility.isBlankOrNull(lti3Request.getLtiTargetLinkUrl())) {
      throw new IllegalStateException("targetLinkUrl is null");
    }

    // resource_link
    if (lti3Request.getLtiResourceLink().isEmpty() || lti3Request.getLtiResourceLink().size() == 0) {
      throw new IllegalStateException("resourceLink is null");
    }
    if (StringUtility.isBlankOrNull(lti3Request.getLtiResourceLink().get("id").toString())) {
      throw new IllegalStateException("resourceLink.id is null");
    }

    // role
    // 本システムでは匿名起動時はエラー画面に遷移するため、role = nullはエラーとする。
    if (lti3Request.getLtiRoles().isEmpty()) {
      throw new IllegalStateException("ltiRole is null");
    } else {
    // 独自処理
    // システムで許可されるroleをDBから取得し、Map<String, String> roleMapを作成する。
    // 連携されたロールがroleMapに含まれない場合、エラー
      boolean roleFound = false;
      for (String role : lti3Request.getLtiRoles()) {
        if (roleMap.containsValue(role)) {
          roleFound = true;
        }
      }
      if (!roleFound) {
        throw new IllegalStateException("ltiRole is not the expected value");
      }
    }

    // context(LTI実装実験ではrequired 指定されているときはidが必須)
    if (lti3Request.getLtiContext().isEmpty() || lti3Request.getLtiContext().size() == 0) {
      throw new IllegalStateException("ltiContextis null");
    }
    if (StringUtility.isBlankOrNull(lti3Request.getLtiContext().get("id").toString())) {
      throw new IllegalStateException("ltiContext.id is null");
    }

    // tool_platform(optional 指定されている時はguidが必要)
    if (!lti3Request.getLtiToolPlatform().isEmpty() && lti3Request.getLtiToolPlatform().size() != 0) {
      if (StringUtility.isBlankOrNull(lti3Request.getLtiToolPlatform().get("guid").toString())) {
        throw new IllegalStateException("tool_platform.guid is null");
      }
    }

    // custom.grade(optional)
    if (!lti3Request.getLtiCustom().isEmpty() && lti3Request.getLtiCustom().size() != 0
        && Objects.nonNull(lti3Request.getLtiCustom().get("grade"))) {
      // 独自処理
      // LTI実証実験で定義されている学年をDBから取得し、Map<String, String> gradeMapを作成する。
      // 学年がLTI実証実験で定義されている形式に合致するか確認する
      if (!gradeMap.containsValue(lti3Request.getLtiCustom().get("grade").toString())) {
        throw new IllegalStateException("custom.grade is not the expected value");
      }
    }

  }


}
