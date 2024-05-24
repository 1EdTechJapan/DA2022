package jp.co.example.osarai2.service.lti;

import java.net.URL;
import java.security.interfaces.RSAPublicKey;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.validation.Validator;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.auth0.jwk.GuavaCachedJwkProvider;
import com.auth0.jwk.Jwk;
import com.auth0.jwk.UrlJwkProvider;
import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;

import jp.co.example.osarai2.config.ApplicationConfig;
import jp.co.example.osarai2.data.lti.ResourceLinkData;
import jp.co.example.springboot.validation.ValidationUtility;

/**
 * LTIツール起動Service
 */
@Service
public class LaunchService {

    @Autowired
    private ApplicationConfig config;

    @Autowired
    private Validator validator;

    /**
     * トークンの検証を行います
     * 検証失敗時は例外をthrowします
     *
     * @param token
     */
    public DecodedJWT verifyToken(HttpServletRequest request, HttpSession session, String token) {
        // token検証
        try {
            // tokenからKeyIDを取得
            DecodedJWT jwt = JWT.decode(token);
            String kid = jwt.getKeyId();

            // jwks URLから公開鍵を取得
            URL url = new URL(config.getLtiJwksUrl());
            UrlJwkProvider provider = new UrlJwkProvider(url);
            GuavaCachedJwkProvider cachedProvider = new GuavaCachedJwkProvider(provider);
            Jwk jwk = cachedProvider.get(kid);
            RSAPublicKey publicKey = (RSAPublicKey)jwk.getPublicKey();

            // 署名検証
            Algorithm algorithm = Algorithm.RSA256(publicKey, null);
            JWTVerifier verifier = JWT.require(algorithm)
                .withIssuer(config.getLtiPlatformId())
                .build();
            verifier.verify(token);

            return jwt;

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }


    /**
     * 学習者のログインを行います
     * 対象の学習者が存在しない場合は作成します
     *
     * @param jwt
     * @return user
     */
    public void /* User */ loginUser(DecodedJWT jwt) {
        try {
            // データ生成と検証
            ResourceLinkData linkData = new ResourceLinkData(jwt);
            ValidationUtility.ifHasErrorThrow(validator, linkData);

            // 匿名認証判定（sub = null）
            String sub = linkData.getSub();
            boolean isAnonymousUser = sub == null;

            // 教室情報取得
            // 匿名認証の場合は空の学習者に体験用教室を設定して返却
            // 自社独自領域のため詳細は割愛

            // 学習者が存在しない場合は登録、存在する場合は更新して返却
            // 自社独自領域のため詳細は割愛
            // return user;

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }




}
