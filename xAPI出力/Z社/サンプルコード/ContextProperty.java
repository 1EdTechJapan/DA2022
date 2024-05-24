import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * contextプロパティ作成時に値を保持するクラス
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ContextProperty extends CreateXApiStatementBase {

	private static final String PREFIX_ID = "http://id.tincanapi.com/activity/lrp/";
	private static final String CONTEXT = "context";
	private static final String CONTEXT_ACTIVITIES = "contextActivities";
	private static final String CATEGORY = "category";
	private static final String ID = "id";
	private static final String DEFINITION = "definition";
	private static final String TYPE = "type";
	private static final String TYPE_VALUE = "http://id.tincanapi.com/activitytype/source";

	/** ログ出力用 */
	private static Logger logger = Logger.getLogger(ActorProperty.class.getName());

	@JsonProperty("category")
	private List<Map> categoryList;
	@JsonProperty("contextActivities")
	private Map<String, Object> contextActivitiesMap;
	@JsonProperty("definition")
	private Map<String, Object> definitionMap;


	public ContextProperty() {
		categoryList = new ArrayList<>();
		contextActivitiesMap = new HashMap<String, Object>();
		definitionMap = new HashMap<String, Object>();
		definitionMap.put(TYPE, TYPE_VALUE);
		categoryList.add(definitionMap);
		contextActivitiesMap.put(CATEGORY, categoryList);
	}


	public void setContextActivitiesMap(String key, List<Map> value) {
		this.contextActivitiesMap.put(key, value);
	}

	public void setDefinitionMap(String key, String value) {
		this.definitionMap.put(key, value);
	}

	public String getContextProperty(String name, String version) {
		return "\"" + CONTEXT + "\":{\"" + CONTEXT_ACTIVITIES + "\":{\"" + CATEGORY
				+ "\":[{\"" + ID + "\":\"" + PREFIX_ID + name + "/" + version + "\",\"" + DEFINITION + "\":{\"" + TYPE + "\":\"" + TYPE_VALUE + "\"}}]}}";
	}
}
