package jp.co.example.osarai2.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import lombok.Getter;




/**
 * application.yml取得用クラス
 */
@Component("ApplicationConfig")
public class ApplicationConfig {

    /**
     * LTI プラットフォームID
     */
    @Getter
    @Value("${settings.lti.id.platform}")
    private String ltiPlatformId;

    /**
     * LTI デプロイメントID
     */
    @Getter
    @Value("${settings.lti.id.deployment}")
    private String ltiDeploymentId;

    /**
     * LTI クライアントID
     */
    @Getter
    @Value("${settings.lti.id.client}")
    private String ltiClientId;

    /**
     * LTI プラットフォームOICD認証URL
     */
    @Getter
    @Value("${settings.lti.url.oidc-auth}")
    private String ltiOidcAuthUrl;

    /**
     * LTI クライアント起動URL
     */
    @Getter
    @Value("${settings.lti.url.launch}")
    private String ltiLaunchUrl;

    /**
     * LTI jwks URL
     */
    @Getter
    @Value("${settings.lti.url.jwks}")
    private String ltiJwksUrl;




}
