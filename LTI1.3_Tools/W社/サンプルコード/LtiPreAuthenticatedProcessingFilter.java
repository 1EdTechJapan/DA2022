import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.preauth.AbstractPreAuthenticatedProcessingFilter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
// 独自処理のimport割愛
import lombok.extern.slf4j.Slf4j;

/**
 * *****************************************************************************
 * LTIリソース起動フィルタクラス
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * (無し)
 * </pre>
 *****************************************************************************
 */

@Slf4j
public class LtiPreAuthenticatedProcessingFilter extends AbstractPreAuthenticatedProcessingFilter {

  /**
   * ***************************************************************************
   * doFilter
   * <pre>
   * [機能説明]
   * 1.
   * [注意事項]
   * 認証処理が正常終了後、stateとnonceを保持しているcookieを削除する
   * </pre>
   ***************************************************************************
   */
  @Override
  public  void doFilter(ServletRequest request, ServletResponse response,
      FilterChain chain) throws IOException, ServletException {

    if (((HttpServletRequest)request).getServletPath().equals("/lti/launches")
        && !response.isCommitted()) {

        super.doFilter(request, response, chain);

      // 認証が成功した場合、stateとnonceを保持しているcookieを削除する
      Cookie ltiStateCookieUsed = CookieUtility.getCookie(LtiStringConstants.LTI_STATE_COOKIE, (HttpServletRequest)request);
      if (ltiStateCookieUsed != null) {
        CookieUtility.deleteCookie((HttpServletResponse)response, ltiStateCookieUsed);
      }
      Cookie ltiNonceCookieUsed = CookieUtility.getCookie(LtiStringConstants.LTI_NONCE_COOKIE, (HttpServletRequest)request);
      if (ltiNonceCookieUsed != null) {
        CookieUtility.deleteCookie((HttpServletResponse)response, ltiNonceCookieUsed);
      }

    }

      chain.doFilter(request, response);

  }

  /**
   * ***************************************************************************
   * getPreAuthenticatedPrincipal
   * <pre>
   * [機能説明]
   * 1.リクエストからstateを取得し、入力チェックを行う。
   * 2.リクエストからid_tokenを取得し、プラットフォームのキーセットから復号を行う
   * 3.id_tokenから取得したclaimの入力チェックを行う
   * 4.認証に必要な情報を返却する
   * [注意事項]
   * (なし)
   * @param request リクエスト
   * @return ltiPlatformKey、ltiUserIdのMap
   * </pre>
   ***************************************************************************
   */
  @Override
  protected Object getPreAuthenticatedPrincipal(HttpServletRequest request) {

    try {

      // stateクエリがあることを確認する。
      String state = request.getParameter(LtiStringConstants.STATE);
      if (StringUtility.isBlankOrNull(state)) {
        throw new IllegalStateException("LTI request doesn't contains state");
      }
      // cookieからstateを取得
      String cookieState = CookieUtility.getCookieValue(request, LtiStringConstants.LTI_STATE_COOKIE);
      log.info("cookieState：" + cookieState);
      if (!StringUtility.isEqual(cookieState, state)) {
        throw new IllegalStateException("LTI request doesn't contains the expected state");
      }

      // stateのバリデーションチェック
      Jws<Claims> stateClaims = LtiUtility.validateState(state);

      String ltiPlatformId = stateClaims.getBody().getSubject();
      String ltiDeploymentId = (String) stateClaims.getBody().get(LtiStringConstants.LTI_DEPLOYMENT_ID);
      String ltiClientId = stateClaims.getBody().getAudience();
      log.info("ltiPlatformId：" + ltiPlatformId + ", ltiDeploymentId：" + ltiDeploymentId + ", ltiClientId：" + ltiClientId);

      // 独自処理
      // APIを介して、DBからリクエストに紐づくプラットフォームの情報を取得する
      // 取得結果をMappingManageLtiPlatformApiRes resEntityに格納する
      if (resEntity == null) {
        throw new IllegalStateException("LTI Platform dosen't found");
      }

      String sub = null;

      // id_tokenの取得
      String jwt = request.getParameter(LtiStringConstants.ID_TOKEN);
      if (!StringUtility.isBlankOrNull(jwt)) {
        // id_token のjwt形式バリデーションチェック
        Jws<Claims> jws = LtiUtility.validateJWT(jwt, resEntity.getLtiJwksEndPoint());
        if (jws != null) {
          // id_tokenの内容をdtoに格納
          LTI3RequestDto lti3Request = new LTI3RequestDto(jws);
          // id_tokenのclaimのバリデーションチェック
          LtiUtility.varidateRequest(lti3Request, request, resEntity);
          sub = lti3Request.getSub();
        } else {
          throw new IllegalStateException("id_token dosen't expected");
        }
      } else {
        throw new IllegalStateException("id_token is null");
      }

      Map<String, Object> principal = new HashMap<>();
      principal.put("ltiPlatformKey",resEntity.getltiPlatformKey());
      principal.put("ltiUserId",sub);

      return principal;

    } catch (Exception e) {
//      エラー時にはprincipalをnullとして返却する
      log.error("LtiPreAuthenticatedProcessingFilter error");
      return null;
    }
  }

  /**
   * ***************************************************************************
   * getPreAuthenticatedCredentials
   * <pre>
   * [機能説明]
   * 1.
   * [注意事項]
   * 認証ではCredentialは用いないため、空文字を返却
   * @param request リクエスト
   * @return 空文字
   * </pre>
   ***************************************************************************
   */
  @Override
  protected Object getPreAuthenticatedCredentials(HttpServletRequest request) {
      return "";
  }

}
