package jp.co.example.osarai2.controller.digital;

import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.auth0.jwt.interfaces.DecodedJWT;

import jp.co.example.osarai2.config.ApplicationConfig;
import jp.co.example.osarai2.data.lti.InitiationRequestData;
import jp.co.example.osarai2.service.lti.InitiationService;
import jp.co.example.osarai2.service.lti.LaunchService;
import jp.co.example.osarai2.service.lti.SessionService;
import jp.commoncode.common.StringUtility;

/**
 * LTI起動コントローラー
 */
@Controller
@RequestMapping("/osarai/lti")
public class LtiController {

    @Autowired
    private InitiationService initiationService;

    @Autowired
    private LaunchService launchService;

    @Autowired
    private SessionService sessionService;

    @Autowired
    private ApplicationConfig config;

    @Autowired
    private HttpSession session;

    /**
     * ログイン初期処理を行います
     *
     * @param requestBody
     * @param redirectAttributes
     * @return OICD認証エンドポイントリダイレクト
     */
    @PostMapping("/initiation")
    public String initiation(
        @Validated InitiationRequestData data,
        HttpServletRequest request,
        RedirectAttributes redirectAttributes,
        HttpServletResponse response
    ) {
        Map<String, String> responseMap = initiationService.createResponse(data);
        sessionService.createSession(request, response, session, responseMap);
        redirectAttributes.addAllAttributes(responseMap);
        return "redirect:" + config.getLtiOidcAuthUrl();
    }

    /**
     * 起動処理を行います
     *
     * @param token
     * @param request
     * @param model
     * @return 学習側ログインテンプレート
     */
    @PostMapping("/launch")
    public String launches(
        @RequestParam("state") String state,
        @RequestParam("id_token") String token,
        HttpServletRequest request,
        Model model
    ) {
        // token検証
        DecodedJWT jwt = launchService.verifyToken(request, session, token);

        // セッション情報検証
        sessionService.verifySession(request, session, state, jwt);

        // ユーザー情報取得
        // User user = launchService.loginUser(jwt);
        launchService.loginUser(jwt);

        // 学習者が存在する場合はtoken発行（学習者PKがない場合はtokenなし＝体験ユーザーとする）
        // ログイン情報返却
        // 自社独自領域のため詳細は割愛

        return "lti/login";
    }

    /**
     * Exception発生時の処理を行います
     *
     * @param e
     * @param model
     * @return エラー画面
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleException(Exception e, Model model) {
        model.addAttribute("errorMessage", formatErrorMessage(e));
        return "lti/error";
    }

    /**
     * RuntimeException発生時の処理を行います
     *
     * @param e
     * @param model
     * @return エラー画面
     */
    @ExceptionHandler(RuntimeException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleRuntimeException(RuntimeException e, Model model) {
        model.addAttribute("errorMessage", formatErrorMessage(e));
        return "lti/error";
    }

    /**
     * 例外メッセージを整形します。
     *
     * @param e
     * @return 整形例外メッセージ
     */
    private String formatErrorMessage(Exception e) {
        String message = StringUtility.toString(e);
        return message.replaceAll(";", StringUtility.NL);
    }



}
