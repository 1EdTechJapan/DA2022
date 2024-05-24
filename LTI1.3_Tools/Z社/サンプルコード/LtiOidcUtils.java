import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.security.GeneralSecurityException;
import java.security.Key;
import java.util.Date;
import java.util.Map;

import org.apache.commons.lang.time.DateUtils;
import org.apache.log4j.Logger;

/**
 * 
 */
public final class LtiOidcUtils {

	/** ステートの有効期限 */
	private static final int EXPIRATION_TIME = 3600;
	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(LtiOidcUtils.class);


	/**
	 * ユーティリティクラスのためprivateで宣言
	 */
	private LtiOidcUtils() {}

	/**
	 * JWTステートを生成する
	 *
	 * @param ownPrivateKey 秘密鍵
	 * @param authRequestMap リクエスト情報のマップ
	 * @param loginInitiationDTO プラットフォーム情報を格納したインスタンス
	 * @param clientIdValue プラットフォームのクライアントID
	 * @param deploymentIdValue プラットフォームのデプロイメントID
	 * @return JWTステート
	 * @throws GeneralSecurityException セキュリティ例外
	 */
    public static synchronized String generateState(String ownPrivateKey, Map<String, String> authRequestMap, OidcLoginInitiationDTO loginInitiationDTO, String clientIdValue, String deploymentIdValue)
    		throws GeneralSecurityException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", clientIdValue, deploymentIdValue) + ")");

        Date date = new Date();
        Key issPrivateKey = OAuthUtils.loadPrivateKey(ownPrivateKey);
        String state = Jwts.builder()
                .setHeaderParam("kid", "OWNKEY")
                .setHeaderParam("typ", "JWT")
                .setIssuer(CommonLtiDefine.LTI_PROVIDER_NAME)
                .setSubject(loginInitiationDTO.getIss())
                .setAudience(clientIdValue)
                .setExpiration(DateUtils.addSeconds(date, EXPIRATION_TIME))
                .setNotBefore(date)
                .setIssuedAt(date)
                .setId(authRequestMap.get("nonce"))
                .claim("original_iss", loginInitiationDTO.getIss())
                .claim("loginHint", loginInitiationDTO.getLoginHint())
                .claim("ltiMessageHint", loginInitiationDTO.getLtiMessageHint())
                .claim("targetLinkUri", loginInitiationDTO.getTargetLinkUri())
                .claim("clientId", clientIdValue)
                .claim("ltiDeploymentId", deploymentIdValue)
                .claim("controller", "/lti_oidc")
                .signWith(SignatureAlgorithm.RS256, issPrivateKey)
                .compact();
        logger.info("decoded state is : " + Jwts.parser().setSigningKey(issPrivateKey).parseClaimsJws(state).toString());
        logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : encoded state is : " + state);
        return state;
    }
}
