import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Map;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;

/**
 * シート実施結果CSVをxAPIステートメントに変換するクラス
 * 
 */
public class SheetChallengeCsvConverter extends XApiCsvConverterBase {

	/**
	 * CSVファイルの行(eポータルID)
	 */
	private static final int COLUMN_NUM_EPORTAL_ID = 0;

	/**
	 * CSVファイルの行(eポータルユーザID)
	 */
	private static final int COLUMN_NUM_EPORTAL_USER_ID = 1;

	/**
	 * CSVファイルの行(シートID)
	 */
	private static final int COLUMN_NUM_SHEET_ID = 2;

	/**
	 * CSVファイルの行(シート実施ユーザID)
	 */
	private static final int COLUMN_NUM_CHALLENGE_USER_ID = 3;

	/**
	 * CSVファイルの行(シート実施開始時刻)
	 */
	private static final int COLUMN_NUM_CHALLENGE_START_DATE = 4;

	/**
	 * CSVファイルの行(シート実施終了時刻)
	 */
	private static final int COLUMN_NUM_CHALLENGE_END_DATE = 5;

	/**
	 * CSVファイルの行(得点)
	 */
	private static final int COLUMN_NUM_SCORE = 6;

	/**
	 * CSVファイルの行(シート名)
	 */
	private static final int COLUMN_NUM_SHEET_NAME = 7;

	/**
	 * CSVファイルの行(教科)
	 */
	private static final int COLUMN_NUM_CURRICULUM = 9;

	/**
	 * CSVファイルの行(学年)
	 */
	private static final int COLUMN_NUM_GRADE = 11;

	/**
	 * CSVファイルの行(ドリル名)
	 */
	private static final int COLUMN_NUM_DRILL_NAME = 12;

	/**
	 * シート実施開始を表すID
	 */
	private static final String VERB_ID_ATTEMPTED = "http://adlnet.gov/expapi/verbs/attempted";

	/**
	 * シート実施終了を表すID
	 */
	private static final String VERB_ID_ANSWED = "http://adlnet.gov/expapi/verbs/answerd";

	/**
	 * xAPIステートメントの種別(シート開始)
	 */
	private static final String STATEMENT_TYPE_ATTEMPTED = "0";

	/**
	 * xAPIステートメントの種別(シート回答終了)
	 */
	private static final String STATEMENT_TYPE_ANSWED = "1";

	/**
	 * オブジェクトプロパティIDの先頭につける文字列
	 */
	public static final String PREFIX_OBJECT_PROPERTY_ID = "http://sample.co.jp/test#";

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(SheetChallengeCsvConverter.class.getName());


	@Override
	Map<String, String> readLine(String[] data) throws ParseException {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		SheetChallengeRecordModel model = new SheetChallengeRecordModel();
		model.setEportalId(data[COLUMN_NUM_EPORTAL_ID]);
		model.setEportalUserId(data[COLUMN_NUM_EPORTAL_USER_ID]);
		model.setSheetId(data[COLUMN_NUM_SHEET_ID]);
		model.setChallengeUserId(Integer.valueOf(data[COLUMN_NUM_CHALLENGE_USER_ID]));
		model.setScore(Integer.valueOf(data[COLUMN_NUM_SCORE]));
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy/MM/dd k:mm");
		model.setChallengeStartDate(sdf.parse(data[COLUMN_NUM_CHALLENGE_START_DATE]));
		model.setChallengeEndDate(sdf.parse(data[COLUMN_NUM_CHALLENGE_END_DATE]));
		model.setSheetName(data[COLUMN_NUM_SHEET_NAME]);
		model.setCurriculumId(data[COLUMN_NUM_CURRICULUM]);
		model.setDrillGrade(data[COLUMN_NUM_GRADE]);
		model.setDrillName(data[COLUMN_NUM_DRILL_NAME]);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return model.getStringMap();
	}

