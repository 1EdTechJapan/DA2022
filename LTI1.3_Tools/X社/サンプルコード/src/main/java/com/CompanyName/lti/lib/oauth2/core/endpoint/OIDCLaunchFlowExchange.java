/*
 * Copyright 2002-2017 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.CompanyName.lti.lib.oauth2.core.endpoint;

import org.springframework.security.oauth2.core.endpoint.OAuth2AuthorizationRequest;
import org.springframework.security.oauth2.core.endpoint.OAuth2AuthorizationResponse;
import org.springframework.util.Assert;

/**
 * An &quot;exchange&quot; of an OAuth 2.0 Authorization Request and Response
 * for the authorization code grant type.
 *
 * @author Joe Grandja
 * @since 5.0
 * @see OAuth2AuthorizationRequest
 * @see OAuth2AuthorizationResponse
 */
public final class OIDCLaunchFlowExchange {
	// This should be our own class in the future
	private final OAuth2AuthorizationRequest authorizationRequest;
	private final OIDCLaunchFlowResponse authorizationResponse;

	/**
	 * Constructs a new {@code OAuth2AuthorizationExchange} with the provided
	 * Authorization Request and Authorization Response.
	 *
	 * @param authorizationRequest the {@link OAuth2AuthorizationRequest Authorization Request}
	 * @param authorizationResponse the {@link OAuth2AuthorizationResponse Authorization Response}
	 */
	public OIDCLaunchFlowExchange(OAuth2AuthorizationRequest authorizationRequest,
								  OIDCLaunchFlowResponse authorizationResponse) {
		Assert.notNull(authorizationRequest, "authorizationRequest cannot be null");
		Assert.notNull(authorizationResponse, "authorizationResponse cannot be null");
		this.authorizationRequest = authorizationRequest;
		this.authorizationResponse = authorizationResponse;
	}

	/**
	 * Returns the {@link OAuth2AuthorizationRequest Authorization Request}.
	 *
	 * @return the {@link OAuth2AuthorizationRequest}
	 */
	public OAuth2AuthorizationRequest getAuthorizationRequest() {
		return this.authorizationRequest;
	}

	/**
	 * Returns the {@link OIDCLaunchFlowResponse Authorization Response}.
	 *
	 * @return the {@link OIDCLaunchFlowResponse}
	 */
	public OIDCLaunchFlowResponse getAuthorizationResponse() {
		return this.authorizationResponse;
	}
}
