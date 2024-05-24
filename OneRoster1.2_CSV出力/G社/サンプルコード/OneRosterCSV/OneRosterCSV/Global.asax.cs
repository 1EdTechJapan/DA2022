using System;
using System.Collections.Generic;
using System.Configuration;
using System.Drawing;
using System.Linq;
using System.Web;
using System.Web.Security;
using System.Web.SessionState;

namespace OneRosterCSV
{
    public class Global : System.Web.HttpApplication
    {
        // データベース接続文字
        public static readonly string mongodbConnection = "mongodb://localhost:27017";
        public static readonly string mongodbHost = "localhost:27017";
        public static readonly string mongodbDatabase = "oneroster";

        // mongoexportパス
        public static readonly string mongoexport = "D:\\mongodb-database-tools-windows-x86_64-100.6.1\\bin\\mongoexport.exe";

        // OneRosterCSV出力パス
        public static readonly string csvPath = @"D:\\oneroster\\csv\\";

        /// <summary>
        /// 全角カナに変換
        /// </summary>
        /// <param name="text"></param>
        /// <returns></returns>
        public static string CnvKana(string text)
        {
            return Microsoft.VisualBasic.Strings.StrConv(
                text, Microsoft.VisualBasic.VbStrConv.Katakana | Microsoft.VisualBasic.VbStrConv.Wide, 0x411);
        }

        /// <summary>
        /// 年度を取得
        /// </summary>
        /// <param name="date"></param>
        /// <returns></returns>
        public static int GetNendo(DateTime date)
        {
            return date.AddMonths(-3).Year;
        }

        /// <summary>
        /// Iso8601UTC形式の日時
        /// </summary>
        /// <returns></returns>
        public static string GetIso8601UTC()
        {
            return DateTime.UtcNow.ToString("yyyy'-'MM'-'dd HH':'mm':'ss'.'fff'Z'");
        }

        /// <summary>
        /// Iso8601UTC形式の日時
        /// </summary>
        /// <returns></returns>
        public static string GetIso8601Date(string value)
        {
            DateTime date;

            try
            {
                date = DateTime.ParseExact(value, "yyyy/MM/dd", null);
            }
            catch (Exception)
            {
                return "";
            }

            return date.ToString("yyyy'-'MM'-'dd");
        }

        /// <summary>
        /// 校務システムの性別をOneRosterの性別に変換
        /// </summary>
        /// <returns></returns>
        public static string GetOneRosterSex(string value)
        {
            string oneRosterSex;

            switch (value)
            {
                case "男":
                    oneRosterSex = "male";
                    break;
                case "女":
                    oneRosterSex = "female";
                    break;
                default:
                    oneRosterSex = "unspecified";
                    break;
            }

            return oneRosterSex;
        }

        protected void Application_Start(object sender, EventArgs e)
        {
        }
    }
}