import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jws;

import java.io.IOException;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;


/**
 * LTIプラットフォームからLTIリクエストメッセージを受信するサーブレット
 */
@WebServlet(name = "LtiReceiveMessageServlet", urlPatterns = "/receive_lti_message")
public class LtiReceiveMessageServlet extends LtiServletBase {

	/** saltireのiss */
	private static String SALTIRE_ISS ="https://saltire.lti.app/platform";

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(LtiReceiveMessageServlet.class);

	@Override
	protected void execute(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());

		// ステートの取得
		String state = req.getParameter("state");
		logger.info("received state is " + state);
		// セッションの取得
		HttpSession session = req.getSession();
		// ステートを検証
		if (session.getAttribute(CommonLtiDefine.KEY_LTI_STATE_LIST) == null) {
			// ステートリストがセッション中にない場合
			logger.error(new IllegalStateException("LTI request doesn't contains the expected state"));
			dispatchLogin(req, resp);
			return;
		}
		List<String> ltiStateList = (List<String>) session.getAttribute(CommonLtiDefine.KEY_LTI_STATE_LIST);
		if (!ltiStateList.contains(state)) {
			// ステートリストにリクエストパラメータのステートがない場合
			logger.error(new IllegalStateException("LTI request doesn't contains the expected state"));
			dispatchLogin(req, resp);
			return;
		}
		// ステートの解読を行う
		LTIJWTService ltijwtService = new LTIJWTService();
		Jws<Claims> stateClaims = ltijwtService.validateState(state);
		logger.info("real state is " + stateClaims.toString());

		// リクエストトークンの取得
		String jwt = req.getParameter("id_token");
		if (StringUtils.isEmpty(jwt)) {
			logger.error(new IllegalStateException("LTI request cann't be received"));
			// リクエストトークンを取得できない場合
			dispatchLogin(req, resp);
			return;
		}
		if ("{".equals(jwt.substring(0,1))) {
			logger.info("pylti1p3.exception.LtiException:Invalid id_token, JWT must contain 3 parts");
			dispatchLogin(req, resp);
			return;
		}
		// トークンの解読を行う
//		LTIJWTService ltijwtService = new LTIJWTService();
		Jws<Claims> jws = null;
		try {
			jws = ltijwtService.validateJWT(jwt);
		} catch (ExpiredJwtException e) {
			// JWT有効期限切れによるエラー
			logger.info("pylti1p3.exception.LtiException:Can't decode id_token: Signature has expired");
			logger.error(e);
			dispatchLogin(req, resp);
			return;
		}
		if (jws == null) {
			// トークンの解読に失敗した場合
			logger.error(new IllegalStateException("LTI request isn't valid"));
			dispatchLogin(req, resp);
			return;
		}
		logger.info("received JWS : { " + jws.toString() + " }");
		// トークンを検証、格納する
		if (jws.getHeader() == null || jws.getBody() == null || jws.getSignature() == null) {
			logger.info("pylti1p3.exception.LtiException:Invalid id_token, JWT must contain 3 parts");
			dispatchLogin(req, resp);
			return;
		}
		LTIRequest ltiRequest = new LTIRequest(req, jws);

		if (ltiRequest.getSub() == null || ltiRequest.getLtiMessageType() == null || ltiRequest.getLtiVersion() == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName());
			dispatchLogin(req, resp);
			return;
		}

		if (StringUtils.isEmpty(ltiRequest.getLtiDeploymentId())) {
			logger.info("pylti1p3.exception.LtiException:deployment_id is not set in jwt body");
			// 以下 https://saltire.lti.app/ と疎通するための分岐
			// deployment_idが送られないことがあるため以下の処理を行う
			// deployment id を外部定義ファイルから取得する
			// 外部定義ファイルの値を利用した場合その旨ログ出力する
			if (SALTIRE_ISS.equals(ltiRequest.getIss())) {
				ltiRequest.setLtiDeploymentId(EnvConfigUtil.getInstance().getValue(CommonLtiDefine.KEY_LTI_PLATFORM_DEPLOYMENT_ID));
				logger.warn("because deploymentId is null,we use an externally defined value.");
			}
		}

		if (!ltiRequest.isSuccess()) {
			dispatchLogin(req, resp);
			return;
		}

		// 所属IDを取得しログイン処理
		DepartmentRecordModel model = getDepartmentId(req, resp, ltiRequest);
		if (model == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : DepartmentRecordModel is null");
			dispatchLogin(req, resp);
			return;
		}
		String departmentId = String.valueOf(model.getDepartmentId());
		logger.info("departmentId is " + departmentId);

		if (StringUtils.isEmpty(departmentId)) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : departmentId is null");
			// ペンまーるログイン画面へ遷移
			dispatchLogin(req, resp);
			return;
		}
		// パラメータを設定しペンまーるアカウント連係画面へ遷移
		req.setAttribute("department_id", departmentId);
		req.setAttribute("sso_object_id", ltiRequest.getSub());
		logger.info("sub is " + ltiRequest.getSub());
		getRequestDispatcher(req, resp, "/login?sso=lti").forward(req, resp);

		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
	}


    /**
     * ペンまーる所属IDを取得する
     *
     * @param req HTTPリクエスト
     * @param resp HTTPレスポンス
     * @param ltiRequest LTIリクエスト情報
     * @return 所属ID
     */
    private DepartmentRecordModel getDepartmentId(HttpServletRequest req, HttpServletResponse resp, LTIRequest ltiRequest) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
    	// Azure接続情報取得
    	BatchApiUtil api = new BatchApiUtil(new ApiOptionalEntity(req, resp));
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
    	return api.getDepartmentIdByLtiDeploymentId(ltiRequest.getLtiDeploymentId());
    }
}
