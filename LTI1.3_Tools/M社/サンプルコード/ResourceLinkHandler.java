
import java.security.KeyFactory;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.regex.Pattern;

import org.apache.commons.codec.digest.DigestUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.maven.surefire.shared.lang3.exception.ExceptionUtils;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.Claim;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;

import io.fusionauth.jwks.JSONWebKeyBuilderException;
import io.fusionauth.jwks.JSONWebKeySetHelper;
import io.fusionauth.jwks.domain.JSONWebKey;
import software.amazon.awssdk.http.HttpStatusCode;

/**
 * AWS Lambda 受信ハンドラクラス<br>
 * LTI連携開始要求
 * 
 *
 */
public class ResourceLinkHandler extends BaseHandler<LtiLinkDto>
        /* BaseHandlerは
         * RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent>
         * をインプリメントしています
         *  */

{

    /**
     * LTI連携開始要求
     */
    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent input, Context context)
    {

        // 応答解析処理
        LtiLinkDto request = null;
        try
        {
            request = validate(input);
            if (request == null)
            {
                return response(HttpStatusCode.BAD_REQUEST, new ApplicationException( "The session is invalid."));
            }
        }
        catch (Exception e)
        {
            return response(HttpStatusCode.INTERNAL_SERVER_ERROR, e);

        }

        // JWTをデコードし、検証する
        DecodedJWT jwt = null;
        try
        {
            jwt = decode(request);
        }
        catch (JSONWebKeyBuilderException 
                | JwksException 
                | InvalidKeySpecException e)
        {
            return response(HttpStatusCode.BAD_REQUEST, e);
        }
        catch (JWTVerificationException e)
        {
            return response(HttpStatusCode.BAD_REQUEST, e);
        }
        catch (ApplicationException e)
        {
            return response(HttpStatusCode.BAD_REQUEST, e);
        }
        catch (Exception e)
        {
            return response(HttpStatusCode.INTERNAL_SERVER_ERROR, e);
        }
        if (jwt == null)
        {
            return response(HttpStatusCode.BAD_REQUEST, new ApplicationException("The JWT is invalid."));
        }

        // 必須クレームの確認
        try {
            parse(jwt);
        }
        catch (AnonymousLaunchException e) {
            anonymousLaunch = true;
        }
        catch (ApplicationException e) {
            return response(HttpStatusCode.BAD_REQUEST, e);
        }
        catch (Exception e)
        {
            return response(HttpStatusCode.INTERNAL_SERVER_ERROR, e);
        }

        // 自社独自領域のため詳細は割愛
        // https://purl.imsglobal.org/spec/lti/claim/rolesに指定されるroleをツールが解釈可能なものに変換する
        // リクエスト許可の判定を行う

        // LTI ResourceLinkローンチ処理
        APIGatewayProxyResponseEvent output = new APIGatewayProxyResponseEvent();

        LaunchDto dto = new LaunchDto(jwt.getSubject(), jwt.getIssuer(), role);
        HashMap<String, String> headers = null;
        try
        {
            if (anonymousLaunch) {
                headers = HttpUtility.setRedirectLocation(jwt.getClaim(LtiUtility.CLAIM_TARGET_LINK_URI).asString(), dto.defaultParam());
            }
            else {
                headers = HttpUtility.setRedirectLocation(jwt.getClaim(LtiUtility.CLAIM_TARGET_LINK_URI).asString(),
                        dto.toString());
            }
        }
        catch (Exception e)
        {
            return response(HttpStatusCode.INTERNAL_SERVER_ERROR, e);
        }

        output.setStatusCode(HttpStatusCode.MOVED_TEMPORARILY);
        output.setHeaders(headers);

        return output;

    }

    /**
     * 応答解析処理
     * 
     * @param input 受信パラメータ
     * @return null : 失敗<br>
     *         上記以外 : 成功
     */
    @Override
    protected LtiLinkDto validate(Map<String, String> input)
    {
        // 自社独自領域のため詳細は割愛
        // 受信パラメータを検証する
        // セッション情報を取得する

        return null;
    }
    
    /**
     * JWTをデコードし、検証する
     * 
     * @param input LTI連携情報
     * @return null : 失敗(alg値不正)<br>
     *         上記以外 : 成功(JWT情報)
     * @throws Exception 失敗(上記以外)
     */
    private DecodedJWT decode(LtiLinkDto input) throws Exception
    {
        DecodedJWT jwt = JWT.decode(input.getIdToken());
        
        if ((jwt.getAlgorithm() == null) || (!jwt.getAlgorithm().equals(OidcUtility.JWT_HEADER_ALG)))
        {
            // alg値が「RS256」以外の場合は、エラー応答し、処理を終了する：
            return null;
        }
        
        
        // 自社独自領域のため詳細は割愛
        // 公開鍵を取得する

        // 検証
        Algorithm algorithm = Algorithm.RSA256(rsaPublicKey, null);
        JWTVerifier verifier = JWT.require(algorithm)
            // iss
            .withIssuer(input.getSession().getIss())
            // aud
            .withAnyOfAudience(input.getSession().getClientId())
            // nonce
            .withClaim(OidcUtility.CLAIM_NONCE, input.getSession().getNonce())
            // message_type
            .withClaim(LtiUtility.CLAIM_MESSAGE_TYPE, LtiUtility.CLAIMVAL_MSGTYPE_RESOURCE_LINK)
            // version
            .withClaim(LtiUtility.CLAIM_VERSION, LtiUtility.CLAIMVAL_LTI_VERSION)
            // target_link_uri
            .withClaim(LtiUtility.CLAIM_TARGET_LINK_URI, input.getSession().getTargetLinkUrl())
            .build();
        
        jwt = verifier.verify(input.getIdToken());

        // expとiatは未定義の場合、verifyで検証されないのでここで確認する
        if (jwt.getExpiresAt() == null) {
            throw new LtiException(String.format(OidcUtility.ERROR_MISSING, OidcUtility.CLAIM_EXP));
        }
        if (jwt.getIssuedAt() == null) {
            throw new LtiException(String.format(OidcUtility.ERROR_MISSING, OidcUtility.CLAIM_IAT));
        }

        Calendar cal = DateTimeUtility.getCalendar(input.getSession().getRequestedDatetime());
        // リクエスト発行日時より古かったらエラーにする。タイマー誤差を考慮して、1分過去にしておく
        cal.add(Calendar.MINUTE, -1);
        if (jwt.getIssuedAt().before(cal.getTime())) {
            Date iat = jwt.getIssuedAt();

            throw new LtiException("The Token issued at " + DateTimeUtility.format(iat.getTime()) + " is too old.");
        }

        
        // azp
        Claim claim = jwt.getClaim(OidcUtility.CLAIM_AUD);
        String[] aud = claim.asArray(String.class);
        if (aud != null && aud.length > 1) {
            claim = jwt.getClaim(OidcUtility.CLAIM_AZP);
            if (claim.isNull() || claim.isMissing())
            {
                throw new LtiException(String.format(LtiUtility.ERROR_MISSING_IN_JWT, OidcUtility.CLAIM_AZP));
            }

            String azp = claim.asString();
            String client_id = input.getSession().getClientId();
            if (!azp.equals(client_id)) {
                throw new LtiException(String.format(LtiUtility.ERROR_VALUE, OidcUtility.CLAIM_AZP));
            }
        }

        return jwt;

    }

    /**
     * 必須クレームを確認する
     * 
     * @param jwt JWT情報
     * @throws Exception AnonymousLaunchException : Anonymous launch要求<br>
     *                   JpProfileException, LtiException : 失敗
     */
    private void parse(DecodedJWT jwt) throws Exception
    {
        Claim claim = null;
        
        // resource_link
        claim = jwt.getClaim(LtiUtility.CLAIM_RESOURCE_LINK);
        if (claim.isMissing() || claim.isNull())
        {
            throw new LtiException( 
                        String.format(LtiUtility.ERROR_MISSING_IN_JWT, LtiUtility.CLAIM_RESOURCE_LINK));
        }
    
        ResourceLinkDto rlDto = claim.as(ResourceLinkDto.class);
        if (rlDto == null || rlDto.id == null || rlDto.id.isEmpty())
        {
            throw new LtiException( 
                        String.format(LtiUtility.ERROR_PARAM, LtiUtility.PARAM_ID, LtiUtility.CLAIM_RESOURCE_LINK ));
        }
        if (rlDto.id.length() > LtiUtility.MAX_CHARS) {
            throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_ID, LtiUtility.CLAIM_RESOURCE_LINK));

        }
        if (rlDto.id.matches(Consts.REGEX_NON_ASCII)) {
            throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_ID, LtiUtility.CLAIM_RESOURCE_LINK));
        }

        // context
        claim = jwt.getClaim(LtiUtility.CLAIM_CONTEXT);
        if (claim.isMissing() || claim.isNull())
        {
            throw new JpProfileException(  String.format(LtiUtility.ERROR_MISSING_IN_JWT, LtiUtility.CLAIM_CONTEXT));
        }

        ContextDto cDto = claim.as(ContextDto.class);
        if (cDto == null || cDto.id == null || cDto.id.isEmpty())
        {
            throw new JpProfileException( 
                    String.format( LtiUtility.ERROR_PARAM, LtiUtility.PARAM_ID, LtiUtility.CLAIM_CONTEXT));
        }
        if (cDto.id.length() > LtiUtility.MAX_CHARS) {
            throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_ID, LtiUtility.CLAIM_CONTEXT));

        }
        if (cDto.id.matches(Consts.REGEX_NON_ASCII)) {
            throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_ID, LtiUtility.CLAIM_CONTEXT));
        }


        // roles
        claim = jwt.getClaim(LtiUtility.CLAIM_ROLES);
        if (claim.isNull() || claim.isMissing())
        {
            throw new LtiException( String.format(LtiUtility.ERROR_MISSING_IN_JWT, LtiUtility.CLAIM_ROLES));
        }

        // deployment_id
        claim = jwt.getClaim(LtiUtility.CLAIM_DEPLOYMENT_ID);
        if (claim.isNull() || claim.isMissing())
        {
            throw new LtiException(
                    String.format(LtiUtility.ERROR_MISSING_IN_JWT, LtiUtility.CLAIM_DEPLOYMENT_ID));

        }
        else {
            if (claim.asString().length() > LtiUtility.MAX_CHARS) {
                throw new LtiException(String.format(LtiUtility.ERROR_FORMAT, LtiUtility.CLAIM_DEPLOYMENT_ID));

            }
            if (claim.asString().matches(Consts.REGEX_NON_ASCII)) {
                throw new LtiException(String.format(LtiUtility.ERROR_FORMAT, LtiUtility.CLAIM_DEPLOYMENT_ID));
            }

            // 学習eポータル標準の仕様に合致するか確認
            String regex = JpProfileUtility.PREP_SCHOOL_CODE + "|" + JpProfileUtility.PREP_PREF_CODE + "|" + JpProfileUtility.PREP_MUNIC_CODE;
            Pattern p = Pattern.compile(regex);
            if ( !p.matcher(claim.asString()).find()) {
                throw new JpProfileException(
                        String.format(LtiUtility.ERROR_VALUE, LtiUtility.CLAIM_DEPLOYMENT_ID));
            }
        }

        // tool_platform
        claim = jwt.getClaim(LtiUtility.CLAIM_TOOL_PLATFORM);
        if (claim.isNull() || claim.isMissing())
        {
        }
        else {
            ToolPlatformDto tpDto = claim.as(ToolPlatformDto.class);
            if (tpDto == null || tpDto.guid == null) {
                throw new LtiException(String.format(LtiUtility.ERROR_PARAM, LtiUtility.PARAM_GUID, LtiUtility.CLAIM_TOOL_PLATFORM));
            }
            if (tpDto.guid.isEmpty()) {
                throw new LtiException(String.format(LtiUtility.ERROR_PARAM, LtiUtility.PARAM_GUID, LtiUtility.CLAIM_TOOL_PLATFORM));
            }
            if (tpDto.guid.length() > LtiUtility.MAX_CHARS) {
                throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_GUID, LtiUtility.CLAIM_TOOL_PLATFORM));

            }
            if (tpDto.guid.matches(Consts.REGEX_NON_ASCII)) {
                throw new LtiException(String.format(LtiUtility.ERROR_PARAM_FORMAT, LtiUtility.PARAM_GUID, LtiUtility.CLAIM_TOOL_PLATFORM));
            }

        }

        // custom/grade
        claim = jwt.getClaim(LtiUtility.CLAIM_CUSTOM);
        if (claim.isNull() || claim.isMissing())
        {
        }
        else {
            CustomDto custom = claim.as(CustomDto.class);
            if (custom != null) {
                if (! JpProfileUtility.GradeMap.contains(custom.grade)) {
                    throw new JpProfileException(String.format(LtiUtility.ERROR_FORMAT, LtiUtility.CLAIM_CUSTOM));

                }
            }
        }        

        // sub
        String sub = jwt.getSubject();
        if (sub == null) {
            throw new AnonymousLaunchException();
        }
        try {
            UUID.fromString(sub);
        }
        catch(Exception e) {
            throw new JpProfileException(String.format(LtiUtility.ERROR_FORMAT, OidcUtility.CLAIM_SUB));
        }
    }
    
}
