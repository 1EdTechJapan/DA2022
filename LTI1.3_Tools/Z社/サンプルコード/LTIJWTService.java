import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.JwsHeader;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SigningKeyResolverAdapter;

import java.io.IOException;
import java.net.URL;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.security.PublicKey;
import java.text.ParseException;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;

import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.jwk.AsymmetricJWK;
import com.nimbusds.jose.jwk.JWK;
import com.nimbusds.jose.jwk.JWKSet;

/**
 *
 */
public class LTIJWTService {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(LTIJWTService.class);

    /**
     * ステートをデコードする
     *
     * @param state ステート
     * @return デコードされたステート
     */
    public Jws<Claims> validateState(String state) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + state + ")");
        return Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {
            // This is done because each state is signed with a different key based on the issuer... so
            // we don't know the key and we need to check it pre-extracting the claims and finding the kid
            @Override
            public Key resolveSigningKey(JwsHeader header, Claims claims) {
                PublicKey toolPublicKey;
                try {
                    toolPublicKey = OAuthUtils.loadPublicKey(EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_OWN_PUBLIC_KEY));
                } catch (GeneralSecurityException e) {
                	logger.error("Error validating the state. Error generating the tool public key", e);
                    return null;
                }
                return toolPublicKey;
            }
        }).parseClaimsJws(state);
    }


    /**
     * JWTをデコードする
     *
     * @param jwt JWT
     * @return デコードされたJWT
     */
    public Jws<Claims> validateJWT(String jwt) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + jwt + ")");

        return Jwts.parser().setSigningKeyResolver(new SigningKeyResolverAdapter() {

            @Override
            public Key resolveSigningKey(JwsHeader header, Claims claims) {
                if (!StringUtils.isEmpty(EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_JWKS_ENDPOINT))) {
                    try {
                        JWKSet publicKeys = JWKSet.load(new URL(EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_JWKS_ENDPOINT)));
                        JWK jwk = publicKeys.getKeyByKeyId(header.getKeyId());
                        return ((AsymmetricJWK) jwk).toPublicKey();
                    } catch (JOSEException | ParseException | IOException e) {
                    	logger.info("pylti1p3.exception.LtiException:Unable to find public key");
                    	logger.error("Error getting the iss public key", e);
                        return null;
                    } catch (NullPointerException e) {
                    	logger.info("pylti1p3.exception.LtiException:JWT KID not found");
                    	logger.error("Kid not found in header", e);
                        return null;
                    }
                } else {
                	logger.error("The platform configuration must contain a valid JWKS");
                    return null;
                }

            }
        }).parseClaimsJws(jwt);
    }
}
