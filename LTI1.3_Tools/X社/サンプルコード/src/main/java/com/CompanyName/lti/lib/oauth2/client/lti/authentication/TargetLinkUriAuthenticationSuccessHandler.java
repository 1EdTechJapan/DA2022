package com.CompanyName.lti.lib.oauth2.client.lti.authentication;

import com.CompanyName.lti.lib.lti.Claims;
import com.CompanyName.lti.lib.oauth2.client.lti.web.OptimisticAuthorizationRequestRepository;
import com.CompanyName.lti.lib.oauth2.client.lti.web.StateCheckingAuthenticationSuccessHandler;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * This looks for the target URI in the final request (as it's signed by the platform).
 */
public class TargetLinkUriAuthenticationSuccessHandler extends StateCheckingAuthenticationSuccessHandler {

    /**
     * @param authorizationRequestRepository The authentication repository.
     */
    public TargetLinkUriAuthenticationSuccessHandler(OptimisticAuthorizationRequestRepository authorizationRequestRepository) {
        super(authorizationRequestRepository);
    }

    @Override
    protected String determineTargetUrl(HttpServletRequest request,
                                        HttpServletResponse response, Authentication authentication) {
        if (authentication instanceof OAuth2AuthenticationToken) {
            OAuth2AuthenticationToken token = (OAuth2AuthenticationToken) authentication;
            // https://www.imsglobal.org/spec/lti/v1p3/#target-link-uri says we should only trust this and not
            // the parameter passed in on the initial login initiation request.
            String targetLink = token.getPrincipal().getAttribute(Claims.TARGET_LINK_URI);
            if (targetLink != null && !targetLink.isEmpty()) {
                return targetLink;
            }
        }
        return super.determineTargetUrl(request, response, authentication);
    }
}
