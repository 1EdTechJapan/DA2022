import java.util.Map;

/**
 * 
 */
public interface ICsvRecordModel {
	/**
	 * CSVファイル1行分のレコードを取得する
	 * @return CSVファイルのレコード
	 */
	Map<String, String> getStringMap();
}
