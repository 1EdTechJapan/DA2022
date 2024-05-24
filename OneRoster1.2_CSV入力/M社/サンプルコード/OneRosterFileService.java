import java.io.File;
import java.nio.charset.MalformedInputException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.text.Normalizer;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang3.BooleanUtils;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.MessageSource;
import org.springframework.context.NoSuchMessageException;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

/***
 * OneRosterファイル検証・名簿データ生成サービス実装クラス
 */
@Component
public class OneRosterFileService {

	/** logger */
	private final Logger logger = LoggerFactory.getLogger(this.getClass());

	/*** messageProperties */
	@Autowired
	private MessageSource messageProperties;

	/*** resourceProperties */
	@Autowired
	private MessageSource resourceProperties;
		
	/** 定数：特別クラス */
	private static final String CHECK_SPECIALCLASS = "特別";

	/** 定数：指導者 */
	private static final String CHECK_TEACHER = "指導者";
	
	/** 定数：出席番号最大値 */
	private static final int ATTENDANCENO_MAX = 255;
	
	/** 定数：ログインID桁数最大値 */
	private static final int LOGINID_MAX = 255;
		
	/** ユーザー種別：指導者 */
	private static final short TEACHER = 1;

	/** ユーザー種別：生徒 */
	private static final short STUDENT = 2;

	/** 学校種別：高校 */
	private static final int TYPE_HIGH_SCHOOL = 1;
	/** 学校種別：大学 */
	private static final int TYPE_UNIVERSITY = 2;
	/** 学校種別：小中一貫校 */
	private static final int TYPE_PRIMARY_AND_2ND_SCHOOL = 3;
	/** 学校種別：中高一貫校 */
	private static final int TYPE_MIDDLE_AND_HIGH_SCHOOL = 4;
	
	/** 内容判定用：学年最大値 */
	private static final int CHECK_GRADENO_MAX = 18;

	/** 内容判定用：組最大値 */
	private static final int CHECK_CLASSNO_MAX = 20;

	/** 内容判定用：特別クラス名桁数 */
	private static final int CHECK_CLASS_NAME_DIGIT = 10;

	/** 内容判定用：氏名桁数 */
	private static final int CHECK_USERNAME_DIGIT = 30;

