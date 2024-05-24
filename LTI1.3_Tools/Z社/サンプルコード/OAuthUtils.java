import java.security.GeneralSecurityException;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

import org.apache.log4j.Logger;

/**
 * 
 */
public final class OAuthUtils {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(OAuthUtils.class);

	/**
	 * ユーティリティクラスのためprivateで宣言
	 */
    private OAuthUtils() {}

    /**
     * 公開鍵の成型を行う
     *
     * @param key 公開鍵の文字列
     * @return 成型された公開鍵文字列
     * @throws GeneralSecurityException セキュリティ例外
     */
    public static synchronized RSAPublicKey loadPublicKey(String key) throws GeneralSecurityException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
        String publicKeyContent = key.replace("\\n", "").replace("\n", "").replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "");
        KeyFactory kf = KeyFactory.getInstance("RSA");
        X509EncodedKeySpec keySpecX509 = new X509EncodedKeySpec(Base64.getDecoder().decode(publicKeyContent));
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
        return (RSAPublicKey) kf.generatePublic(keySpecX509);
    }

    /**
     * 秘密鍵の成型を行う
     *
     * @param privateKeyPem 秘密鍵の文字列
     * @return 成型された秘密鍵文字列
     * @throws GeneralSecurityException セキュリティ例外
     */
    public static synchronized PrivateKey loadPrivateKey(String privateKeyPem) throws GeneralSecurityException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
        // PKCS#8 format
        String pemPrivateStart = "-----BEGIN PRIVATE KEY-----";
        String pemPrivateEnd = "-----END PRIVATE KEY-----";

        // PKCS#8 format
        if (privateKeyPem.contains(pemPrivateStart)) {
            privateKeyPem = privateKeyPem.replace(pemPrivateStart, "").replace(pemPrivateEnd, "");
            privateKeyPem = privateKeyPem.replaceAll("\\s", "");
            byte[] pkcs8EncodedKey = Base64.getDecoder().decode(privateKeyPem);
            KeyFactory factory = KeyFactory.getInstance("RSA");
            return factory.generatePrivate(new PKCS8EncodedKeySpec(pkcs8EncodedKey));
        }

		logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " Not supported format of a private key");
        throw new GeneralSecurityException("Not supported format of a private key");
    }
}
