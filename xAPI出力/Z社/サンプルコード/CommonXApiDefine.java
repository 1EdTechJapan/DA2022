
/**
 * CSV管理で使用する定数を定義するクラス
 */
public final class CommonXApiDefine {

	/**
	 * 定数定義クラスのためprivateでコンストラクタを宣言
	 */
	private CommonXApiDefine(){}

	/**
	 * eポータルID
	 */
	public static final String EPORTAL_ID = "EPORTAL_ID";

	/**
	 * eポータルユーザID
	 */
	public static final String EPORTAL_USER_ID = "EPORTAL_USER_ID";

	/**
	 * シートID
	 */
	public static final String SHEET_ID = "SHEET_ID";

	/**
	 * シート実施ユーザID
	 */
	public static final String CHALLENGE_USER_ID = "CHALLENGE_USER_ID";

	/**
	 * 実施開始時間
	 */
	public static final String CHALLENGE_START_DATE = "CHALLENGE_START_DATE";

	/**
	 * 実施終了時間
	 */
	public static final String CHALLENGE_END_DATE = "CHALLENGE_END_DATE";

	/**
	 * 得点
	 */
	public static final String SCORE = "SCORE";

	/**
	 * シート名
	 */
	public static final String SHEET_NAME = "SHEET_NAME";

	/**
	 * 学年ID(ドリル)
	 */
	public static final String GRADE = "GRADE";

	/**
	 * 教科ID
	 */
	public static final String CURRICULUM = "CURRICULUM";

	/**
	 * ドリル名
	 */
	public static final String DRILL_NAME = "DRILL_NAME";

	/**
	 * 日本語であることを示すパラメータ
	 */
	public static final String JA_JP = "ja-jp";

	/**
	 * CSVファイルのパス(テスト用)
	 */
	public static final String CSV_FILE_PATH = "xapi_target_tsv_path";

	/**
	 * 認可コード(テスト用)
	 */
	public static final String AUTHORIZATION_CODE = "xapi_authorization_code";

	/**
	 * xAPI送信先URL(テスト用)
	 */
	public static final String SEND_URL = "xapi_send_url";

	/**
	 * xAPI送信者名
	 */
	public static final String LRS_NAME = "xapi_lrp_name";

	/**
	 * xAPI送信者バージョン
	 */
	public static final String LRS_VERSION = "xapi_lrp_version";

	/**
	 * xAPIステートメントテキストファイル出力先パス
	 */
	public static final String STATEMENT_OUTPUT_PATH = "xapi_statement_output_path";

	/**
	 *  認可コード取得キー
	 */
	public static final String KEY_AUTHORIZATION = "Authorization";

	/**
	 * パラメータ取得キー(since)
	 */
	public static final String KEY_SINCE = "since";

	/**
	 * ログメッセージ(メソッド開始)
	 */
	public static final String LOG_START_METHOD = "start method";

	/**
	 * ログメッセージ(メソッド終了)
	 */
	public static final String LOG_END_METHOD = "end method";
}
