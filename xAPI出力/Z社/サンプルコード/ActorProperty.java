import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * actorプロパティ作成時の値を保持するクラス
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ActorProperty extends CreateXApiStatementBase {

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(ActorProperty.class.getName());

	/** オブジェクトタイプ */
	private String objectType;
	/** 名前 */
	@JsonIgnore
	private String name;
	/** メールアドレス */
	private String mbox;
	/** ハッシュ化されたメールアドレス */
	@JsonProperty("mbox_sha1sum")
	private String mboxSha1sum;
	/** オープンID */
	private String openid;
	/** アカウントのあるサイトURL */
	@JsonIgnore
	private String homePage;
	/** アカウント情報マップ */
	@JsonProperty("account")
	private Map<String, Object> accountMap;


	/**
	 * コンストラクタ
	 */
	public ActorProperty() {
		this.objectType = "Agent";
		this.accountMap = new HashMap<>();
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
	 * オブジェクトタイプをセットする
	 *
	 * @param objectType オブジェクトタイプ
	 */
	public void setObjectType(String objectType) {
		this.objectType = objectType;
	}

	/**
	 * 名前を取得する
	 *
	 * @return 名前
	 */
	public String getName() {
		return name;
	}

	/**
	 * 名前をセットする
	 *
	 * @param name 名前
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * メールアドレスを取得する
	 *
	 * @return メールアドレス
	 */
	public String getMbox() {
		return mbox;
	}

	/**
	 * メールアドレスをセットする
	 *
	 * @param mbox メールアドレス
	 */
	public void setMbox(String mbox) {
		this.mbox = mbox;
	}

	/**
	 * ハッシュ化されたメールアドレスを取得する
	 *
	 * @return ハッシュ化されたメールアドレス
	 */
	public String getMboxSha1sum() {
		return mboxSha1sum;
	}

	/**
	 * ハッシュ化されたメールアドレスをセットする
	 *
	 * @param mboxSha1sum ハッシュ化されたメールアドレス
	 */
	public void setMboxSha1sum(String mboxSha1sum) {
		this.mboxSha1sum = mboxSha1sum;
	}

	/**
	 * オープンIDを取得する
	 *
	 * @return オープンID
	 */
	public String getOpenid() {
		return openid;
	}

	/**
	 * オープンIDをセットする
	 *
	 * @param openid オープンID
	 */
	public void setOpenid(String openid) {
		this.openid = openid;
	}

	/**
	 * アカウントのあるサイトURLを取得する
	 *
	 * @return アカウントのあるサイトURL
	 */
	public String getHomePage() {
		return homePage;
	}

	/**
	 * アカウントのあるサイトURLをセットする
	 *
	 * @param homePage アカウントのあるサイトURL
	 */
	public void setHomePage(String homePage) {
		this.homePage = homePage;
	}

	/**
	 * アカウント情報のマップをセットする
	 *
	 * @param key キー
	 * @param value 値
	 */
	public void setAccountMap(String key, String value) {
		logger.info("pass " + Thread.currentThread().getStackTrace()[1].getMethodName() + "(" + String.join(",", key, value) + ")");
		this.accountMap.put(key, value);
	}

}