package jp.commoncode.common;

import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;



/**
 * 文字列を処理します。
 *
 * @version 2013/07/03
 */
public class StringUtility {

    //------------------------------------------------------------------
    //- public static フィールド
    //------------------------------------------------------------------

    /** Driver名（quoteメソッドでエスケープする文字に影響する） */
    public static String DriverName = "";

    /** CSV区切り文字 */
    public static final char CSV_DELIMITER_CHAR = ',';

    /** CSV区切り文字列（引用符付き） */
    public static final String CSV_QUOTATION_DELIMITER = "\",\"";

    /** TSV区切り文字 */
    public static final char TSV_DELIMITER_CHAR = '\t';

    /** TSV区切り文字列（引用符付き） */
    public static final String TSV_QUOTATION_DELIMITER = "\"\t\"";

    /** 引用符文字列 */
    public static final String QUOTATION = "\"";

    /** 改行文字列 */
    public static final String NL = "\n";




    //------------------------------------------------------------------
    //- コンストラクタ
    //------------------------------------------------------------------

    /**
     * コンストラクタ
     */
    private StringUtility() {
        // 外部からの呼び出し禁止
    }



    //----------------------------------------------------------------------
    //- 日付時刻取得メソッド
    //----------------------------------------------------------------------

    /**
     * 日付文字列（8桁）を取得します。
     *
     * @return 日付文字列（8桁）
     */
    public static String getDateString() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        java.util.Date d = new java.util.Date();
        return sdf.format(d);
    }

    /**
     * 時刻文字列（6桁）を取得します。
     *
     * @return 時刻文字列（6桁）
     */
    public static String getTimeString() {
        SimpleDateFormat sdf = new SimpleDateFormat("HHmmss");
        java.util.Date d = new java.util.Date();
        return sdf.format(d);
    }

    /**
     * 日付時刻文字列を取得します。
     *
     * @param format フォーマット
     * @return 日付時刻文字列
     */
    public static String getDateTimeString(String format) {
        SimpleDateFormat sdf = new SimpleDateFormat(format);
        java.util.Date d = new java.util.Date();
        return sdf.format(d);
    }




    //----------------------------------------------------------------------
    //- 文字列変換メソッド
    //----------------------------------------------------------------------

    /**
     * 引数がnullの場合空文字を、その他の場合はオブジェクトを文字列化したものを返却します
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String emptyIfNull(Object str) {
        if (str == null) return "";
        return str.toString();
    }

    /**
     * HTMLエンコーディングを行います。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String htmlEncode(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if      (c == '<')  sb.append("&lt;");
            else if (c == '>')  sb.append("&gt;");
            else if (c == '"')  sb.append("&quot;");
            else if (c == '&')  sb.append("&amp;");
            else if (c == '\'') sb.append("&#39;");
            else                sb.append(c);
        }
        return sb.toString();
    }

    /**
     * 文字列記述用に「'」を「\'」、「"」を「\"」、「\」を「\\」に変換します。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String escape(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if      (c == '\'')  sb.append("\\\'");
            else if (c == '\"')  sb.append("\\\"");
            else if (c == '\\')  sb.append("\\\\");
            else                 sb.append(c);
        }
        return sb.toString();
    }

    /**
     * SQL用に文字列中の「'」を「''」に変換します。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String quote(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if      (c == '\'')                                        sb.append("''");
            else if (c == '\\' && DriverName.indexOf("sqlite") == -1)  sb.append("\\\\");
            else                                                       sb.append(c);
        }
        return sb.toString();
    }

    /**
     * 文字列中の「"」を「""」に変換します。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String dquote(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        while (true) {
            int index = str.indexOf(QUOTATION);
            if (index == -1) {
                sb.append(str);
                break;

            } else {
                sb.append(str.substring(0, index+1) + QUOTATION);
                str = str.substring(index+1);
            }
        }
        return sb.toString();
    }

    /**
     * 改行コード（LF）を<br>に変換します。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String LFtoBR(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if      (c == '\n')  sb.append("<br>");
            else if (c != '\r')  sb.append(c);
        }
        return sb.toString();
    }

    /**
     * 改行コード（CR）を<br>に変換します。
     *
     * @param str 変換前文字列
     * @return 変換後文字列
     */
    public static String CRtoBR(String str) {

        if (str == null) return null;
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            if      (c == '\r')  sb.append("<br>");
            else if (c != '\n')  sb.append(c);
        }
        return sb.toString();
    }



    //----------------------------------------------------------------------
    //- 文字列分割メソッド
    //----------------------------------------------------------------------

    /**
     * CSV形式の文字列を分割します。
     *
     * @param str CSV形式文字列
     * @return 文字列配列リスト
     */
    public static ArrayList<String[]> divideCSV(String str) {
        return divideDelimiter(str, CSV_DELIMITER_CHAR);
    }

    /**
     * TSV形式の文字列を分割します。
     *
     * @param str TSV形式文字列
     * @return 文字列配列リスト
     */
    public static ArrayList<String[]> divideTSV(String str) {
        return divideDelimiter(str, TSV_DELIMITER_CHAR);
    }

    /**
     * CSVまたはTSV形式の文字列を分割します。
     *
     * @param str TSV形式文字列
     * @param delimiter 区切り文字
     * @return 文字列配列リスト
     */
    public static ArrayList<String[]> divideDelimiter(String str, char delimiter) {

        // 返却用
        ArrayList<String[]> list = new ArrayList<String[]>();

        // 「\r」を抜いておく
        String tmp = str.replace("\r", "");

        // この時点で文字列が空の場合は終了
        if (tmp.length() == 0) return list;

        // 最後に改行文字を付けておく
        tmp += NL;

        int lastIndex = tmp.length() - 1;

        // 1行ぶんのリスト
        ArrayList<String> line = new ArrayList<String>();

        int pos = 0;
        while (true) {
            char c = tmp.charAt(pos);
            // 先頭が「"」の場合
            if (c == '"') {
                StringBuffer sb = new StringBuffer();
                int pos1 = pos+1;
                boolean nflag = false;
                while (true) {
                    if (pos1 == lastIndex) throw new IllegalArgumentException("「\"」で囲まれている文字列が「\"」で終わっていません。");
                    char c1 = tmp.charAt(pos1);
                    if (c1 != '"') {
                        sb.append(c1);
                        pos1++;
                    } else {
                        char c2 = tmp.charAt(pos1+1);
                        if (c2 == '"') {
                            sb.append('"');
                            pos1 += 2;
                        } else if (c2 == delimiter) {
                            line.add(sb.toString());
                            break;
                        } else if (c2 == '\n') {
                            line.add(sb.toString());
                            nflag = true;
                            break;
                        } else {
                            throw new IllegalArgumentException("「\"」で囲まれている文字列に不正な「\"」が含まれています。");
                        }
                    }
                }
                if (nflag) {
                    String[] values = new String[line.size()];
                    for (int i = 0; i < line.size(); i++) values[i] = line.get(i);
                    list.add(values);
                    if (pos1+1 == lastIndex) break;
                    line = new ArrayList<String>();
                }
                pos = pos1 + 2;
            }
            // 先頭が「"」でない場合
            else {
                int pos1 = tmp.indexOf(delimiter, pos);
                int pos2 = tmp.indexOf('\n',      pos);
                if (pos2 == -1 || (pos1 != -1 && pos2 != -1 && pos1 < pos2) ) {
                    String value = tmp.substring(pos, pos1);
                    line.add(value);
                    pos = pos1+1;
                } else {
                    String value = tmp.substring(pos, pos2);
                    line.add(value);
                    String[] values = new String[line.size()];
                    for (int i = 0; i < line.size(); i++) values[i] = line.get(i);
                    list.add(values);
                    if (pos2 == lastIndex) break;
                    pos = pos2+1;
                    line = new ArrayList<String>();
                }
            }
        }

        // リストの最後に空行が存在する場合は省く
        int count = list.size();
        for (int i = count-1; i >= 0; i--) {
            String[] strs = list.get(i);
            if (strs.length == 1 && strs[0].length() == 0) list.remove(i);
            else break;
        }

        return list;
    }

    /**
     * プロパティを取得します。
     *
     * @param src プロパティ形式文字列
     * @return プロパティ
     */
    public static Properties getProperties(String src) {

        Properties prop = new Properties();
        String[] line = src.split("\r|\n");
        for (int i = 0; i < line.length; i++) {
            String[] column = line[i].split("\t");
            if (column.length < 2) continue;
            prop.put(column[0], column[column.length-1]);
        }
        return prop;
    }



    //----------------------------------------------------------------------
    //- デバッグ用
    //----------------------------------------------------------------------

    /**
     * StackTraceの内容をStringに変換します。
     *
     * @param t Throwableインスタンス
     * @return Stringに変換されたStackTrace
     */
    public static String toString(Throwable t) {

        String ret = "";
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            PrintWriter writer = new PrintWriter(baos);
            t.printStackTrace(writer);
            writer.flush();
            byte[] buf = baos.toByteArray();
            ret = new String(buf);
            writer.close();
            baos.close();

        } catch (Exception e) {
        }
        return ret;
    }

    /**
     * コレクションの文字列表現を取得します。
     *
     * @param collection java.util.Collectionの実装クラス
     * @return コレクションの文字列表現
     */
    public static String toString(Collection<?> collection) {

        if (collection == null) return null;
        StringBuffer sb = new StringBuffer();
        sb.append("--- StringConvertor.toString(collection) ---" + NL);
        Iterator<?> ite = collection.iterator();
        while (ite.hasNext()) {
            Object value = ite.next();
            sb.append(value + NL);
        }
        return sb.toString();
    }

    /**
     * Mapの文字列表現を取得します。
     *
     * @param collection java.util.Mapの実装クラス
     * @return Mapの文字列表現
     */
    public static String toString(Map<?, ?> map) {

        if (map == null) return null;
        StringBuffer sb = new StringBuffer();
        sb.append("--- StringConvertor.toString(Map) ---" + NL);
        Iterator<?> ite = map.keySet().iterator();
        while (ite.hasNext()) {
            Object key = ite.next();
            Object value = map.get(key);
            sb.append(key + ":"+ value + NL);
        }
        return sb.toString();
    }

    /**
     * リストの文字列表現を取得します。
     *
     * @param list java.util.Listの実装クラス
     * @return リストの文字列表現
     */
    public static String toString(List<?> list) {

        if (list == null) return null;
        StringBuffer sb = new StringBuffer();
        sb.append("--- StringConvertor.toString(List) ---" + NL);
        for (int i = 0; i < list.size(); i++) {
            sb.append(list.get(i) + NL);
        }
        return sb.toString();
    }

} // end-class
