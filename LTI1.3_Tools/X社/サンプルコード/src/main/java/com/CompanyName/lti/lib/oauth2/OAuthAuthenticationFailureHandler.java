package com.CompanyName.lti.lib.oauth2;

import org.springframework.http.HttpStatus;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationFailureHandler;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class OAuthAuthenticationFailureHandler extends SimpleUrlAuthenticationFailureHandler {

	public void onAuthenticationFailure(HttpServletRequest request,
										HttpServletResponse response, AuthenticationException exception)
			throws IOException, ServletException {
		if (exception instanceof OAuth2AuthenticationException) {
			response.sendError(HttpStatus.UNAUTHORIZED.value(), ((OAuth2AuthenticationException)exception).getError().getErrorCode()+ " : "+ exception.getMessage());
		} else {
			super.onAuthenticationFailure(request, response, exception);
		}
	}
}
