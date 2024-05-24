import org.apache.log4j.Logger;


/**
 * xAPIステートメントの枠組み作成時の値を保持するクラス
 * 
 */
public class FrameProperty extends CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(FrameProperty.class.getName());

	/** ステートメントID */
	private String id;
	/** ステートメントバージョン */
	private String version;
	/** タイムスタンプ */
	private String timestamp;


	/**
	 * コンストラクタ
	 */
	public FrameProperty() {
		this.version = "1.0.0";
	}

	/**
	 * ステートメントIDを取得する
	 *
	 * @return ステートメントID
	 */
	public String getId() {
		return id;
	}

	/**
	 * ステートメントIDをセットする
	 *
	 * @param id ステートメント
	 */
	public void setId(String id) {
		this.id = id;
	}

	/**
	 * ステートメントバージョンを取得する
	 *
	 * @return ステートメントバージョン
	 */
	public String getVersion() {
		return version;
	}

	/**
	 * ステートメントバージョンをセットする
	 *
	 * @param version ステートメントバージョン
	 */
	public void setVersion(String version) {
		this.version = version;
	}

	/**
	 * タイムスタンプを取得する
	 *
	 * @return タイムスタンプ
	 */
	public String getTimestamp() {
		return timestamp;
	}

	/**
	 * タイムスタンプをセットする
	 *
	 * @param timestamp タイムスタンプ
	 */
	public void setTimestamp(String timestamp) {
		this.timestamp = timestamp;
	}

}
