import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * verbプロパティ作成時の値を保持するクラス
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class VerbProperty extends CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(VerbProperty.class.getName());

	/** 動作ID */
	private String id;
	/** 動作詳細マップ */
	@JsonProperty("display")
	private Map<String, Object> displayMap;


	/**
	 * コンストラクタ
	 */
	public VerbProperty() {
		this.displayMap = new HashMap<>();
	}

	/**
	 * 動作IDを取得する
	 *
	 * @return 動作ID
	 */
	public String getId() {
		return id;
	}

	/**
	 * 動作IDをセットする
	 *
	 * @param id 動作ID
	 */
	public void setId(String id) {
		this.id = id;
	}

	/**
	 * 動作詳細マップをセットする
	 *
	 * @param key キー
	 * @param value 値
	 */
	public void setDisplayMap(String key, String value) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", key, value) + ")");
		this.displayMap = createMap(key, value);
	}

}
