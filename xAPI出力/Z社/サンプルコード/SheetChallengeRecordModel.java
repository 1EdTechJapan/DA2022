import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * シート実施結果のモデルクラス
 * 
 */
public class SheetChallengeRecordModel implements ICsvRecordModel {

	/** eポータルID */
	private String eportalId;
	/** eポータルユーザID */
	private String eportalUserId;
	/** シートID */
	private String sheetId;
	/** シート実施ペンまーるユーザID */
	private int challengeUserId;
	/** シート実施開始時刻 */
	private Date challengeStartDate;
	/** シート実施終了時刻 */
	private Date challengeEndDate;
	/** 得点 */
	private int score;
	/** ドリル学年 */
	private String drillGrade;
	/** ドリル教科 */
	private String curriculum;
	/** ドリル名 */
	private String drillName;
	/** シート名 */
	private String sheetName;

	/**
	 * eポータルID
	 *
	 * @return eポータルID
	 */
	public String getEportalId() {
		return eportalId;
	}

	/**
	 * eポータルID
	 *
	 * @param eportalId eポータルID
	 */
	public void setEportalId(String eportalId) {
		this.eportalId = eportalId;
	}

	/**
	 * eポータルユーザID
	 *
	 * @return eポータルユーザID
	 */
	public String getEportalUserId() {
		return eportalUserId;
	}

	/**
	 * eポータルユーザID
	 *
	 * @param eportalUserId eポータルユーザID
	 */
	public void setEportalUserId(String eportalUserId) {
		this.eportalUserId = eportalUserId;
	}

	/**
	 * シートID
	 *
	 * @return シートID
	 */
	public String getSheetId() {
		return sheetId;
	}

	/**
	 * シートID
	 *
	 * @param sheetId シートID
	 */
	public void setSheetId(String sheetId) {
		this.sheetId = sheetId;
	}

	/**
	 * シート実施ペンまーるユーザID
	 *
	 * @return シート実施ペンまーるユーザID
	 */
	public int getChallengeUserId() {
		return challengeUserId;
	}

	/**
	 * シート実施ペンまーるユーザID
	 *
	 * @param challengeUserId シート実施ペンまーるユーザID
	 */
	public void setChallengeUserId(int challengeUserId) {
		this.challengeUserId = challengeUserId;
	}

	/**
	 * シート実施開始時刻
	 *
	 * @return シート実施開始時刻
	 */
	public Date getChallengeStartDate() {
		return challengeStartDate;
	}

	/**
	 * シート実施開始時刻
	 *
	 * @param challengeStartDate シート実施開始時刻
	 */
	public void setChallengeStartDate(Date challengeStartDate) {
		this.challengeStartDate = challengeStartDate;
	}

	/**
	 * シート実施終了時刻
	 *
	 * @return シート実施終了時刻
	 */
	public Date getChallengeEndDate() {
		return challengeEndDate;
	}

	/**
	 * シート実施終了時刻
	 *
	 * @param challengeEndDate シート実施終了時刻
	 */
	public void setChallengeEndDate(Date challengeEndDate) {
		this.challengeEndDate = challengeEndDate;
	}

	/**
	 * 得点
	 *
	 * @return 得点
	 */
	public int getScore() {
		return score;
	}

	/**
	 * 得点
	 *
	 * @param score 得点
	 */
	public void setScore(int score) {
		this.score = score;
	}

	/**
	 * ドリル学年
	 *
	 * @return ドリル学年
	 */
	public String getDrillGrade() {
		return drillGrade;
	}

	/**
	 * ドリル学年
	 *
	 * @param drillGrade ドリル学年
	 */
	public void setDrillGrade(String drillGrade) {
		this.drillGrade = drillGrade;
	}

	/**
	 * ドリル教科
	 *
	 * @return ドリル教科
	 */
	public String getCurriculumId() {
		return curriculum;
	}

	/**
	 * ドリル教科
	 *
	 * @param curriculum ドリル教科
	 */
	public void setCurriculumId(String curriculum) {
		this.curriculum = curriculum;
	}

	/**
	 * ドリル名
	 *
	 * @return ドリル名
	 */
	public String getDrillName() {
		return drillName;
	}

	/**
	 * ドリル名
	 *
	 * @param drillName ドリル名
	 */
	public void setDrillName(String drillName) {
		this.drillName = drillName;
	}

	/**
	 * シート名
	 *
	 * @return シート名
	 */
	public String getSheetName() {
		return sheetName;
	}

	/**
	 * シート名
	 *
	 * @param sheetName シート名
	 */
	public void setSheetName(String sheetName) {
		this.sheetName = sheetName;
	}

	@Override
	public Map<String, String> getStringMap() {
		Map<String, String> map = new HashMap<String, String>();
		map.put(CommonXApiDefine.EPORTAL_ID, this.eportalId);
		map.put(CommonXApiDefine.EPORTAL_USER_ID, this.eportalUserId);
		map.put(CommonXApiDefine.SHEET_ID, this.sheetId);
		map.put(CommonXApiDefine.CHALLENGE_USER_ID, String.valueOf(this.challengeUserId));
		map.put(CommonXApiDefine.SCORE, String.valueOf(this.score));
		map.put(CommonXApiDefine.GRADE, this.drillGrade);
		map.put(CommonXApiDefine.CURRICULUM, this.curriculum);
		map.put(CommonXApiDefine.DRILL_NAME, this.drillName);
		map.put(CommonXApiDefine.SHEET_NAME, this.sheetName);
		// 日付をISO8601拡張形式に直す
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX");
		map.put(CommonXApiDefine.CHALLENGE_START_DATE, sdf.format(this.challengeStartDate));
		map.put(CommonXApiDefine.CHALLENGE_END_DATE, sdf.format(this.challengeEndDate));
		return map;
	}
}
