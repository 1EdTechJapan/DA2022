<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Start.aspx.cs" Inherits="OneRosterCSV.Start" %>

<!DOCTYPE html>

<%@ Register Tagprefix="SharePoint" Namespace="Microsoft.SharePoint.WebControls" Assembly="Microsoft.SharePoint, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" %>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:mso="urn:schemas-microsoft-com:office:office" xmlns:msdt="uuid:C2F41010-65B3-11d1-A29F-00AA00C14882">
<%@ Register Tagprefix="SharePoint" Namespace="Microsoft.SharePoint.WebControls" Assembly="Microsoft.SharePoint, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" %>
<head runat="server">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title></title>

<!--[if gte mso 9]><SharePoint:CTFieldRefs runat=server Prefix="mso:" FieldList="FileLeafRef,MediaLengthInSeconds"><xml>
<mso:CustomDocumentProperties>
<mso:display_urn_x003a_schemas-microsoft-com_x003a_office_x003a_office_x0023_Editor msdt:dt="string">西原 達平(NISHIHARA Tappei)</mso:display_urn_x003a_schemas-microsoft-com_x003a_office_x003a_office_x0023_Editor>
<mso:Order msdt:dt="string">549400.000000000</mso:Order>
<mso:_ExtendedDescription msdt:dt="string"></mso:_ExtendedDescription>
<mso:SharedWithUsers msdt:dt="string"></mso:SharedWithUsers>
<mso:display_urn_x003a_schemas-microsoft-com_x003a_office_x003a_office_x0023_Author msdt:dt="string">西原 達平(NISHIHARA Tappei)</mso:display_urn_x003a_schemas-microsoft-com_x003a_office_x003a_office_x0023_Author>
<mso:ComplianceAssetId msdt:dt="string"></mso:ComplianceAssetId>
<mso:ContentTypeId msdt:dt="string">0x010100A4E0542992183D489D153D529261FBD2</mso:ContentTypeId>
<mso:TriggerFlowInfo msdt:dt="string"></mso:TriggerFlowInfo>
<mso:_SourceUrl msdt:dt="string"></mso:_SourceUrl>
<mso:_SharedFileIndex msdt:dt="string"></mso:_SharedFileIndex>
<mso:MediaLengthInSeconds msdt:dt="string"></mso:MediaLengthInSeconds>
</mso:CustomDocumentProperties>
</xml></SharePoint:CTFieldRefs><![endif]-->
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
