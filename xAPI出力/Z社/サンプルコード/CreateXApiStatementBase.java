import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;


/**
 * xAPIステートメント作成のベースクラス
 * 
 */
public class CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(CreateXApiStatementBase.class.getName());

	/**
	 * 引数からJSONステートメントを生成する
	 *
	 * @return JSONステートメント
	 */
	public String createJsonStatement() {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName());
		String json = null;
		ObjectMapper mapper = new ObjectMapper();
		try {
			json = mapper.writeValueAsString(this);
		} catch (JsonProcessingException e) {
			e.printStackTrace();
			return null;
		}
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return json;
	}

	/**
	 * 引数からマップを生成する
	 *
	 * @param key キー
	 * @param value 値
	 * @return マップ
	 */
	protected Map<String, Object> createMap(String key, Object value) {
		logger.info("start " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(key : " + key + ")");
		Map<String, Object> map = new HashMap<String, Object>();
		map.put(key, value);
		logger.info("end " + Thread.currentThread().getStackTrace()[1].getMethodName());
		return map;
	}
}
