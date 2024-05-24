package jp.co.example.programming.data.lti;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;

import com.auth0.jwt.interfaces.Claim;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import jp.co.example.programming.definition.lti_request;
import jp.co.example.programming.validation.constraints.ResourceLink;
import lombok.Data;




/**
 * LTIツール起動リクエストデータ
 */
@Data
@JsonIgnoreProperties(ignoreUnknown = false)
@ResourceLink
public class ResourceLinkData {

    @NotEmpty
    private String iss;

    private String sub;

    @NotEmpty
    private List<String> aud;

    @NotNull
    private Date exp;

    @NotNull
    private Date iat;

    @NotEmpty
    private String nonce;

    @NotEmpty
    private String messageType;

    @NotEmpty
    private String version;

    @NotEmpty
    private List<String> roles;

    @NotEmpty
    private String deploymentId;

    @NotEmpty
    private String contextId;

    @NotEmpty
    private String resourceLinkId;

    @NotEmpty
    private String targetLinkUri;

    private String toolPlatformGuid;

    private String customGrade;

    private String name;



    //------------------------------------------------------------------
    //- constructor
    //------------------------------------------------------------------

    /**
     * ResourceLinkDataを作成します。
     *
     * @param jwt
     */
    public ResourceLinkData(DecodedJWT jwt) {
        // JWT reserved
        iss = jwt.getIssuer();
        sub = jwt.getSubject();
        aud = jwt.getAudience();
        exp = jwt.getExpiresAt();
        iat = jwt.getIssuedAt();

        // root
        Map<String, Claim> claims = jwt.getClaims();
        nonce         = getClaimAsString(claims, lti_request.KEY_LINK_NONCE);
        messageType   = getClaimAsString(claims, lti_request.KEY_LINK_MESSAGE_TYPE);
        version       = getClaimAsString(claims, lti_request.KEY_LINK_VERSION);
        roles         = getClaimAsList(claims, lti_request.KEY_LINK_ROLES);
        deploymentId  = getClaimAsString(claims, lti_request.KEY_LINK_DEPLOYMENT_ID);
        targetLinkUri = getClaimAsString(claims, lti_request.KEY_LINK_TARGET_LINK_URI);
        name          = getClaimAsString(claims, lti_request.KEY_LINK_NAME);

        // context
        Map<String, Object> contextMap = getClaimAsMap(claims, lti_request.KEY_LINK_CONTEXT);
        contextId = getStringFromMap(contextMap, lti_request.KEY_LINK_CONTEXT_ID);

        // resource link
        Map<String, Object> resourceLinkMap = getClaimAsMap(claims, lti_request.KEY_LINK_RESOURCE_LINK);
        resourceLinkId = getStringFromMap(resourceLinkMap, lti_request.KEY_LINK_RESOURCE_LINK_ID);

        // tool platform
        Map<String, Object> toolPlatformMap = getClaimAsMap(claims, lti_request.KEY_LINK_TOOL_PLATFORM);
        toolPlatformGuid = getStringFromMap(toolPlatformMap, lti_request.KEY_LINK_TOOL_PLATFORM_GUID);

        // custom
        Map<String, Object> customMap = getClaimAsMap(claims, lti_request.KEY_LINK_CUSTOM);
        customGrade = getStringFromMap(customMap, lti_request.KEY_LINK_CUSTOM_GRADE);
    }



    //------------------------------------------------------------------
    //- private methods
    //------------------------------------------------------------------

    /**
     * 指定keyのClaimをStringで取得します。
     * Claimが存在しない場合はnullを返却します。
     *
     * @param claims
     * @param key
     * @return String型のClaim
     */
    private String getClaimAsString(Map<String, Claim> claims, String key) {
        Claim c = claims.get(key);
        return c != null ? c.asString() : null;
    }

    /**
     * 指定keyのClaimをMap<String,Object>で取得します。
     * Claimが存在しない場合は空のMapを返却します。
     *
     * @param claims
     * @param key
     * @return Map<String, Object>型のClaim
     */
    private Map<String, Object> getClaimAsMap(Map<String, Claim> claims, String key) {
        Claim c = claims.get(key);
        return c != null ? c.asMap() : new HashMap<String, Object>();
    }

    /**
     * 指定keyのClaimをList<String>で取得します。
     * Claimが存在しない場合は空のList<String>を返却します。
     *
     * @param claims
     * @param key
     * @return List<String>型のClaim
     */
    private List<String> getClaimAsList(Map<String, Claim> claims, String key) {
        Claim c = claims.get(key);
        return c != null ? c.asList(String.class) : new ArrayList<String>();
    }

    /**
     * Mapから指定keyの要素をStringで取得します。
     * 指定keyの要素が無い場合はnullを返却します。
     *
     * @param map
     * @param key
     * @return String要素
     */
    private String getStringFromMap(Map<String, Object> map, String key) {
        Object obj = map.get(key);
        return obj != null ? obj.toString() : null;
    }

}
