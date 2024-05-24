package jp.co.example.osarai2.service.lti;

import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;

import com.auth0.jwt.interfaces.DecodedJWT;

import jp.co.example.osarai2.definition.lti_request;

/**
 * LTIセッション管理Service
 */
@Service
public class SessionService {

    /**
     * OICD認証エンドポイントリダイレクト用のセッション情報を作成します
     *
     * @param request
     * @param response
     * @param session
     * @param map
     */
    public void createSession(HttpServletRequest request, HttpServletResponse response, HttpSession session, Map<String, String> map) {
        session = request.getSession(true);
        session.setAttribute(lti_request.KEY_LINK_STATE, map.get(lti_request.KEY_LINK_STATE));
        session.setAttribute(lti_request.KEY_LINK_NONCE, map.get(lti_request.KEY_LINK_NONCE));
        // SameSite=Noneでないとセッションが取れないためCookieを再設定
        response.reset();
        response.setHeader(HttpHeaders.SET_COOKIE, "JSESSIONID=" + session.getId() + "; SameSite=None; Secure");
    }

    /**
     * OICD認証エンドポイントリダイレクト時に設定したセッション情報を検証します
     *
     * @param request
     * @param session
     * @param data
     */
    public void verifySession(HttpServletRequest request, HttpSession session, String state, DecodedJWT jwt) {
        session = request.getSession(false);
        String sessionState = session.getAttribute(lti_request.KEY_LINK_STATE).toString();
        String sessionNonce = session.getAttribute(lti_request.KEY_LINK_NONCE).toString();
        String nonce = jwt.getClaim(lti_request.KEY_LINK_NONCE).asString();
        if (!sessionState.equals(state)) {
            throw new RuntimeException("Invalid session state");
        }
        if (nonce != null && !sessionNonce.equals(nonce)) {
            throw new RuntimeException("Invalid session nonce");
        }
    }




}
