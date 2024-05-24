/**
 * OIDC認証
 *
 */
@Service
public class StudyToolAccessService {

    @Autowired
    HttpSession session;

    /** userDetails targetUrl type sarthTestId
     * 学習ツールコンテンツ画像押下時
     * @param userDetails
     * @param model
     * @return
     */
    public void handleRequestStudyTool(HttpServletResponse response, StudyToolAccessRequest requestBody,
            PortalUserDetails userDetails) throws Exception{

        HashMap<String, String> parameter = getParameter(requestBody.getTargetLinkUri());

        response.setContentType("text/html; charset=UTF-8");

        PrintWriter out = response.getWriter();
        StringBuffer studyToolViewData = new StringBuffer();

        //studyToolUri 学習ツール初期接続用URL
        String studyToolUri = parameter.get("lti-connect-url");

        //iss IDPのentityID
        String iss = (String) session.getAttribute("IdpIssuer");

        //loginHint ログイン者のUUID
        String loginHint = userDetails.getuuID();

        //requestBody 学習ツールにアクセスするためのUri
        String targetLinkUri = parameter.get("contentPath");
        //clientId　
        String clientId = parameter.get("lti-clientid");

        //ltiDeploymentId 現在未使用
        String ltiDeploymentId = parameter.get("lti-dep-id");

        //ltiMessageHint リクエストパラメーター
        String ltiMessageHint = parameter.get("lti-type");

        //連携用HTML格納用
        XXXXXResponse studyTool_res = new XXXXXResponse();

        // OIDC認証
        if(XXXXXLoginRequest.isXXXXXLoginRequest(studyToolUri,//学習ツール初期接続用URL
                iss,                                            //iss IDPのentityID
                loginHint,                                      //loginHint ログイン者のUUID
                targetLinkUri,                                  //requestBody 学習ツールにアクセスするためのUri
                clientId,                                       //clientId　
                ltiDeploymentId,                                //ltiDeploymentId 現在未使用
                ltiMessageHint,                                 //ltiMessageHint リクエストパラメーター
                studyTool_res)) {                               //連携用HTML格納用

            //成功時生成されたHTMLを格納
            studyToolViewData.append(studyTool_res.redirectHtml);

        } else {

            //エラー発生時エラー画面にリダイレクトするHTMLを生成し格納
            studyToolViewData.append(getErrorRedirect());

        }

        out.println(studyToolViewData);

    }

    /**
     * エラー画面リダイレクトHTML作成関数
     * @return
     */
    public String getErrorRedirect() {

      //エラー画面リダイレクト用HTML作成
        String viewHTML = "<!DOCTYPE html>"
                        + "<html lang=\"ja\">"
                        + "  <HEAD>"
                        + "    <script type=\"text/javascript\">"
                        + "       function getRootPath(){"
                        + "          var curWwwPath=window.document.location.href;"
                        + "          var pathName=window.document.location.pathname;"
                        + "          var pos=curWwwPath.indexOf(pathName);"
                        + "          var localhostPaht=curWwwPath.substring(0,pos);"
                        + "          var projectName=pathName.substring(0,pathName.substr(1).indexOf('/')+1);"
                        + "          return(localhostPaht+projectName);"
                        + "       }"
                        + "       async function HttpRequest(){"
                        + "          document.location.href = getRootPath() + \"/error/error\"; "
                        + "       }"
                        + "    </script>"
                        + "    <TITLE>"
                        + "      Redirecting"
                        + "     </TITLE>"
                        + "  </HEAD>"
                        + "  <BODY onload=\"onload=HttpRequest();\">"
                        + "  </BODY>"
                        + "</HTML>";

        return viewHTML;

    }

}