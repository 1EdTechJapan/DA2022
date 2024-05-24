import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;

/**
 * xAPI処理のベースクラス
 * 
 */
abstract class XApiServletBase extends ServletBase {

	/** 通常終了時のステータスコード */
	private static final int NON_ERROR_SUTATUS_CODE = 200;
	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(XApiServletBase.class);


	/**
	 * リクエストのヘッダ情報やパラメータを取得する
	 *
	 * @param req HTTPリクエスト
	 * @param resp HTTPレスポンス
	 * @return リクエスト情報のマップ
	 */
	protected Map<String, String> getRequestParameter(HttpServletRequest req, HttpServletResponse resp) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		// プロトタイプは外部定義ファイルから取得
		Map<String, String> map = new HashMap<String, String>();
		// 認可コードを取得
//		String authorizationCode = req.getHeader(KEY_AUTHORIZATION);
//		if (authorizationCode == null) {
//			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : authorization code is null");
//			return null
//		}
		map.put(CommonXApiDefine.KEY_AUTHORIZATION, EnvConfigUtil.getInstance().getValue(CommonXApiDefine.AUTHORIZATION_CODE));
		if (map.get(CommonXApiDefine.KEY_AUTHORIZATION).isEmpty()) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : authorization code is null");
			return null;
		}
		// リクエストパラメータを取得
//		String since = req.getParameter(KEY_SINCE);
//		if (since == null) {
//			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : since is null");
//			return null;
//		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return map;
	}

	/**
	 * 読み込み対象のTSVファイルのパスを取得する
	 *
	 * @return ファイルパス
	 */
	protected String getFilePath() {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		// プロトタイプでは外部定義ファイルから取得
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return EnvConfigUtil.getInstance().getValue(CommonXApiDefine.CSV_FILE_PATH);
	}

	/**
	 * xAPI送信先のURLを取得する
	 *
	 * @return xAPI送信先のURL
	 */
	protected String getTargetUrl() {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		// プロトタイプでは外部定義ファイルから取得
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return EnvConfigUtil.getInstance().getValue(CommonXApiDefine.SEND_URL);
	}

	/**
	 * xAPIステートメントの送信処理を行う
	 *
	 * @param filePath 読み込むCSVファイルのパス
	 * @param authorizationCode 認可コード
	 * @param targetUrl 送信先URL
	 * @throws IOException 入出力エラー
	 * @throws ParseException 解析エラー
	 */
	protected void sendXApiStatement(String filePath, String authorizationCode, String targetUrl) throws IOException, ParseException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", filePath, authorizationCode, targetUrl) + ")");
		// 送信するステートメントを取得
		SheetChallengeCsvConverter sccc = new SheetChallengeCsvConverter();
		String xApiStatement = sccc.convertCsvToXApi(filePath);
		if (xApiStatement == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : xApiStatement is null");
			return;
		}
		// xAPIステートメントを送信する
		 HttpURLConnection con = sendXApiToClient(targetUrl, authorizationCode, xApiStatement);
		logger.info("finish sending xAPI statements");
		logger.info("response code : " + String.valueOf(con.getResponseCode()));
		boolean resultFlag = true;
		// エラーの場合はログ出力
		if (con.getResponseCode() != NON_ERROR_SUTATUS_CODE) {
		resultFlag = false;
		logger.warn("response message : " + con.getResponseMessage());
		}
		// xAPIステートメントをテキストファイルに出力
		createTextFileOfStatement(xApiStatement, resultFlag);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
	}

	/**
	 * xAPIステートメントを送信する
	 *
	 * @param strUrl 送信先URL
	 * @param authorizationCode 認可コード
	 * @param xApiStatement xAPIステートメント
	 * @return 接続情報
	 * @throws IOException 入出力エラー
	 */
	protected HttpURLConnection sendXApiToClient(String strUrl, String authorizationCode, String xApiStatement) throws IOException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", strUrl, authorizationCode, xApiStatement) + ")");
		// 送信先との接続情報を設定
        URL url = new URL(strUrl);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        //リクエストヘッダに値を設定
        con.setRequestMethod("POST");
        con.setDoOutput(true);
        con.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        con.setRequestProperty("X-Experience-API-Version", "1.0");
        con.setRequestProperty("Authorization", authorizationCode);
        // xAPIステートメントの送信
        OutputStreamWriter out = new OutputStreamWriter(con.getOutputStream());
        out.write(xApiStatement);
        out.close();
        con.disconnect();
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
        return con;
	}

	/**
	 * xAPIステートメントをテキストファイルに出力する
	 *
	 * @param statement xAPIステートメント
	 * @param resultFlag 送信成否
	 */
	protected void createTextFileOfStatement(String statement, boolean resultFlag) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		// 出力先を取得
		String path = EnvConfigUtil.getInstance().getValue(CommonXApiDefine.STATEMENT_OUTPUT_PATH);
		if (StringUtils.isEmpty(path)) {
			// 出力先が設定されていない場合出力しない
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : output path is null");
			return;
		}
		// 送信失敗の場合ファイル名末尾にその旨追加
		String suffixText = "";
		if (!resultFlag) {
			suffixText = "FAILED";
		}
		PrintWriter writer = null;
		try {
			writer = new PrintWriter(path + "/xAPI_Statement_" + getNowStr() + suffixText + ".txt", "utf-8");
			writer.println(statement);
		} catch (FileNotFoundException | UnsupportedEncodingException e) {
			logger.warn("output statement text file is fail", e);
			return;
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
	}

	/**
	 * 現在時刻の文字列を返す
	 *
	 * @return 現在時刻の文字列
	 */
	private String getNowStr() {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss_SSS");
		Date now = new Date();
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return sdf.format(now);
	}
}
