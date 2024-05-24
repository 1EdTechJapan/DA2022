import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * resultプロパティ作成時の値を保持するクラス
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ResultProperty extends CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(ResultProperty.class.getName());

	/** 得点情報のマップ */
	@JsonProperty("score")
	private Map<String, Object> scoreMap;
	/** 得点 */
	@JsonIgnore
	private String raw;


	/**
	 * コンストラクタ
	 */
	public ResultProperty() {
		scoreMap = new HashMap<>();
	}

	/**
	 * 得点を取得する
	 *
	 * @return 得点
	 */
	public String getRaw() {
		return raw;
	}

	/**
	 * 得点をセットする
	 *
	 * @param raw 得点
	 */
	public void setRaw(String raw) {
		this.raw = raw;
	}

	/**
	 * 得点情報のマップをセットする
	 *
	 * @param key キー
	 * @param obj 値
	 */
	public void setScoreMap(String key, Object obj) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(key : " + key + ")");
		scoreMap = createMap(key, obj);
	}

}