	/**
	 * OneRoster名簿アップロード処理.
	 * <p>
	 * アップロードされたZIPファイルを解凍して検証し名簿データに変換する<br>
	 * 検証エラーがあれば errorMessage にその内容を格納して返す
	 * </p>
	 *
	 * @param file アップロードファイル
	 * @param orgId 組織ID
	 * @param schoolId 学校ID
	 * @param lang ロケール
	 * @return 結果格納Map
	 */
	public final Map<String, Object> uploadOneRosterFileBulk(
			MultipartFile file, String orgId, String schoolId, Locale lang) {

		Map<String, Object> returnMap = new HashMap<String, Object>();
		String error = ""; // ファイル検証エラーメッセージ
		String pre = messageProperties.getMessage("oneroster_error", null, lang); // 検証エラー接頭辞 OneRoster規格外エラー：
		String filePath = ""; // 自社独自領域のため詳細は割愛。この部分でシステムフォルダ内にファイル保存先の一時パスを生成する
		File tmpDir = new File(filePath);
		try {
			// アップロードファイル一時保存・zip解凍処理
			/**
			* *********************************************
			* 自社独自領域のため詳細は割愛
			* zip解凍エラーがあれば専用メッセージを格納して処理を中断する
			* *********************************************
			*/ 

			 
			// 一時フォルダ内のデータ数を評価
			File[] listFiles = tmpDir.listFiles();
			if (listFiles == null || listFiles.length == 0) { // ファイルなしエラー
				error = pre + messageProperties.getMessage("file_not_exist", null, lang);
				return returnMap;
			}
			// CSVファイル検証・ロード情報格納
			Map<String, List<List<String>>> loadMap = new HashMap<String, List<List<String>>>();
			Map<String, String> valMap = Arrays.asList(resourceProperties.getMessage("manifest_valid", null, lang)
					.split("/")).stream().collect(Collectors.toMap(d -> d.split(",")[0], d -> d.split(",", 2)[1]));
			Map<String, List<String>> checkMap = new HashMap<String, List<String>>(); // 設定値相対チェック用
			// 一時フォルダ内の全CSVファイルをループ処理し、データの取得と検証、格納を行う
			for (File f : listFiles) {
				if (!FilenameUtils.getExtension(f.getName()).toUpperCase().equals("CSV")) { // ファイル拡張子エラー
					error = pre + messageProperties.getMessage("invalid_fileType", null, lang)
							+ "(" + f.getName() + ")";
					return returnMap;
				}
				// ファイルの内容を1行で1要素のデータとして読みだす(UTF-8以外なら MalformedInputException が発生)
				List<String> lines = Files.readAllLines(f.toPath(), StandardCharsets.UTF_8);
				if (lines.size() <= 1) { // データサイズエラー(ヘッダー行しか含まれていない場合もNG)
					error = pre + messageProperties.getMessage("file_not_exist", new String[]{f.getName()}, lang);
					return returnMap;
				}
				// ファイルBOMチェック
				/**
				* *********************************************
				* 自社独自領域のため詳細は割愛
				* *********************************************
				*/


				// ファイルをbyte配列に変換して評価する。BOM付きならばMalformedInputExceptionを throwして処理を中断する

				// ファイル名・ヘッダー情報判定：リソース取得成功＆ヘッダー情報一致のみ許可
				String header, key = FilenameUtils.getBaseName(f.getName());
				try {
					// ファイル名と一致するヘッダーリソース情報を取得
					header = resourceProperties.getMessage(f.getName(), null, lang);
				} catch (NoSuchMessageException e) {
					// ヘッダーリソース取得失敗
					if (valMap.get("file.").contains(key)) { // 検証Mapの"file"に含まれる名称ならエラー扱いしない
						loadMap.put(key, new ArrayList<List<String>>()); // OneRoster定義済みファイル：空データのみ格納
						continue;
					}
					// 未定義ファイル混入エラー
					error = pre + messageProperties.getMessage("invalid_fileheader", new String[]{f.getName()}, lang);
					return returnMap;
				}
				
				// 1行1要素のListの各列を分割した二次元Listに変換する
				List<List<String>> loadData = convertLinesToMatrix(lines);
				if (loadData.size() == 1) { // ヘッダー行以外で値""囲みなしエラー：行/列番号を出力
					error = pre + messageProperties.getMessage("double_quote_error", 
									new String[]{f.getName(), loadData.get(0).get(0), loadData.get(0).get(1)}, lang);
					return returnMap;
				}
				// ヘッダー内容評価
				String[] headers = header.split("/", -1);
				if (!String.join(",", loadData.get(0)).startsWith(headers[0])) { // ヘッダー情報不一致エラー
					error = pre + messageProperties.getMessage("invalid_fileheader", new String[]{f.getName()}, lang);
					return returnMap;
				}
				// 取得情報格納
				loadMap.put(key + "Header", new ArrayList<List<String>>()); // ヘッダー情報格納
				loadMap.get(key + "Header").add(Arrays.asList(headers));
				loadMap.put(key, loadData); // key:ファイル名 value:行列リスト としてロードデータを格納
				// 相対チェック用データ格納
				for (int i = 1; i < loadData.size(); i++) {
					if (i == 1) {
						checkMap.put(key + "SourcedId", new ArrayList<String>());
						if (key.equals("orgs")) {
							checkMap.put("orgsType", new ArrayList<String>());
						} else if (key.equals("users")) {
							checkMap.put("userMasterIdentifier", new ArrayList<String>());
						}
					}
					if (checkMap.get(key + "SourcedId").contains(loadData.get(i).get(0))) { // sourcedId重複エラー
						error = pre + messageProperties.getMessage("duplicated_error", 
								   new String[]{key + "SourcedId"}, lang) + "(" + key + ".csv)";
								return returnMap;
					} else {
						checkMap.get(key + "SourcedId").add(loadData.get(i).get(0));
					}
					if (key.equals("orgs")) {
						checkMap.get("orgsType").add(loadData.get(i).get(loadData.get(0).indexOf("type")));
					} else if (key.equals("users")) {
						if (checkMap.get("userMasterIdentifier").contains(// userMasterIdentifier重複エラー
								loadData.get(i).get(loadData.get(0).indexOf("userMasterIdentifier")))) {
							error = pre + messageProperties.getMessage("duplicated_error", 
									   new String[]{"userMasterIdentifier"}, lang) + "(" + key + ".csv)";
									return returnMap;
						} else {
							checkMap.get("userMasterIdentifier").add(
									loadData.get(i).get(loadData.get(0).indexOf("userMasterIdentifier")));
						}
					}
				}
			}
			// 必須情報判定：manifestファイル評価
			if (!loadMap.containsKey("manifest")) { // manifestファイルなしエラー
				error = pre + messageProperties.getMessage("file_not_exist", null, lang) + "(manifest.csv)";
				return returnMap;
			}
			// manifestファイルの内容を1行ずつループし、定義内容を検証する
			for (int mi = 1; mi < loadMap.get("manifest").size(); mi++) {
				String[] col =
						loadMap.get("manifest").get(mi).toArray(new String[loadMap.get("manifest").get(mi).size()]);
				if (mi <= 2 && (valMap.get(col[0]) == null || !col[1].equals(valMap.get(col[0])))) { // バージョン情報エラー
					error = pre + messageProperties.getMessage("validation_error", null, lang);
				} else if (col[0].indexOf("file.") == 0) {
					// CSVファイル定義内容＆格納値検証
					col[0] = col[0].split("\\.")[1]; // ファイル名(拡張子無し)に置換
					if (!valMap.get("file.").contains(col[0]) // ファイル名不正 or absent存在 or 列挙型不正
							|| (loadMap.containsKey(col[0]) && col[1].equals("absent"))
							|| (!col[1].equals("absent") && !col[1].equals("bulk") && !col[1].equals("delta"))) {
						error = pre + messageProperties.getMessage("inoperable_error", null, lang);
					} else if (!loadMap.containsKey(col[0]) && (col[1].equals("bulk") || col[1].equals("delta"))) {
						error = pre + messageProperties.getMessage("file_not_exist", null, lang); // bulk/delta欠落
					} else if (loadMap.containsKey(col[0] + "Header")) {
						// エラーなし＆検証用ヘッダ格納済み：各データを検証
						if (valMap.get("requires").contains(col[0])) { // 名簿必須ファイル：取得済みとして必須欄から削除
							valMap.put("requires", valMap.get("requires").replace(col[0], ""));
						}
						List<List<String>> loadData = loadMap.get(col[0]);
						String[] headers = loadMap.get(col[0] + "Header").get(0).get(1).split(",", -1);
						if (col[1].equals("delta")) { // deltaデータ：statusとdateLastModifiedを必須項目として検証
							headers[1] = "Not" + headers[1];
							headers[2] = "Not" + headers[2];
						}
						Map<String, List<String>> rolesMap = new HashMap<String, List<String>>(); // roles.csv 検証用
						for (int i = 1; i < loadData.size(); i++) { // ヘッダー以降の行を評価
							String chkValue = "", chkHeader = ""; // 同一レコード内設定矛盾検証用チェック値＆ヘッダー
							for (int j = 0; j < headers.length; j++) {
								String validOpt = headers[j];
								if (!StringUtils.isEmpty(validOpt)) {
									String target = loadData.get(i).get(j);
									String targetHeader = loadData.get(0).get(j);
									if (validOpt.startsWith("NotBlank") && StringUtils.isEmpty(target)) { // 必須項目欠落エラー
										error = pre + messageProperties.getMessage("missing_required_item", null, lang);
									} else if (validOpt.equals("MustBlank") && !StringUtils.isEmpty(target)) { // 空以外エラー
										error = pre + messageProperties.getMessage("must_blank_error", null, lang);
									} else if (validOpt.equals("MustBlank") || target.equals("NULL")
									   && col[0].equals("academicSessions") && targetHeader.equals("parentSourcedId")) {
										continue; // 空項目(正常)：データ型判定などはスキップ
									}
									if (!error.isEmpty()) { // エラーメッセージにファイル名と行番号、エラー項目を追加
										error += "(" + col[0] + ".csv "
											  + resourceProperties.getMessage("rowNumber_colone", new String[]{
													  		String.valueOf(i + 1), targetHeader}, lang) + ")";
										return returnMap;
									}
									if (col[0].equals("orgs")) {
										if (targetHeader.equals("parentSourcedId") && chkValue.equals("district")) {
											validOpt = "null"; // 教育委員会は設定値矛盾チェックのみ実施する
										} else if (targetHeader.equals("identifier")) { // コードパターン設定
											validOpt = "pattern:" + BooleanUtils.toString(chkValue.equals("district"),
											 "^(0[1-9]|[1-3][0-9]|4[0-7])\\d{4}$", // ←一致：教育委員会, ↓不一致：学校 
											 "^([A-H&&[^BEG]][1-2]|[BEG]1)(0[1-9]|[1-3][0-9]|4[0-7])[1-3][1-9]\\d{7}$");
										} else {
											validOpt = validOpt.split("\\|", 2)[1];
										}
									} else {
										validOpt = validOpt.split("\\|", 2)[1];
									}
									if (!validOpt.equals("null") && !StringUtils.isEmpty(target)) {
										if (!validOneRosterValue(validOpt, target)) { // データ型エラー
											error = pre + messageProperties.getMessage("invalid_valueType", null, lang)
											+ "(" + col[0] + ".csv " + resourceProperties.getMessage(
												"rowNumber_colone", new String[]{String.valueOf(i + 1),
																targetHeader + " \"" + target}, lang) + "\")";
											return returnMap;
										}
										if (validOpt.startsWith("uuid")) { // sourcedId存在確認
											List<String> list = null; // 確認先リスト取得
											if (targetHeader.equals("parentSourcedId")) {
												list = checkMap.get(col[0] + "SourcedId");
											} else if (targetHeader.matches("termSourcedIds|schoolYearSourcedId")) {
												list = checkMap.get("academicSessionsSourcedId");
											} else if (targetHeader.matches("classSourcedId|metadata.jp.homeClass")) {
												list = checkMap.get("classesSourcedId");
											} else if (targetHeader.equals("courseSourcedId")) {
												list = checkMap.get("coursesSourcedId");
											} else if (targetHeader.matches(
													"orgSourcedId|schoolSourcedId|primaryOrgSourcedId")) {
												list = checkMap.get("orgsSourcedId");
											} else if (targetHeader.equals("userProfileSourcedId")) {
												list = checkMap.get("userProfilesSourcedId");
											} else if (targetHeader.matches("userSourcedId|agentSourcedIds")
													|| col[0].equals("demographics") && j == 0) {
												list = checkMap.get("usersSourcedId");
											}
											if (list != null) {
												for (String t :target.split(",")) {
													if (!list.contains(t)) { // sourcedId不存在エラー
														error = pre
																+ messageProperties.getMessage("reference_not_exist", 
																		new String[]{col[0], String.valueOf(i + 1),
																				targetHeader, t}, lang);
														return returnMap;
													}
												}
											}
										}
									}
									if (col[0].matches("enrollments|orgs")) { // 同一レコード内設定矛盾検証
										if (targetHeader.matches("role|type")) {
											chkValue = target;
											chkHeader = targetHeader;
										} else if ((targetHeader.equals("primary") // enrollments：生徒設定矛盾 or
														&& chkValue.equals("student") && !target.matches("[Ff]alse"))
											|| (targetHeader.equals("parentSourcedId") && chkValue.equals("district")
												&& !(target.isEmpty() || target.equals("NULL")))) { // orgs：教育委員会所属先矛盾
											error = pre + messageProperties.getMessage("conflict_value",
													new String[]{col[0], String.valueOf(i + 1), chkHeader, chkValue, 
															targetHeader, target}, lang);
											return returnMap;
										}
									} else if (col[0].equals("roles")) { // roles設定検証値格納
										if (targetHeader.equals("userSourcedId")) {
											chkValue = target;
										} else if (targetHeader.equals("roleType")) {
											if (!rolesMap.containsKey(chkValue)) {
												rolesMap.put(chkValue, new ArrayList<String>());
											}
											rolesMap.get(chkValue).add(target);
										}
									}
									if (col[0].matches("classes|enrollments") && checkMap.containsKey("orgsType")
											&& targetHeader.equals("schoolSourcedId") && checkMap.get("orgsType").get(
													checkMap.get("orgsSourcedId").indexOf(target)).equals("district")) {
										error = pre + messageProperties.getMessage("conflict_value", // 所属先矛盾(教育委員会に所属)
												new String[]{col[0], String.valueOf(i + 1), targetHeader, target, 
														"orgs.csv:type", "district"}, lang);
										return returnMap;
									}
								}
							}
						}
						if (col[0].equals("roles")) { // roles.csv roleType検証
							for (List<String> list : rolesMap.values()) {
								if (!list.contains("primary")) { // 必須情報欠落エラー
									error = pre + messageProperties.getMessage("missing_required_data",
											new String[]{col[0], "roleType \"primary\""}, lang);
									return returnMap;
								}
							}
						}
					}
				}
				// manifestファイル定義エラー：接尾辞をつけて返却
				if (!error.isEmpty()) {
					error += "(manifest.csv：" + String.join(",", loadMap.get("manifest").get(mi)) + ")";
					return returnMap;
				}
			}
			if (!StringUtils.deleteWhitespace(valMap.get("requires")).isEmpty()) { // 名簿必須ファイル欠落エラー
				error = valMap.get("requires").trim().replace(" ", ".csv, ") + ".csv"; // 欠落ファイル名を繋げる
				error = messageProperties.getMessage("missing_required_any", new String[]{error}, lang);
				return returnMap;
			}
			// 学校sourcedId取得・検証 ※学校情報が単一ならその学校の名簿とみなす
			Map<String, Object> schoolMap = new HashMap<String, Object>();
			// 学校情報取得処理 
			/**
			* *********************************************
			* 自社独自領域のため詳細は割愛
			* この部分でデータベースから学校情報を格納したMapを取得する
			* *********************************************
			*/

			String schoolCode = (String) schoolMap.get("SchoolCode");
			String schoolName = (String) schoolMap.get("SchoolName");
			String sid = "";
			int schoolCnt = 0;
			List<String> idxs = loadMap.get("orgs").get(0);
			// orgs.csvのレコードをループし、登録対象の学校を特定する
			for (List<String> row : loadMap.get("orgs")) {
				if (!row.equals(idxs) && row.get(idxs.indexOf("type")).equals("school")) {
					sid = row.get(0);
					if (!schoolCode.isEmpty() && row.get(idxs.indexOf("identifier")).equals(schoolCode)
							|| row.get(idxs.indexOf("name")).equals(schoolName)) { // 学校コードor学校名一致
						schoolCnt = 1;
						break;
					}
					schoolCnt++;
				}
			}
			if (sid.isEmpty()) { // 学校情報欠落エラー
				error = messageProperties.getMessage("missing_required_any", new String[]{
						resourceProperties.getMessage("school_info", null, lang)}, lang) + "(orgs.csv)";
			} else if (schoolCnt > 1) { // 学校特定失敗エラー(複数の学校情報が混在)
				if (schoolCode.isEmpty()) { // 学校コード無し
					error = messageProperties.getMessage("multiple_school_data", null, lang);
				} else { // 学校名・学校コード不一致
					error = messageProperties.getMessage("discrepancy_school_data", null, lang);
				}
			} else { // 学校特定成功：名簿情報検証・登録用データ生成処理
				returnMap.put("schoolSourcedId", sid);						// 名簿ファイル検証用(一致する情報のみ取得する)
				returnMap.put("schoolType", schoolMap.get("SchoolType"));	// 学年コード使用範囲判定用
				createBulkDataFromOneRoster(returnMap, loadMap, orgId, schoolId, lang);
				@SuppressWarnings("unchecked")
				List<Map<String, Object>> castList = (List<Map<String, Object>>) returnMap.get("loadDataList");
				if (castList.size() == 0) { // 検証結果O件エラー
					error = messageProperties.getMessage("data_not_exist",
								new String[]{FilenameUtils.getName(file.getOriginalFilename())}, lang);
				}
			}
		} catch (MalformedInputException e) { // OneRoster規格外：文字コードエラー
			error = pre + messageProperties.getMessage("invalid_charCode", null, lang);
		} catch (Exception e) { // 予期せぬエラー：ログ出力
			error = messageProperties.getMessage("unexpected_error", null, lang);
			logger.error(e.getMessage(), e);
		} finally { // エラーメッセージ格納・一時フォルダ削除
			returnMap.put("errorMessage", error);
			FileUtils.deleteQuietly(tmpDir);
		}
		return returnMap;
	}
	
