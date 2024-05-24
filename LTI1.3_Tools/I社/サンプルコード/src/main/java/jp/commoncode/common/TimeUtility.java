package jp.commoncode.common;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;



/**
 * Timestampを処理します。
 *
 * @version 2013/09/25
 */
public class TimeUtility {

    //------------------------------------------------------------------
    //- コンストラクタ
    //------------------------------------------------------------------

    /**
     * コンストラクタ
     */
    private TimeUtility() {
        // 外部からの呼び出し禁止
    }



    //----------------------------------------------------------------------
    //- public static メソッド
    //----------------------------------------------------------------------

    /**
     * Timestampを生成します。
     *
     * @return Timestampインスタンス
     */
    public static Timestamp createTimestamp() {
        return new Timestamp((new Date()).getTime());
    }

    /**
     * ミリ秒からTimestampを生成します。
     *
     * @param millis ミリ秒
     * @return Timestampインスタンス
     */
    public static Timestamp createTimestamp(long millis) {
        return new Timestamp(millis);
    }

    /**
     * 文字列を指定したフォーマットで解析しTimestampを生成します。<br/>
     * フォーマットの詳細はSimpleDateFormatの説明を参照してください。<br/>
     *
     * @param format 解析用フォーマット
     * @param src 解析対象文字列
     * @return 解析できた場合はTimestamp、できなかった場合はnullを返却します。
     */
    public static Timestamp parseTimestamp(String format, String src) {
        Timestamp result = null;
        try {
            if (src == null || src.equals("")) return null;
            SimpleDateFormat sdf = new SimpleDateFormat(format);
            sdf.setLenient(false);
            result = new Timestamp(sdf.parse(src).getTime());
        } catch (Exception e) {
            result = null;
        }
        return result;
    }

    /**
     * Timestampに加減算を行います。<br/>
     * fieldはCalendarクラスで定義されている、年月日時分秒を表す値です。<br/>
     *
     * @param timestamp 対象のTimestamp
     * @param field 対象フィールド
     * @param amount 加減算値
     * @return 加減算後のTimestamp
     */
    public static Timestamp add(Timestamp timestamp, int field, int amount) {
        Calendar cal = Calendar.getInstance();
        cal.setTimeInMillis(timestamp.getTime());
        cal.add(field, amount);
        return createTimestamp(cal.getTimeInMillis());
    }

    /**
     * Timestampを指定したフォーマットで変換し日付文字列を生成します。
     * フォーマットの詳細はSimpleDateFormatの説明を参照してください。
     *
     * @param timestamp 変換元Timestampインスタンス
     * @param format 変換用フォーマット
     * @return 変換に成功した場合は日付文字列。できなかった場合はnullを返す。
     */
    public static String form(Timestamp timestamp, String format) {
        if (timestamp == null) return null;
        String result = null;
        try {
            SimpleDateFormat sdf = new SimpleDateFormat(format);
            result = sdf.format(timestamp);
        } catch (Exception e) {
            result = null;
        }
        return result;
    }

    /**
     * 指定フォーマットで現在日時文字列を生成します。
     *
     * @param format 変換用フォーマット
     * @return 変換に成功した場合は現在日時文字列。できなかった場合はnullを返す。
     */
    public static String createTimestampString(String format) {
        return form(createTimestamp(), format);
    }

    /**
     * ミリ秒から指定フォーマットで日時文字列を生成します。
     *
     * @param millis ミリ秒
     * @param format 変換用フォーマット
     * @return 変換に成功した場合は日時文字列。できなかった場合はnullを返す。
     */
    public static String createTimestampString(long millis, String format) {
        return form(new Timestamp(millis), format);
    }

    /**
     * 解析用フォーマットの日時文字列に加減算を行います。<br/>
     * fieldはCalendarクラスで定義されている、年月日時分秒を表す値です。<br/>
     *
     * @param format 解析用フォーマット
     * @param src 日時文字列
     * @param field 対象フィールド
     * @param amount 加減算値
     * @return 日時として解析できた場合は加減算後の解析用フォーマットの日時文字列、できなかった場合はnullを返却します。
     */
    public static String add(String format, String src, int field, int amount) {
        Timestamp ts = parseTimestamp(format, src);
        if (ts == null) return null;

        Calendar cal = Calendar.getInstance();
        cal.setTimeInMillis(ts.getTime());
        cal.add(field, amount);
        return form(createTimestamp(cal.getTimeInMillis()), format);
    }

} // end-class
