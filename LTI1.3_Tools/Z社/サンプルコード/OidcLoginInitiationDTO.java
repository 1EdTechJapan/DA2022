import javax.servlet.http.HttpServletRequest;

import org.apache.log4j.Logger;

/**
 * プラットフォームからのinitリクエスト情報を保持するクラス
 */
public class OidcLoginInitiationDTO {

	/** iss */
	private String iss;
	/** ログインヒント */
	private String loginHint;
	/** ターゲットURI */
	private String targetLinkUri;
	/** ログインヒントメッセージ */
	private String ltiMessageHint;
	/** クライアントID */
	private String clientId;
	/** デプロイメントID */
	private String deploymentId;

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(OidcLoginInitiationDTO.class);


	/**
	 * コンストラクタ
	 *
	 * @param iss プラットフォームのURL
	 * @param loginHint ログインヒント
	 * @param targetLinkUri 遷移先URL
	 * @param ltiMessageHint ログインメッセージ
	 * @param clientId クライアントID
	 * @param deploymentId デプロイメントID
	 */
	public OidcLoginInitiationDTO(String iss, String loginHint, String targetLinkUri, String ltiMessageHint, String clientId, String deploymentId) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", iss, loginHint, targetLinkUri, ltiMessageHint, clientId, deploymentId) + ")");
		this.iss = iss;
		this.loginHint = loginHint;
		this.targetLinkUri = targetLinkUri;
		this.ltiMessageHint = ltiMessageHint;
		this.clientId = clientId;
		this.deploymentId = deploymentId;
        logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
	}

	/**
	 * コンストラクタ
	 *
	 * @param req HTTPリクエスト
	 */
	public OidcLoginInitiationDTO(HttpServletRequest req) {
		this(req.getParameter(CommonLtiDefine.KEY_ISS),
				req.getParameter(CommonLtiDefine.KEY_LOGIN_HINT),
				req.getParameter(CommonLtiDefine.KEY_TARGET_LINK_URI),
				req.getParameter(CommonLtiDefine.KEY_LTI_MESSAGE_HINT),
				req.getParameter(CommonLtiDefine.KEY_CLIENT_ID),
				req.getParameter(CommonLtiDefine.KEY_DEPLOYMENT_ID));
	}

	/**
	 *
	 * @return iss
	 */
	public String getIss() {
		return iss;
	}

	/**
	 *
	 * @param iss セットする iss
	 */
	public void setIss(String iss) {
		this.iss = iss;
	}

	/**
	 *
	 * @return loginHint
	 */
	public String getLoginHint() {
		return loginHint;
	}

	/**
	 *
	 * @param loginHint セットする loginHint
	 */
	public void setLoginHint(String loginHint) {
		this.loginHint = loginHint;
	}

	/**
	 *
	 * @return targetLinkUri
	 */
	public String getTargetLinkUri() {
		return targetLinkUri;
	}

	/**
	 *
	 * @param targetLinkUri セットする targetLinkUri
	 */
	public void setTargetLinkUri(String targetLinkUri) {
		this.targetLinkUri = targetLinkUri;
	}

	/**
	 *
	 * @return ltiMessageHint
	 */
	public String getLtiMessageHint() {
		return ltiMessageHint;
	}

	/**
	 *
	 * @param ltiMessageHint セットする ltiMessageHint
	 */
	public void setLtiMessageHint(String ltiMessageHint) {
		this.ltiMessageHint = ltiMessageHint;
	}

	/**
	 *
	 * @return clientId
	 */
	public String getClientId() {
		return clientId;
	}

	/**
	 *
	 * @param clientId セットする clientId
	 */
	public void setClientId(String clientId) {
		this.clientId = clientId;
	}

	/**
	 *
	 * @return deploymentId
	 */
	public String getDeploymentId() {
		return deploymentId;
	}

	/**
	 *
	 * @param deploymentId セットする deploymentId
	 */
	public void setDeploymentId(String deploymentId) {
		this.deploymentId = deploymentId;
	}
}
