<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Start.aspx.cs" Inherits="OneRosterCSV.Start" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title></title>
</head>
<body>
    <form id="formMain" runat="server">
        <div style="padding-top:10px; padding-left:10px;">
            <div style="padding-top:30px; padding-bottom:10px;">
                準拠仕様
            </div>
            <div style="padding-bottom:10px;">
                ・OneRosterCSV項目定義書_JapanProfile_v.1.2版（rev2）_20221207
            </div>
            <div style="padding-top:30px; padding-bottom:10px;">
                校務システムのデータをOneRoster用に変換
            </div>
            <div style="padding-bottom:10px;">
                <asp:Button ID="ButtonKoumuToOneRoster" runat="server" Text="校務システムのデータをmongodbへ" OnClick="ButtonKoumuToOneRoster_Click" />
            </div>
            <div style="padding-bottom:10px;">
                OneRosterCSVをダウンロード
            </div>
            <div style="padding-bottom:10px;">
                <asp:Button ID="ButtonOneRosterCSVDownload" runat="server" Text="OneRosterCSVをダウンロードする" OnClick="ButtonOneRosterCSVDownload_Click" />
            </div>
        </div>
    </form>
</body>
</html>