	/**
	 * OneRoster項目値検証処理.
	 * <p>検証オプションに設定した内容で対象値を検証した結果を返す</p>
	 *
	 * @param validOpt 検証オプション(date:日付/ enum:列挙型(|区切りで記述)/bool:真偽値/uuid：UUID型/pattern:正規表現 のいずれかを指定)
	 * @param target 検証対象値
	 * @return result 検証結果(OK:true NG:false)
	 */
	private boolean validOneRosterValue(String validOpt, String target) {
		boolean result = true;
		String regExp = "", targets = target; // 正規表現パターンチェック用
		if (validOpt.startsWith("date")) { // 日付：フォーマット失敗ならNG
			try {
				new SimpleDateFormat(validOpt.split(":")[1]).parse(target);
			} catch (Exception e) {
				result = false;
			}
		} else if (validOpt.startsWith("enum")  && !target.startsWith("ext") // 列挙型(拡張型以外)：列挙値に含まれなければNG
				 		&& !Arrays.asList(validOpt.split(":")[1].split("\\|")).contains(target)) {
			result = false;
		} else if (validOpt.equals("bool")) { // 真偽値：パターン不一致ならNG ※パスカル記法も許容
			result = target.matches("[Tt]rue|[Ff]alse");
		} else if (validOpt.startsWith("uuid")) { // UUID形式：パターン設定
			targets = target.toLowerCase(); // アルファベット大文字も許容するよう小文字のみに置換
			final int[] varRange = {1, 5}; // バージョン範囲
			regExp = "([0-9a-f]{8})-([0-9a-f]{4})-";
			if (rangeCheck(validOpt.replace("uuid", ""), varRange[0], varRange[1])) { // バージョン指定あり
				regExp += "(" + validOpt.replace("uuid", "") + "[0-9a-f]{3})-([0-9a-f]{4})-([0-9a-f]{12})";
			} else {
				regExp += "([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})";
			}
		} else if (validOpt.startsWith("pattern")) { // 正規表現パターン：パターン設定
			regExp = validOpt.split(":", 2)[1];
			if (regExp.equals("notHalfKana")) { // 半角カナ禁止：パターンを設定(始端終端の空白も禁止)
				regExp = "(?!.*[\uFF65-\uFF9F].*)(?!^[\\s|^　].*)(?!.*[\\s|^　]$).+";
			}
		}
		if (!regExp.isEmpty()) { // 正規表現チェック(複数の値を検証可能)：パターン不一致ならNG
			for (String t : targets.split(",")) {
				result = t.matches(regExp);
				if (!result) {
					break;
				}
			}
		}
		return result;
	}

