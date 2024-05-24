/**
 * 学習eポータルサイトからCBTシステムの各種画面にアクセスする際にOIDCの認証の代行を実施するライブラリ。
 * @author
 *
 */
public class XXXXXLoginRequest {

	private static Logger logger = LoggerFactory.getLogger(XXXXXLoginRequest.class);
	private static AuthLibUtil authLib = new AuthLibUtil();

	/**
	 * パラメータのバリデーションチェックを行い、パラメータをもとにCBTシステムにリクエスト(※1)を発行します。
	 * @param xxxxxUri			CBTシステム接続用URL
	 * @param iss				学習eポータルのベースURL
	 * @param loginHint			uuid　※IDトークン内のsubと同じ値
	 * @param targetLinkUri		targetLinkUri
	 * @param clientId			学習eポータルでCBTシステムに振り出したclient id
	 * @param ltiDeploymentId	CBTシステムでは利用しない
	 * @param ltiMessageHint	連携された場合設定
	 * @param res        		レスポンスのHTTPステータスを設定（正常の場合、302を返す）
	 * @param errorMassege      エラーが発生した場合、エラー内容が返される
	 * @return true:  	false:
	 */
	public static boolean isXXXXXLoginRequest(String xxxxxUri,
			String iss,
			String loginHint,
			String targetLinkUri,
			String clientId,
			String ltiDeploymentId,
			String ltiMessageHint,
			XXXXXResponse res )
					 {

		logger.info("*** XXXXXLoginRequest START: " + new Object() {}.getClass().getEnclosingClass().getName());
		logger.info("xxxxxUri=" + xxxxxUri);
		logger.info("iss=" + iss);
		logger.info("loginHint=" + loginHint);
		logger.info("targetLinkUri=" + targetLinkUri);
		logger.info("clientId=" + clientId);
		logger.info("ltiDeploymentId=" + ltiDeploymentId);
		logger.info("ltiMessageHint=" + ltiMessageHint);

		boolean ret = false;
		res.errorMassege = "";
		res.redirectHtml = new StringBuffer();

		//パラメータチェック


		res.redirectHtml = createHtml(xxxxxUri, iss, loginHint, targetLinkUri, clientId, ltiDeploymentId, ltiMessageHint);
		ret = true;

		logger.info("*** XXXXXLoginRequest END: " + new Object() {}.getClass().getEnclosingClass().getName());
		return ret;
	}

	/***
	 * ブラウザにてリダイレクト
	 * @param xxxxxUri			CBTシステム接続用URL
	 * @param iss				学習eポータルのベースURL
	 * @param loginHint			uuid　※IDトークン内のsubと同じ値
	 * @param targetLinkUri		targetLinkUri
	 * @param clientId			学習eポータルでCBTシステムに振り出したclient id
	 * @param ltiDeploymentId	CBTシステムでは利用しない
	 * @param ltiMessageHint	連携された場合設定
	 * @return　StringBuffer
	 */
	private static StringBuffer createHtml(String xxxxxUri,
			String iss,
			String loginHint,
			String targetLinkUri,
			String clientId,
			String ltiDeploymentId,
			String ltiMessageHint) {

	    String BR = System.getProperty("line.separator");
		StringBuffer htmlStr = new StringBuffer();
		htmlStr.append("<!DOCTYPE html>" + BR);
		htmlStr.append("<html lang=\"ja\">" + BR);
		htmlStr.append(BR);
		htmlStr.append("    <head>" + BR);
		htmlStr.append("        <meta charset=\"utf-8\">" + BR);
		htmlStr.append("        <script type=\"text/javascript\">" + BR);
		htmlStr.append("	    	var params = new URLSearchParams({" + BR);
		htmlStr.append("            iss: \"" + StringEscapeUtils.escapeEcmaScript(iss) + "\"," + BR);
		htmlStr.append("            client_id: \"" + StringEscapeUtils.escapeEcmaScript(clientId) + "\"," + BR);
		htmlStr.append("            login_hint: \"" + StringEscapeUtils.escapeEcmaScript(loginHint) + "\"," + BR);
		htmlStr.append("            target_link_uri: \"" + StringEscapeUtils.escapeEcmaScript(targetLinkUri) + "\"," + BR);
		htmlStr.append("            lti_deployment_id: \"" + StringEscapeUtils.escapeEcmaScript(ltiDeploymentId) + "\"," + BR);
		htmlStr.append("            lti_message_hint: \"" + StringEscapeUtils.escapeEcmaScript(ltiMessageHint) + "\"" + BR);
		htmlStr.append("        });" + BR);
		htmlStr.append(BR);
		htmlStr.append("        async function HttpRequest(){" + BR);
		htmlStr.append("	            document.location.href = \"" + StringEscapeUtils.escapeEcmaScript(xxxxxUri) + "?\"+params;" + BR);
		htmlStr.append("        }" + BR);
		htmlStr.append("        </script>" + BR);
		htmlStr.append("        <title>Redirecting</title>" + BR);
		htmlStr.append("    </head>" + BR);
		htmlStr.append(BR);
		htmlStr.append("    <body onload=HttpRequest()> </body>" + BR);
		htmlStr.append(BR);
		htmlStr.append("</html>");

		return htmlStr;
	}
}