import org.apache.log4j.Logger;

/**
 * ツールで保持する学習eポータル情報を持つクラス
 */
public class PlatformDeployment {

	/**  */
	private String iss;
	/**  */
	private String oidcEndpoint;
	/**  */
	private String jwksEndpoint;
	/**  */
	private String deploymentId;
	/**  */
	private String clientId;

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(PlatformDeployment.class);


	/**
	 * コンストラクタ
	 * プロトタイプではプラットフォーム情報をconfig.xmlから取得
	 */
	public PlatformDeployment() {
        logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		this.iss = EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_ISS);
		this.oidcEndpoint = EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_OIDC_ENDPOINT);
		this.jwksEndpoint = EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_JWKS_ENDPOINT);
		this.deploymentId = EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_DEPLOYMENT_ID);
		this.clientId = EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_CLIENT_ID);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", iss, oidcEndpoint, jwksEndpoint, deploymentId, clientId) + ")");
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
	 * @return oidcEndpoint
	 */
	public String getOidcEndpoint() {
		return oidcEndpoint;
	}

	/**
	 *
	 * @param oidcEndpoint セットする oidcEndpoint
	 */
	public void setOidcEndpoint(String oidcEndpoint) {
		this.oidcEndpoint = oidcEndpoint;
	}

	/**
	 *
	 * @return jwksEndpoint
	 */
	public String getJwksEndpoint() {
		return jwksEndpoint;
	}

	/**
	 *
	 * @param jwksEndpoint セットする jwksEndpoint
	 */
	public void setJwksEndpoint(String jwksEndpoint) {
		this.jwksEndpoint = jwksEndpoint;
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


}