	/**
	 * OneRoster CSV読み込みデータ 行列リスト変換処理.
	 * <p>readAllLinesで取得した1要素1行分の文字列Listを1文字単位で分割し、行-列の二次元リストに変換して返す</p>
	 *
	 * @param lines 行リスト
	 * @return 行列リスト ※ヘッダー行以外で値が""で囲まれていない場合は、該当した行/列番号のみ格納する
	 */
	private List<List<String>> convertLinesToMatrix(List<String> lines) {
		List<List<String>> list = new ArrayList<List<String>>();
		for (int i = 0; i < lines.size(); i++) {
			if (lines.get(i).contains("\"")) { // 文字列中に"が含まれていれば、1文字ずつ分割して評価
				StringBuilder sb = new StringBuilder();
				boolean notString = true;
				List<String> cols = new ArrayList<String>(); // 列データ格納用リスト
				int colCnt = 1, dqCnt = 0; // 列＆"カウンター
				for (String c : lines.get(i).split("")) {
					if (c.equals(",") && notString) {
						if (dqCnt < 2) { // 0～1のまま列尾処理：""囲み無しエラー
							list.clear();
							list.add(Arrays.asList(String.valueOf(i + 1), String.valueOf(colCnt)));
							return list;
						}
						dqCnt = 0;
						colCnt++;
						cols.add(sb.toString());
						sb.delete(0, sb.length());
					} else if (c.equals("\"")) {
						notString = !notString;
						dqCnt++;
					} else {
						sb.append(c);
					}
				}
				if (dqCnt < 2) { // 0～1のまま行尾処理：""囲み無しエラー
					list.clear();
					list.add(Arrays.asList(String.valueOf(i + 1), String.valueOf(colCnt)));
					return list;
				} else {
					cols.add(sb.toString()); // 最後列の要素を格納
				}
				list.add(cols);
			} else { 
				if (i == 0) { // ヘッダー行：カンマで分割して格納
					list.add(Arrays.asList(lines.get(i).split(",", -1)));
				} else if (lines.get(i).length() > 0) { // ヘッダー行以外で囲み無しはエラー(改行のみは読み飛ばす)
					list.clear();
					list.add(Arrays.asList(String.valueOf(i + 1), "1"));
					break;
				}
			}
		}
		return list;
	}
	
