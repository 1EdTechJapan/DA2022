import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;

import org.apache.log4j.Logger;
import org.w3c.dom.Document;
import org.w3c.dom.Element;


/**
 * API-MakerにLTI関連の情報を取得させるクラス
 */
public class LtiApi extends BaseApi {

	/**
	 * Logger.
	 */
	private static final Logger LOG = Logger.getLogger(LtiApi.class);

	/**
	 * LTIプラットフォーム取得のAPI名
	 */
	private static final String LTI_PLATFORM_LIST = "lti_get_platform_list";

	/**
	 * API名。
	 */
	private String ifName;

	/**
	 * 検索条件の格納用変数
	 */
	private String where;

	/**
	 * iss指定
	 */
	private String iss;

	/**
	 * クライアントID指定
	 */
	private String clientId;

	/**
	 * デプロイメントID指定
	 */
	private String deploymentId;


	/**
	 * コンストラクタ
	 *
	 * @param option APIオプションエンティティ
	 */
	public LtiApi(ApiOptionalEntity option) {
		super(option);
	}


	/**
	 * API-Makerに一覧取得の要求を送信して戻り値を取得する
	 * @return API-Makerから返却されたXML
	 */
	@Override
	protected Document request() {
		LOG.debug("request start");
		String xml = null;
		try {
			Document doc = createDocument();

			Element ifElem = this.createIf(doc, ifName, where, null, null);

			if (iss != null && !iss.isEmpty()) {
				// iss情報が設定されている場合
				Element iss = this.createColumn(doc, "ISS", this.iss);
				ifElem.appendChild(iss);
			}
			if (clientId != null && !clientId.isEmpty()) {
				// クライアントIDが設定されている場合
				Element clientId = this.createColumn(doc, "CLIENT_ID", this.clientId);
				ifElem.appendChild(clientId);
			}
			if (deploymentId != null && !deploymentId.isEmpty()) {
				// デプロイメントIDが設定されている場合
				Element deploymentId = this.createColumn(doc, "DEPLOYMENT_ID", this.deploymentId);
				ifElem.appendChild(deploymentId);
			}

			doc.appendChild(ifElem);

			xml = this.xmlToStr(doc);
			LOG.debug(xml);
		} catch (ParserConfigurationException | TransformerException e) {
			LOG.error(e);
			return null;
		}
		return requestApi(ifName, xml);
	}

	/**
	 * LTIプラットフォーム一覧を取得する
	 * 各種パラメタは事前設定しておく必要がある
	 *
	 * @return LTIプラットフォーム一覧のXML形式のデータリスト
	 */
	public Document getLtiPlatformList() {
		this.ifName = LTI_PLATFORM_LIST;
		Document doc = request();
		return doc;
	}

	/**
	 *
	 * @param where セットする where
	 */
	public void setWhere(String where) {
		this.where = where;
	}

	/**
	 *
	 * @param iss セットする iss
	 */
	public void setIss(String iss) {
		this.iss = iss;
	}

	/**
	 *
	 * @param clientId セットする clientId
	 */
	public void setClientId(String clientId) {
		this.clientId = clientId;
	}

	/**
	 *
	 * @param deploymentId セットする deploymentId
	 */
	public void setDeploymentId(String deploymentId) {
		this.deploymentId = deploymentId;
	}

}
