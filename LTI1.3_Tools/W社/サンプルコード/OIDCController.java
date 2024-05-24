import java.io.IOException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.tomcat.util.http.SameSiteCookies;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

// 独自処理のimport割愛
import lombok.extern.slf4j.Slf4j;

/**
 * *****************************************************************************
 * OIDCログイン開始Controller
 * <pre>
 * [機能説明]
 * 1.OIDCから呼び出され、プラットフォームに求められる認証情報を返却する。
 * [注意事項]
 * (なし)
 * </pre>
 *****************************************************************************
 */

@Controller
@Slf4j
public class OIDCController {

  /** OIDCログイン開始Service */
  @Autowired
  private OIDCService service;

  /**
   * Cookie生成時のレスポンスヘッダ名称
   */
  private static final String SET_COOKIE = "Set-Cookie";

  //  OIDCではgetとpostの両方をサポートする必要があるため、明示
  @RequestMapping(path = "/lti/login_initiations", method = { RequestMethod.GET, RequestMethod.POST })
  public String loginInitiations(HttpServletRequest req,HttpServletResponse res, Model model) throws IOException {

    try {

      //    OIDCリクエスト作成
      OIDCLoginInitiationDto oidcLoginInitiationDto = new OIDCLoginInitiationDto(req);

      // 入力チェック
      // iss, login_hint, target_link_urlが設定されていない場合、エラー
      if (StringUtility.isBlankOrNull(oidcLoginInitiationDto.getIss())
          || StringUtility.isBlankOrNull(oidcLoginInitiationDto.getLoginHint())
          || StringUtility.isBlankOrNull(oidcLoginInitiationDto.getTargetLinkUri())) {
        throw new ApplicationException("required parameters is null：iss, login_hint, target_link_url");
      }

      Map<String, String> parameters = service.initiation(oidcLoginInitiationDto);

      // stateをcookieにセット
      ResponseCookie stateCookie = ResponseCookie.from(LtiStringConstants.LTI_STATE_COOKIE, parameters.get(LtiStringConstants.STATE))
                .maxAge(60 * 100)
                .httpOnly(true)
                .secure(true)
                .sameSite(SameSiteCookies.NONE.getValue())
                .build();
      res.addHeader(SET_COOKIE, stateCookie.toString());

      // nonceをcookieにセット
      ResponseCookie nonceCookie = ResponseCookie.from(LtiStringConstants.LTI_NONCE_COOKIE, parameters.get(LtiStringConstants.NONCE))
                .maxAge(60 * 100)
                .httpOnly(true)
                .secure(true)
                .sameSite(SameSiteCookies.NONE.getValue())
                .build();
      res.addHeader(SET_COOKIE, nonceCookie.toString());

      return "redirect:" + parameters.get(LtiStringConstants.OIDC_END_POINT_COMPLETE);

    } catch (Exception e) {
      log.error("OIDCController error");
      throw new ApplicationException();
    }

  }

}