	/**
	 * OneRoster名簿検証・登録用名簿データ生成処理.
	 * <p>学籍クラスの所属者またはその他の指導者情報を集計し、登録用の名簿データを生成する</p>
	 *
	 * @param returnMap 返却用データMap(追加データ格納先)
	 * @param loadMap ロード情報Map
	 * @param orgId 組織ID
	 * @param schoolId 学校ID
	 * @param language ロケール
	 */
	private void createBulkDataFromOneRoster(Map<String, Object> returnMap,
			Map<String, List<List<String>>> loadMap, String orgId, String schoolId, Locale language) {
		List<Map<String, Object>> emptyList = new ArrayList<Map<String, Object>>(); // 空リスト
		String sid = (String) returnMap.get("schoolSourcedId");
		// 学年コード取得・クラス情報格納
		int schoolType = Integer.parseInt(String.valueOf((short) returnMap.get("schoolType"))); // 学校種別
		String grades = "P1,P2,P3,P4,P5,P6/J1,J2,J3/H1,H2,H3";
		if (schoolType <= TYPE_HIGH_SCHOOL) {						// 小中高いずれか：対応する学年コードを使用
			grades = grades.split("/")[schoolType - 1];
		} else if (schoolType == TYPE_PRIMARY_AND_2ND_SCHOOL) {	// 小中一貫校：P1～J3を使用
			grades = grades.substring(0, grades.lastIndexOf("/")).replace("/", ",");
		} else if (schoolType == TYPE_MIDDLE_AND_HIGH_SCHOOL) {	// 中高一貫校：J1～H3を使用
			grades = grades.substring(grades.indexOf("/") + 1).replace("/", ",");
		} else if (schoolType == TYPE_UNIVERSITY) {					// 大学：学年コード非対応
			grades = "";
		} else {														// それ以外：P1～H3までの全学年コードを使用
			grades = grades.replace("/", ",");
		}
		List<String> gradeCodes = Arrays.asList(grades.split(",")); // 学年コードリスト化(学年変換用)
		String gradeSuf = resourceProperties.getMessage("year_grade", null, language);	// 年
		String classSuf = resourceProperties.getMessage("unit_class", null, language);	// 組
		String kansuji = "零一二三四五六七八九十";
		String alphabet = String.valueOf(
			IntStream.rangeClosed('A', 'Z').mapToObj(c -> "" + (char) c).collect(Collectors.joining()).toCharArray());
		Map<String, List<String>> classMap = new HashMap<String, List<String>>(); // classSourcedId:[学年, 組, クラス名]を保持
		List<String> idxs = loadMap.get("classes").remove(0); // ヘッダー情報(インデックス検索用)
		for (List<String> cols : loadMap.get("classes")) {
			if (cols.get(idxs.indexOf("classType")).equals("homeroom")
					&& sid.equals(cols.get(idxs.indexOf("schoolSourcedId")))) { // 学籍クラス＆学校soursedId一致
				String gradeNo = "", classNo = "", className = ""; // 組取得失敗ならclassNameにtitle入れることで、
				if (!StringUtils.isEmpty(cols.get(idxs.indexOf("grades")))) {
					gradeNo = cols.get(idxs.indexOf("grades"));
					if (!grades.isEmpty() && grades.contains(gradeNo)) { // 学年コード一致：学年に変換
						gradeNo = String.valueOf(gradeCodes.indexOf(gradeNo) + 1);
					}
					// 数字以外の文字と18超えの数字は空文字に置換(何も残らなければclassCodeから取得)
					gradeNo = gradeNo.replaceAll("\\D", "");
					gradeNo = BooleanUtils.toString(rangeCheck(gradeNo, 1, CHECK_GRADENO_MAX), gradeNo, "");
				}
				if (!StringUtils.isEmpty(cols.get(idxs.indexOf("classCode")))) {
					String classCode = cols.get(idxs.indexOf("classCode"));
					if (classCode.matches(".*\\d{2}.*\\d{2}.*")) { // 数字2桁×2を含む
						classNo = classCode.replaceAll("[^\\d{2}]", ""); // 数字2桁部分のみを取り出す
						if (gradeNo.isEmpty()) {
							gradeNo = classNo.substring(0, 2); // 上位2桁を学年とみなす(18超えは空文字に置換)
							gradeNo = BooleanUtils.toString(rangeCheck(gradeNo, 1, CHECK_GRADENO_MAX), gradeNo, "");
						}
					} else if (classCode.matches(".*(" + grades.replace(",", "|") + ").*\\d{2}.*")) { // 学年コード+数字2桁を含む
						classNo = classCode.replaceAll("[^(" + grades.replace(",", "|") + ")\\d{2}]", "");
						if (gradeNo.isEmpty()) {
							gradeNo = String.valueOf(gradeCodes.indexOf(classNo.substring(0, 2)) + 1);
						}
					}
					if (!classNo.isEmpty()) {
						classNo = classNo.substring(2); // 下位2桁を組とみなす(20超えは空文字に置換)
						classNo = BooleanUtils.toString(rangeCheck(classNo, 1, CHECK_CLASSNO_MAX), classNo, "");
					}
				}
				String title = Normalizer.normalize(cols.get(idxs.indexOf("title")), Normalizer.Form.NFKC); // クラス名
				if (gradeNo.isEmpty() && title.matches(".+" + gradeSuf + ".*")) { // 学年無し＆クラス名が 〇年 に一致
					gradeNo = title.split(gradeSuf)[0];
					if (kansuji.contains(gradeNo)) { // 学年が漢数字
						gradeNo = String.valueOf(kansuji.indexOf(gradeNo));
					} else if (alphabet.contains(gradeNo.toUpperCase())) { // 学年が英字1文字：数値変換
						gradeNo = String.valueOf(alphabet.indexOf(gradeNo) + 1);
					}
					gradeNo = BooleanUtils.toString(
							rangeCheck(gradeNo.replaceAll("\\D", ""), 1, CHECK_GRADENO_MAX), gradeNo, "");
				}
				if (classNo.isEmpty() && title.matches(".+" + classSuf + ".*")) { // 組無し＆クラス名が △組 に一致
					if (title.matches(".*" + gradeSuf + ".*")) {
						classNo = title.substring(title.indexOf(gradeSuf) + 1).split(classSuf)[0];
					} else {
						classNo = title.split(classSuf)[0];
					}
					if (kansuji.contains(classNo)) { // 組が漢数字
						classNo = String.valueOf(kansuji.indexOf(classNo));
					} else if (alphabet.contains(classNo.toUpperCase())) { // 組が英字1文字：数値変換
						classNo = String.valueOf(alphabet.indexOf(classNo) + 1);
					}
					// 数字以外の文字と20以上の数字は空文字に置換(組は別途割り当てる)
					classNo = BooleanUtils.toString(
							rangeCheck(classNo.replaceAll("\\D", ""), 1, CHECK_CLASSNO_MAX), classNo, "");
				}
				if (gradeNo.isEmpty()) { // 学年未特定：特別クラスとみなす
					gradeNo = CHECK_SPECIALCLASS;
					if (title.length() > CHECK_CLASS_NAME_DIGIT) { // クラス名文字数超過
						title = title.substring(0, CHECK_CLASS_NAME_DIGIT); // 10文字に切り詰め
					}
					classNo = title; // 組はクラス名を設定
				} else {
					gradeNo = String.valueOf(Integer.parseInt(gradeNo)); // 学年特定：数値変換して0埋めを削除
					if (!classNo.isEmpty()) { // 組特定：数値変換して0埋めを削除
						classNo = String.valueOf(Integer.parseInt(classNo));
					} else {
						className = title;
					}
				}
				classMap.put(cols.get(0), Arrays.asList(gradeNo, classNo, className));
			}
		}
		// 所属情報格納(key:user_userSourcedId,value:[クラス情報, 期間]でtmpMapに追加)
		Map<String, List<String>> tmpMap = new HashMap<String, List<String>>();
		idxs = loadMap.get("enrollments").remove(0);
		for (List<String> cols : loadMap.get("enrollments")) {
			String uid = "user_" + cols.get(idxs.indexOf("userSourcedId"));
			String cid = cols.get(idxs.indexOf("classSourcedId"));
			String role = cols.get(idxs.indexOf("role"));
			String term = cols.get(idxs.indexOf("endDate")) + cols.get(idxs.indexOf("beginDate"));
			if (sid.equals(cols.get(idxs.indexOf("schoolSourcedId"))) // 学校soursedId一致＆指導者or学習者
					&& (role.equals("teacher") || role.equals("student"))) {
				if (role.equals("teacher") && !tmpMap.containsKey(uid)) { // 指導者＆未格納
					tmpMap.put(uid, new ArrayList<String>(Arrays.asList(CHECK_TEACHER, term)));
				} else if (role.equals("student") && classMap.containsKey(cid)) { // 学習者＆クラス情報あり
					if (tmpMap.containsKey(uid) && term.compareTo((String) tmpMap.get(uid).get(1)) <= 0) {
						continue; // 格納済み＆古い情報なら読み飛ばす
					}
					tmpMap.put(uid, new ArrayList<String>(Arrays.asList(cid, term)));
				}
			}
		}
		// 指導者情報はenrollmentsに含まれない可能性があるため、rolesがあれば参照する
		if (loadMap.get("roles") != null) {
			idxs = loadMap.get("roles").remove(0);
			for (List<String> cols : loadMap.get("roles")) {
				String uid = "user_" + cols.get(idxs.indexOf("userSourcedId"));
				String role = cols.get(idxs.indexOf("role"));
				if (sid.equals(cols.get(idxs.indexOf("orgSourcedId")))
						&& role.equals("teacher") && !tmpMap.containsKey(uid)) {
					tmpMap.put(uid, new ArrayList<String>(Arrays.asList(CHECK_TEACHER, "")));
				}
			}
		}
		
		// 名簿に使用するクラスに組の割当がなければ是正する
		idxs = new ArrayList<String>(); // 初期化：使用クラスIDを格納
		Map<String, List<String>> noMap = new HashMap<String, List<String>>(); // 出席番号採番用Map(クラスごとに保持)
		List<String> availableNoList = // 学習者クラス用番号一覧
				Arrays.asList(Arrays.stream(IntStream.rangeClosed(1, ATTENDANCENO_MAX).toArray())
				.mapToObj(String::valueOf).toArray(String[]::new));
			/**
			* *********************************************
			* 自社独自領域のため詳細は割愛
			* この部分でデータベースから値を取得し、指導者に未割当の番号Listを作成してnoMapに格納する
			* 登録用のユーザー情報から使用するクラス情報を読み出し、各学年の未割り当ての組情報を取得する
			* *********************************************
			*/

		for (Map.Entry<String, List<String>> entry : tmpMap.entrySet()) {
			if (entry.getKey().startsWith("user_")) {
				String classId = entry.getValue().get(0);
				if (!CHECK_TEACHER.equals(classId) && !idxs.contains(classId)) {
					idxs.add(classId);
					List<String> list = classMap.get(classId);
					if (!noMap.containsKey(list.get(0))) { // 学年をキーに割り当て済みの組を一覧として格納
						noMap.put(list.get(0), new ArrayList<String>());
					}
					if (!list.get(1).isEmpty()) { // 組設定あり：組と番号一覧を格納
						noMap.get(list.get(0)).add(list.get(1));
						noMap.put(String.join("-", list), new ArrayList<String>(availableNoList));
					}
				}
			}
		}
		// 参照用のクラス情報のうち組未格納のクラスを捜索
		for (Map.Entry<String, List<String>> entry : classMap.entrySet()) {
			if (idxs.contains(entry.getKey()) && entry.getValue().get(1).isEmpty()) { // 使用クラス＆組未割り当て
				for (int i = 1; i <= CHECK_CLASSNO_MAX; i++) {
					if (!noMap.get(entry.getValue().get(0)).contains(String.valueOf(i))) { // 組設定なし：未使用の最小組を割り当て
						entry.getValue().set(1, String.valueOf(i));
						entry.getValue().set(2, ""); // 退避していたクラス名を空文字に置換
						noMap.get(entry.getValue().get(0)).add(String.valueOf(i)); // 学年の組一覧に追加して番号一覧を格納
						noMap.put(String.join("-", entry.getValue()), new ArrayList<String>(availableNoList));
						break;
					}
				}
				if (entry.getValue().get(1).isEmpty()) { // 組割当失敗：特別クラス(クラス名も同じ)として登録
					entry.getValue().set(0, CHECK_SPECIALCLASS);
					entry.getValue().set(1, entry.getValue().get(2)); // 退避していたクラス名を組に設定
					entry.getValue().set(2, "");
					if (!noMap.containsKey(String.join("-", entry.getValue()))) { // 番号一覧を格納
						noMap.put(String.join("-", entry.getValue()), new ArrayList<String>(availableNoList));
					}
				}
			}
		}
		
		// 名簿検証・ユーザー情報格納 ※所属情報あり＆有効データのみ
		Map<String, Map<String, Object>> userMap = new TreeMap<String, Map<String, Object>>(); // キー値でソート
		List<String> loginIdList = new ArrayList<String>(); // ログインID重複チェック用
		idxs = loadMap.get("users").remove(0);
		for (List<String> cols : loadMap.get("users")) {
			if (tmpMap.containsKey("user_" + cols.get(0))
					&& "true".equals(cols.get(idxs.indexOf("enabledUser")).toLowerCase())) {
				List<String> list = tmpMap.get("user_" + cols.get(0)); // データ一時格納用リスト：所属情報を読み出し学年情報を格納
				Map<String, Object> map = new HashMap<String, Object>();
				String key = ""; // userMap格納キー(学年-組-番号の順になるよう値を設定)
				short type = TEACHER;
				if (list.get(0).equals(CHECK_TEACHER)) { // 指導者：組のみ格納
					map.put("Class", ""); // 組(指導者は空文字)
					key = list.get(0);
				} else { // 学習者：組、番号を格納
					type = STUDENT;
					list = classMap.get(list.get(0));
					try {
						map.put("Number", noMap.get(String.join("-", list)).remove(0)); // 番号(1～255)割り当て
					} catch (IndexOutOfBoundsException e) { // 割り当てられる番号がない：同学年の他の組、または他の学年の未使用組の学習者として登録
						String valueB = "";
						boolean isAllocated = false;
						if (!list.get(0).equals(CHECK_SPECIALCLASS) // 通常クラス＆割り当て可能組なし
								&& noMap.get(list.get(0)).size() == CHECK_CLASSNO_MAX) {
							for (int i = 1; i <= CHECK_GRADENO_MAX; i++) { // 未使用組がある学年を捜索
								valueB = String.valueOf(i);
								if (!noMap.containsKey(valueB) // 未使用の学年 or 未使用組のある学年
										|| noMap.get(list.get(0)).size() < CHECK_CLASSNO_MAX) {
									if (!noMap.containsKey(valueB)) {
										noMap.put(valueB, new ArrayList<String>());
									}
									classMap.get(tmpMap.get("user_" + cols.get(0)).get(0)).set(0, valueB); // 学年情報を差し替え
									break;
								}
							}
						}
						for (int i = 1; i <= CHECK_CLASSNO_MAX; i++) { // 未使用組検索
							if (list.get(0).equals(CHECK_SPECIALCLASS)) {
								valueB = resourceProperties.getMessage("special_class", null, language) + i;
							} else {
								valueB = String.valueOf(i);
							}
							if (!noMap.get(list.get(0)).contains(valueB)) { // クラス重複なし
								noMap.get(list.get(0)).add(valueB); // 学年の組一覧に追加
								classMap.get(tmpMap.get("user_" + cols.get(0)).get(0)).set(1, valueB); // 組情報を差し替え
								noMap.put(String.join("-", classMap.get(tmpMap.get("user_" + cols.get(0)).get(0))),
										new ArrayList<String>(availableNoList)); // 番号情報を追加
								isAllocated = true;
								break;
							}
						}
						if (!isAllocated) { // 未使用組検索失敗：番号割り当て失敗として登録しない
							logger.warn(
									"OneRoster:Excluded because the number of {} exceeds 255. schoolId:{} userName:{}",
									"students", schoolId, cols.get(idxs.indexOf("familyName"))
									+ cols.get(idxs.indexOf("middleName")) + cols.get(idxs.indexOf("givenName")));
							continue;
						}
						map.put("Number", noMap.get(String.join("-", list)).remove(0)); // 番号を再取得
					}
					map.put("Class", list.get(1)); // 組(学習者は 1～20 or 組名)
					if (list.get(0).equals(CHECK_SPECIALCLASS)) {
						key = "50" + list.get(0) + list.get(1); // 特別クラス：通常クラスより下に表示されるキー値を設定
					} else {
						key = String.format("%02d", Integer.valueOf(list.get(0)))
								+ String.format("%02d", Integer.valueOf(list.get(1))); // 通常クラス：学年と組を0埋め2桁で設定
					}
				}
				map.put("Grade", list.get(0)); // 学年(1～18 or 特別 or 指導者)
				list = new ArrayList<String>(); // 可変長リストに初期化し [姓, ミドルネーム, 名] の順に格納(希望名等があれば優先)
				list.add(StringUtils.defaultIfEmpty(
								cols.get(idxs.indexOf("preferredFamilyName")), cols.get(idxs.indexOf("familyName"))));
				list.add(StringUtils.defaultIfEmpty(
								cols.get(idxs.indexOf("preferredMiddleName")), cols.get(idxs.indexOf("middleName"))));
				list.add(StringUtils.defaultIfEmpty(
								cols.get(idxs.indexOf("preferredGivenName")), cols.get(idxs.indexOf("givenName"))));
				if (String.join("", list).length() > CHECK_USERNAME_DIGIT) { // 氏名桁数超過
					list.remove(1); // ミドルネーム削除
					if (String.join("", list).length() > CHECK_USERNAME_DIGIT) { // 姓名のみで30文字超
						list.set(0, String.join("", list).substring(0, CHECK_USERNAME_DIGIT));
						list.remove(1); // // 姓名でまとめて超過分は切りつめたため名前要素を削除
					}
				}
				map.put("Name", String.join("", list)); // 氏名(最大30文字)
				// ログインID：UUID一致ユーザーがいなければusername,emailで登録済みユーザー判定を実施
				map.put("UUID", StringUtils.defaultIfEmpty(// UUID：userMasterIdentifierがなければidentifierを設定
						cols.get(idxs.indexOf("userMasterIdentifier")), cols.get(idxs.indexOf("identifier"))));
				List<Map<String, Object>> users = new ArrayList<Map<String, Object>>();
				if (!map.get("UUID").toString().isEmpty()) {
				/**
				* *********************************************
				* 自社独自領域のため詳細は割愛
				* この部分でデータベースから値を取得し、変数usersにUUIDが一致するユーザー情報を格納する
				* *********************************************
				*/
					// 
					if (users.size() == 1 && schoolId.equals(users.get(0).get("SchoolId"))
							&& type == (short) users.get(0).get("UserType")
							&& !loginIdList.contains(users.get(0).get("LoginId").toString())) { // UUID一致ユーザー特定
						map.put("Password", new String(// パスワード
								Base64.getDecoder().decode(users.get(0).get("InitialPassword").toString())));
						if (map.get("Grade").equals(CHECK_TEACHER)
								&& !"0".equals(users.get(0).get("Number").toString())) { // 先生：今の番号を踏襲
							map.put("Number", users.get(0).get("Number").toString()); // 出席番号
						}
						map.put("LoginId", users.get(0).get("LoginId").toString()); // ログインID(最大255文字)
					}
				}
				if (!map.containsKey("LoginId")) { // UUID一致ユーザー未特定：username,emailで登録済みユーザーを検索
					list.clear(); // 検証用に初期化
					for (String colKey : "username,email".split(",")) {
						String lid = cols.get(idxs.indexOf(colKey)).replaceAll("[^\\w\\.\\-@]", "");
						if (lid.length() > LOGINID_MAX) {
							lid = lid.substring(0, LOGINID_MAX);
						}
						if (!lid.isEmpty() && !loginIdList.contains(lid) && !list.contains(lid)) {
							/**
							* *********************************************
							* 自社独自領域のため詳細は割愛
							* この部分でデータベースから値を取得し、変数usersにusernameまたはemailが一致するユーザー情報を格納する
							* *********************************************
							*/ 

							if (users.size() == 1 && schoolId.equals(users.get(0).get("SchoolId"))
									&& type == (short) users.get(0).get("UserType")) { // 登録済みユーザー：現パスワード＆状況追加
								map.put("Password", new String(// パスワード
										Base64.getDecoder().decode(users.get(0).get("InitialPassword").toString())));
								if (map.get("Grade").equals(CHECK_TEACHER)
										&& !"0".equals(users.get(0).get("Number").toString())) { // 先生：今の番号を踏襲
									map.put("Number", users.get(0).get("Number").toString()); // 出席番号
								}
								map.put("LoginId", lid); // ログインID(最大255文字)
								break; // 検索完了
							} else if (users.size() == 0 && !map.containsKey("LoginId")) { // 未登録ユーザー：ログインID仮格納
								map.put("LoginId", lid); // 他のlid候補でも登録済みユーザーを検索するが、どちらも未登録なら最初の値を採用
							}
						}
						list.add(lid); // usernameとemailが同じ値なら二度検証しないように格納
					}
				}
				if (!map.containsKey("LoginId")) { // ログインID未格納(値重複時)：一意なログインIDをハッシュ値から生成
					map.put("displayMessage", // ログインID割り当て済みメッセージを追加
							messageProperties.getMessage("assign_other_loginid", new String[]{list.get(0)}, language));
					/**
					* *********************************************
					* 自社独自領域のため詳細は割愛
					* この部分でユーザー情報等を用いてSHA-256によるハッシュ値を生成し、mapにログインIDとして格納する
					* *********************************************
					*/ 
				}
				if (!map.containsKey("Password")) { // パスワード未格納(新規ユーザー)：8桁パスワード生成・状況等デフォルト値追加
					/**
					* *********************************************
					* 自社独自領域のため詳細は割愛
					* この部分でユーザー情報等を用いてSHA-256によるハッシュ値を生成し、mapにパスワードとして格納する
					* *********************************************
					*/
					map.put("successFlg", true);
					map.put("userId", "");
					map.put("addMessage", "");
					if (!map.containsKey("displayMessage")) {
						map.put("displayMessage", ""); // ログインID割り当て済みメッセージがなければ格納
					}
				}
				if (!map.containsKey("Number")) { // 番号未格納(指導者新規登録時)：未使用の番号から最小値を割り当て
					try {
						map.put("Number", noMap.get(CHECK_TEACHER).remove(0));
					} catch (IndexOutOfBoundsException e) { // 指導者で割り当てられる番号がない場合は登録しない
						logger.warn("OneRoster:Excluded because the number of {} exceeds 255. schoolId:{} userName:{}",
								"teachers", schoolId, map.get("Name"));
						continue;
					}
				}
				loginIdList.add((String) map.get("LoginId")); // ログインID重複チェック用一覧に追加
				map.put("messages", emptyList); // エラー無しを示す空リストを格納
				userMap.put(key + String.format("%03d", Integer.valueOf((String) map.get("Number"))), map); // 学年-組-番号のキーで格納
			}
		}
		returnMap.put("errorCount", 0);
		returnMap.put("errorStatus", false);
		returnMap.put("errorDataList", emptyList);
		returnMap.put("loadDataList", new ArrayList<Map<String, Object>>(userMap.values()));
	}
	
	/**
	 * 対象の文字列が引数に指定された下限値～上限値の範囲内かチェックする.
	 *
	 * @param target チェック値
	 * @param lower 範囲の下限値
	 * @param upper 範囲の上限値
	 * @return true:範囲チェックOK false:範囲チェックNG
	 */
	private boolean rangeCheck(String target, int lower, int upper) {
		boolean res = false;
		try {
			int checkInt = Integer.parseInt(target);
			if (lower <= checkInt && checkInt <= upper) {
				res = true;
			}
		} catch (NumberFormatException e) { // 変換不可
			res = false;
		}
		return res;
	}
}