	@Override
	ArrayList<String> createXApiStatement(Map<String, String> map) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		ArrayList<String> statementList = new ArrayList<String>();
		statementList.add(createStrXApiStatement(map, STATEMENT_TYPE_ATTEMPTED));
		statementList.add(createStrXApiStatement(map, STATEMENT_TYPE_ANSWED));
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return statementList;
	}

	/**
	 * xAPIステートメントの文字列を生成する
	 *
	 * @param map シート実施情報
	 * @param statementType 作成するステートメントの種別
	 * @return xAPIステートメントの文字列
	 */
	private String createStrXApiStatement(Map<String, String> map, String statementType) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", "Map map", statementType) + ")");
		// actorプロパティの生成
		String actorProperty = createActorProperty(map.get(CommonXApiDefine.EPORTAL_USER_ID), map.get(CommonXApiDefine.EPORTAL_ID));

		// verbプロパティの生成
		String verbProperty = null;
		switch (statementType) {
		case STATEMENT_TYPE_ATTEMPTED:
			verbProperty = createVerbProperty(VERB_ID_ATTEMPTED, "シート実施開始");
			break;
		case STATEMENT_TYPE_ANSWED:
			verbProperty = createVerbProperty(VERB_ID_ANSWED, "シート実施終了");
			break;
		default:
			break;
		}

		// objectプロパティの生成
		String objectProperty = createObjectProperty(map.get(CommonXApiDefine.SHEET_ID), map.get(CommonXApiDefine.SHEET_NAME),
				map.get(CommonXApiDefine.DRILL_NAME), map.get(CommonXApiDefine.GRADE), map.get(CommonXApiDefine.CURRICULUM));

		// resultプロパティの生成
		String resultProperty = null;
		if (STATEMENT_TYPE_ANSWED.equals(statementType)) {
			resultProperty = createResultProperty(map.get(CommonXApiDefine.SCORE));
		}

		// contextプロパティの生成
		String contextProperty = createContextProperty(EnvConfigUtil.getInstance().getValue(CommonXApiDefine.LRS_NAME), EnvConfigUtil.getInstance().getValue(CommonXApiDefine.LRS_VERSION));

		// actor、verb、object、contextいずれかがnullの場合はステートメント作成を中止
		if (StringUtils.isEmpty(actorProperty)
		 || StringUtils.isEmpty(verbProperty)
		 || StringUtils.isEmpty(objectProperty)
		 || StringUtils.isEmpty(contextProperty)) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : required property is null");
			return null;
		}
		// 各プロパティの結合
		switch (statementType) {
		// シート実施開始の場合
		case STATEMENT_TYPE_ATTEMPTED:
			logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
			return joinProperties(map.get(CommonXApiDefine.CHALLENGE_START_DATE), actorProperty, verbProperty, objectProperty, resultProperty, contextProperty);
		// シート実施終了の場合
		case STATEMENT_TYPE_ANSWED:
			logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
			return joinProperties(map.get(CommonXApiDefine.CHALLENGE_END_DATE), actorProperty, verbProperty, objectProperty, resultProperty, contextProperty);
		default:
			break;
		}
		logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : statementType is illegal");
		return null;
	}

	/**
	 * actorプロパティを生成する
	 *
	 * @param userId eポータルのユーザID
	 * @param eportalId eポータルID
	 * @return actorプロパティの文字列
	 */
	private String createActorProperty(String userId, String eportalId) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", userId, eportalId) + ")");
		ActorProperty act = new ActorProperty();
		act.setAccountMap("name", userId);
		act.setAccountMap("homePage", eportalId);
		String property = act.createJsonStatement();
		// nullでない場合キーを追加
		if (property == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : property is null");
			return null;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return "\"actor\":" + property;
	}

	/**
	 * verbプロパティを生成する
	 *
	 * @param id 動作を示すID
	 * @param remark idを説明する注釈
	 * @return verbプロパティの文字列
	 */
	private String createVerbProperty(String id, String remark) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", id, remark) + ")");
		VerbProperty verb = new VerbProperty();
		verb.setId(id);
		verb.setDisplayMap(CommonXApiDefine.JA_JP, remark);
		String property = verb.createJsonStatement();
		// nullでない場合キーを追加
		if (property == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : property is null");
			return null;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return "\"verb\":" + property;
	}

	/**
	 * objectプロパティを生成する
	 *
	 * @param id シートID
	 * @param sheetName シート名
	 * @param drillName ドリル名
	 * @param drillGrade ドリルの対象学年
	 * @param curriculum 教科
	 * @return objectプロパティの文字列
	 */
	private String createObjectProperty(String id, String sheetName, String drillName, String drillGrade, String curriculum) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", id, sheetName, drillName, drillGrade, curriculum) + ")");
		ObjectProperty object = new ObjectProperty();
		object.setObjectType("Activity");
		object.setId(PREFIX_OBJECT_PROPERTY_ID + id);
		object.setDefinitionMap("name", CommonXApiDefine.JA_JP, String.join(" ", sheetName, drillName, drillGrade, curriculum));
		String property = object.createJsonStatement();
		// nullでない場合キーを追加
		if (property == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : property is null");
			return null;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return "\"object\":" + property;
	}

	/**
	 * resultプロパティを生成する
	 *
	 * @param score 得点
	 * @return resultプロパティの文字列
	 */
	private String createResultProperty(String score) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + score + ")");
		ResultProperty result = new ResultProperty();
		// scoreは数値でなければならないため変換する1
		result.setScoreMap("raw", Integer.valueOf(score));
		String property = result.createJsonStatement();
		// nullでない場合キーを追加
		if (property == null) {
			logger.info("break " + Thread.currentThread().getStackTrace()[1].getMethodName() + " : property is null");
			return null;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return "\"result\":" + property;
	}

	/**
	 * contextプロパティを生成する
	 *
	 * @param name LRP名称
	 * @param version LRPバージョン
	 * @return contextプロパティの文字列
	 */
	private String createContextProperty(String name, String version) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", name, version) + ")");
		ContextProperty context = new ContextProperty();
		String property = context.getContextProperty(name, version);
		if (StringUtils.isEmpty(property)) {
			return null;
		}
		return property;
	}

}
