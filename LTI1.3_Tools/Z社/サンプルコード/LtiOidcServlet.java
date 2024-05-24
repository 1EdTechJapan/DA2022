import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;

import com.google.common.hash.Hashing;

/**
 * initLoginリクエストを受けるサーブレット
 */
@WebServlet(name = "LtiOIDCServlet", urlPatterns = "/lti_oidc")
public class LtiOidcServlet extends LtiServletBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(LtiOidcServlet.class);

	@Override
	protected void execute(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());

        // パラメータの取得
        OidcLoginInitiationDTO dto = new OidcLoginInitiationDTO(req);
        // プラットフォーム情報の取得
        PlatformDeployment platformDeployment = new PlatformDeployment();
        // プラットフォーム情報の検証
        if (!dto.getIss().equals(platformDeployment.getIss())) {
        	logger.warn("tool doesn't have this platform iss");
        	dispatchLogin(req, resp);
        	return;
        }
        String clientIdValue = dto.getClientId();
        String deploymentIdValue = dto.getDeploymentId();
        if (StringUtils.isEmpty(clientIdValue)) {
        	// パラメータにクライアントIDが含まれていない場合
        	clientIdValue = platformDeployment.getClientId();
        }
        if (StringUtils.isEmpty(deploymentIdValue)) {
        	// パラメータにデプロイメントIDが含まれていない場合
        	deploymentIdValue = platformDeployment.getDeploymentId();
        }

        String nextUrl;

        try {
            // OIDCリクエスト情報の作成
            Map<String, String> parameters = generateAuthRequestPayload(dto, clientIdValue, deploymentIdValue, platformDeployment.getOidcEndpoint());
            HttpSession session = req.getSession();
            List<String> stateList = session.getAttribute(CommonLtiDefine.KEY_LTI_STATE_LIST) != null ? (List) session.getAttribute("lti_state") : new ArrayList<>();
            String state = parameters.get(CommonLtiDefine.KEY_LTI_STATE);

            if (!stateList.contains(state)) {
                stateList.add(state);
                logger.info("state is {" + state + "}");
            }
            session.setAttribute(CommonLtiDefine.KEY_LTI_STATE_LIST, stateList);

            List<String> nonceList = session.getAttribute(CommonLtiDefine.KEY_LTI_NONCE_LIST) != null ? (List) session.getAttribute("lti_nonce") : new ArrayList<>();
            String nonce = parameters.get("nonce");
            if (!nonceList.contains(nonce)) {
                nonceList.add(nonce);
                logger.info("nonce is {" + nonce + "}");
            }
            session.setAttribute(CommonLtiDefine.KEY_LTI_NONCE_LIST, nonceList);
            nextUrl = parameters.get("oidcEndpointComplete");
        } catch (GeneralSecurityException | IOException e) {
        	// セキュリティエラーがあった場合
			logger.error("create oidc request is failed", e);
			dispatchLogin(req, resp);
        	return;
        }
        resp.sendRedirect(nextUrl);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName() + "nextUrl is {" + nextUrl + "}");
	}


	/**
	 * JWTペイロードに格納する情報をマップにまとめる
	 *
	 * @param dto プラットフォーム情報を格納したインスタンス
	 * @param clientIdValue プラットフォームのクライアントID
	 * @param deploymentIdValue プラットフォームのデプロイメントID
	 * @param oidcEndpoint プラットフォームの認証エンドポイント
	 * @return JWTペイロードに格納する情報のマップ
	 * @throws GeneralSecurityException セキュリティエラー
	 * @throws IOException 入出力エラー
	 */
    private Map<String, String> generateAuthRequestPayload(OidcLoginInitiationDTO dto, String clientIdValue, String deploymentIdValue, String oidcEndpoint)
    		throws GeneralSecurityException, IOException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + "(" + String.join(",", clientIdValue, deploymentIdValue, oidcEndpoint) + ")" + ")");
        Map<String, String> authRequestMap = new HashMap<>();
        if (clientIdValue != null) {
            authRequestMap.put(CommonLtiDefine.KEY_CLIENT_ID, clientIdValue);
        }
        authRequestMap.put("login_hint", dto.getLoginHint());
        authRequestMap.put("lti_message_hint", dto.getLtiMessageHint());
        String nonce = UUID.randomUUID().toString();
        String nonceHash = Hashing.sha256().hashString(nonce, StandardCharsets.UTF_8).toString();
        authRequestMap.put("nonce", nonce);
        authRequestMap.put("nonce_hash", nonceHash);
        authRequestMap.put("prompt", CommonLtiDefine.KEY_NONE);
        authRequestMap.put("redirect_uri", EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_REDIRECT_URL));
        authRequestMap.put("response_mode", CommonLtiDefine.KEY_FORM_POST);
        authRequestMap.put("response_type", CommonLtiDefine.KEY_ID_TOKEN);
        authRequestMap.put("scope", CommonLtiDefine.KEY_OPEN_ID);
        // 秘密鍵はmanage_config.xmlに外部定義
        String state = LtiOidcUtils.generateState(EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_OWN_PRIVATE_KEY), authRequestMap, dto, clientIdValue, deploymentIdValue);
        authRequestMap.put("state", state);
        authRequestMap.put("oidcEndpoint", oidcEndpoint);
        authRequestMap.put("oidcEndpointComplete", generateCompleteUrl(authRequestMap));
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
        return authRequestMap;
    }

    /**
     * パラメータを追加したURLを生成する
     *
     * @param model パラメータのマップ
     * @return パラメータを追加したURL
     * @throws UnsupportedEncodingException 文字コードエラー
     */
    private String generateCompleteUrl(Map<String, String> model) throws UnsupportedEncodingException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
        StringBuilder getUrl = new StringBuilder();

        getUrl.append(model.get("oidcEndpoint"));
        if (model.get(CommonLtiDefine.KEY_CLIENT_ID) != null) {
            getUrl = addParameter(getUrl, "client_id", model.get(CommonLtiDefine.KEY_CLIENT_ID), true);
            getUrl = addParameter(getUrl, "login_hint", model.get("login_hint"), false);
        } else {
            getUrl = addParameter(getUrl, "login_hint", model.get("login_hint"), true);
        }
        getUrl = addParameter(getUrl, "lti_message_hint", model.get("lti_message_hint"), false);
        getUrl = addParameter(getUrl, "nonce", model.get("nonce_hash"), false);
        getUrl = addParameter(getUrl, "prompt", model.get("prompt"), false);
        getUrl = addParameter(getUrl, "redirect_uri", model.get("redirect_uri"), false);
        getUrl = addParameter(getUrl, "response_mode", model.get("response_mode"), false);
        getUrl = addParameter(getUrl, "response_type", model.get("response_type"), false);
        getUrl = addParameter(getUrl, "scope", model.get("scope"), false);
        getUrl = addParameter(getUrl, "state", model.get("state"), false);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName() + "return:" + getUrl.toString());
        return getUrl.toString();
    }

    /**
     * URLにパラメータを追加する
     *
     * @param url URL
     * @param parameter キー
     * @param value 値
     * @param first 初期追加かどうかのフラグ
     * @return パラメータが追加されたURL
     * @throws UnsupportedEncodingException 文字コードエラー
     */
    private StringBuilder addParameter(StringBuilder url, String parameter, String value, boolean first) throws UnsupportedEncodingException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", url, parameter, value, String.valueOf(first)) + ")" + ")");

        if (value != null) {
            if (first) {
                url.append("?").append(parameter).append("=");
            } else {
                url.append("&").append(parameter).append("=");
            }
            url.append(URLEncoder.encode(value, String.valueOf(StandardCharsets.UTF_8)));
        }
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName() + " return:" + url);
        return url;
    }

}
