import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * objectプロパティ作成時の値を保持するクラス
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ObjectProperty extends CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(ObjectProperty.class.getName());

	/** オブジェクトID */
	private String id;
	/** オブジェクトタイプ */
	private String objectType;
	/** オブジェクト詳細マップ */
	@JsonProperty("definition")
	private Map<String, Object> definitionMap;

	/**
	 * オブジェクトIDを取得する
	 *
	 * @return オブジェクトID
	 */
	public String getId() {
		return id;
	}

	/**
	 * オブジェクトIDをセットする
	 *
	 * @param id オブジェクトID
	 */
	public void setId(String id) {
		this.id = id;
	}

	/**
	 * オブジェクトタイプを取得する
	 *
	 * @return オブジェクトタイプ
	 */
	public String getObjectType() {
		return objectType;
	}

	/**
	 * オブジェクトタイプセットする
	 *
	 * @param objectType オブジェクトタイプ
	 */
	public void setObjectType(String objectType) {
		this.objectType = objectType;
	}

	/**
	 * オブジェクト詳細マップをセットする
	 *
	 * @param mapKey マップのキー
	 * @param strKey 入れ子のマップのキー
	 * @param value 入れ子のマップの値
	 */
	public void setDefinitionMap(String mapKey, String strKey, String value) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", mapKey, strKey, value) + ")");
		this.definitionMap = createMap(mapKey, createMap(strKey, value));
	}

}
