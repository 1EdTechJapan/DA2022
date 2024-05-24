import java.util.Map;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;

/**
 * xAPIステートメントを送信するサーブレット
 * 
 */
@WebServlet(name = "SendXApiServlet", urlPatterns = "/send_xapi")
public class SendXApiServlet extends XApiServletBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(SendXApiServlet.class.getName());

	@Override
	protected void execute(HttpServletRequest req, HttpServletResponse resp) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		// リクエスト情報を取得
		Map<String, String> requestMap = getRequestParameter(req, resp);
		if (requestMap.isEmpty()) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : requestMap is null");
			return;
		}
		// 読み込み対象のCSVファイルのパスを取得する
		String filePath = getFilePath();
		if (filePath.isEmpty()) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : filePath is null");
			return;
		}
		// 送信先のURLを取得する
		String targetUrl = getTargetUrl();
		if (targetUrl.isEmpty()) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : targetUrl is null");
			return;
		}
		try {
			// xAPIステートメントの送信
			sendXApiStatement(filePath, requestMap.get(CommonXApiDefine.KEY_AUTHORIZATION), targetUrl);
		} catch (Exception e) {
			logger.warn("break " + Thread.currentThread().getStackTrace()[1].getMethodName(), e);
			e.printStackTrace();
			return;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
	}

}
