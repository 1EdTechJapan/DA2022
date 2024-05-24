import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.apache.log4j.Logger;


/**
 * CSV→xAPI変換のベースクラス
 * 
 */
abstract class XApiCsvConverterBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(XApiCsvConverterBase.class);

	/**
	 * CSVファイルを読み込み、xApiステートメント形式に変換して返す
	 *
	 * @param filePath 読み込むCSVファイルのパス
	 * @return xApiステートメントのリスト
	 * @throws IOException 入出力エラー
	 * @throws ParseException 解析エラー
	 */
	public String convertCsvToXApi(String filePath) throws IOException, ParseException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + filePath + ")");
		// CSVファイルの読み込み
		ArrayList<Map<String, String>> csvList = new ArrayList<>();
		csvList = loadCsv(filePath);
		if (csvList.isEmpty()) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : csvList is null");
			return null;
		}
		// xAPIステートメントへ変換
		ArrayList<String> xApiStatementList = new ArrayList<String>();
		for (Map<String, String> map: csvList) {
			xApiStatementList.addAll(createXApiStatement(map));
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return convertStatementArrayStr(xApiStatementList);
	}

	/**
	 * CSVファイルの読み込みを行う
	 *
	 * @param filePath 読み込むCSVファイルのパス
	 * @return CSVのリスト
	 * @throws IOException 入出力エラー
	 * @throws ParseException 解析エラー
	 */
	private ArrayList<Map<String, String>> loadCsv(String filePath) throws IOException, ParseException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + filePath + ")");
		ArrayList<Map<String, String>> csvList = new ArrayList<Map<String, String>>();
		BufferedReader br = null;
		File file = new File(filePath);
		br = new BufferedReader(new InputStreamReader(new FileInputStream(file), "utf-8"));
		String line;
		int count = 1;
		while ((line = br.readLine()) != null) {
			// 空欄のデータがある場合スキップする
			if (line.contains("\t\t") || line.startsWith("\t") || line.endsWith("\t")) {
				logger.info("skip csv raw : " + Integer.valueOf(count));
				count++;
				continue;
			}
			// カラム行をスキップする
			if (count == 1) {
				count++;
				continue;
			}
			// 情報をリストに格納する
			String[] data = line.split("\t");
			csvList.add(readLine(data));
			count++;
		}
		if (br != null) {
			br.close();
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return csvList;
	}

	/**
	 * 各プロパティの結合を行う
	 *
	 * @param timestamp タイムスタンプ
	 * @param actor actorプロパティ
	 * @param verb verbプロパティ
	 * @param object objectプロパティ
	 * @param result resultプロパティ
	 * @return xAPIステートメント文字列
	 */
	protected String joinProperties(String timestamp, String actor, String verb, String object, String result, String context) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", timestamp, actor, verb, object, result, context) + ")");
		FrameProperty frame = new FrameProperty();
		// ステートメント内の要素の設定
		frame.setId(createUuid());
		frame.setTimestamp(timestamp);
		String strFrame = frame.createJsonStatement();
		// 各プロパティを結合
		String strPropertiey;
		if (result != null) {
			strPropertiey = "," + String.join(",", actor, verb, object, result, context);
		} else {
			strPropertiey = "," + String.join(",", actor, verb, object, context);
		}
		// xAPIステートメント形式にして返す
		StringBuilder sb = new StringBuilder(strFrame);
		sb.insert(strFrame.length() - 1, strPropertiey);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return sb.toString();
	}

	/**
	 * UUIDを生成する
	 *
	 * @return UUID
	 */
	protected String createUuid() {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return UUID.randomUUID().toString();
	}

	/**
	 * xAPIステートメントのリストをJSON配列の文字列に変換する
	 *
	 * @param statementList xAPIステートメントのリスト
	 * @return JSON配列の文字列
	 */
	private String convertStatementArrayStr(List<String> statementList) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return "[" + String.join(",", statementList) + "]";
	}

	/**
	 * 引数からマップを生成する
	 *
	 * @param key キー
	 * @param value 値
	 * @return マップ
	 */
	protected Map<String, Object> createMap(String key, Object value) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", key, String.valueOf(value)) + ")");
		Map<String, Object> map = new HashMap<String, Object>();
		map.put(key, value);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return map;
	}

	/**
	 * CSVファイル1行分の配列をマップに変換するメソッド
	 * 内容は各実装クラスに記述
	 *
	 * @param data CSVファイル1行分の配列
	 * @return CSVファイル1行分のマップ
	 * @throws ParseException 解析エラー
	 */
	abstract Map<String, String> readLine(String[] data) throws ParseException;

	/**
	 * xApiステートメントを生成する
	 *
	 * @param map CSVファイル1行分の情報
	 */
	abstract ArrayList<String> createXApiStatement(Map<String, String> map);
}
