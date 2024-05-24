/*
 * Copyright 2002-2018 the original author or authors.
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

package com.group.lti.lib.oauth2.client.lti.authentication;

import com.group.lti.lib.lti.Role;
import com.nimbusds.jose.shaded.json.JSONObject;
import com.nimbusds.jose.shaded.json.JSONValue;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.core.oidc.OidcIdToken;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.net.URL;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.group.lti.lib.lti.Claims.*;

/**
 * This needs to be update for the launch flow for IMS Sec 1.0
 * We should refactor this so that it implements org.springframework.security.oauth2.core.OAuth2TokenValidator
 *
 * @author Rob Winch
 * @see OAuth2TokenValidator
 * @since 5.1
 */

@Component
public class OidcTokenValidator {
    public static final String INVALID_ID_TOKEN_ERROR_CODE = "invalid_id_token";

    private static final Set<String> INVALID_GRADES = new HashSet<>(Arrays.asList("P1", "P2", "P3", "P4", "P5", "P6", "J1", "J2", "J3"));
    private static final String UUIDV4_REGEX = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$";

    @Value("${spring.security.oauth2.client.provider.ims-ri.deployment-id}")
    private String deploymentId;

    void validateIdToken(OidcIdToken idToken, ClientRegistration clientRegistration) {
        // 3.1.3.7  ID Token Validation
        // https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation

        // Validate REQUIRED Claims
        URL issuer = idToken.getIssuer();
        if (issuer == null || issuer.toString().isEmpty()) {
            throwInvalidIdTokenException("No issuer in token.");
        }
        String subject = idToken.getSubject();
        if (subject != null && !subject.isEmpty() && !subject.matches(UUIDV4_REGEX)) {
            throwInvalidIdTokenException("Subject invalid in token.");
        }
        List<String> audience = idToken.getAudience();
        if (CollectionUtils.isEmpty(audience)) {
            throwInvalidIdTokenException("No audience in token.");
        }
        Instant expiresAt = idToken.getExpiresAt();
        if (expiresAt == null) {
            throwInvalidIdTokenException("No expiry timestamp in token.");
        }
        Instant issuedAt = idToken.getIssuedAt();
        if (issuedAt == null) {
            throwInvalidIdTokenException("No issue timestamp in token.");
        }

        // 2. The Issuer Identifier for the OpenID Provider (which is typically obtained during Discovery)
        // MUST exactly match the value of the iss (issuer) Claim.
        // TODO Depends on gh-4413

        // 3. The Client MUST validate that the aud (audience) Claim contains its client_id value
        // registered at the Issuer identified by the iss (issuer) Claim as an audience.
        // The aud (audience) Claim MAY contain an array with more than one element.
        // The ID Token MUST be rejected if the ID Token does not list the Client as a valid audience,
        // or if it contains additional audiences not trusted by the Client.
        if (!audience.contains(clientRegistration.getClientId())) {
            throwInvalidIdTokenException("Client ID not found for audience in token.");
        }

        // 4. If the ID Token contains multiple audiences,
        // the Client SHOULD verify that an azp Claim is present.
        String authorizedParty = idToken.getAuthorizedParty();
        if (audience.size() > 1 && authorizedParty == null) {
            throwInvalidIdTokenException("Multiple audiences and no authorized party in token.");
        }

        // 5. If an azp (authorized party) Claim is present,
        // the Client SHOULD verify that its client_id is the Claim Value.
        if (authorizedParty != null && !authorizedParty.equals(clientRegistration.getClientId())) {
            throwInvalidIdTokenException("Authorized party doesn't match client ID in token.");
        }

        // 7. The alg value SHOULD be the default of RS256 or the algorithm sent by the Client
        // in the id_token_signed_response_alg parameter during Registration.
        // TODO Depends on gh-4413

        // 9. The current time MUST be before the time represented by the exp Claim.
        Instant now = Instant.now();
        if (!now.isBefore(expiresAt)) {
            throwInvalidIdTokenException("Token expiry timestamp is in the future.");
        }

        // 10. The iat Claim can be used to reject tokens that were issued too far away from the current time,
        // limiting the amount of time that nonces need to be stored to prevent attacks.
        // The acceptable range is Client specific.
        Instant maxIssuedAt = now.plusSeconds(30);
        if (issuedAt.isAfter(maxIssuedAt)) {
            throwInvalidIdTokenException();
        }

        // 11. If a nonce value was sent in the Authentication Request,
        // a nonce Claim MUST be present and its value checked to verify
        // that it is the same value as the one that was sent in the Authentication Request.
        // The Client SHOULD check the nonce value for replay attacks.
        // The precise method for detecting replay attacks is Client specific.
        // TODO Depends on gh-4442
        // TODO Must validate this although the state is like a nonce.

        // These are the LTI Claims that we check https://www.imsglobal.org/spec/lti/v1p3/#required-message-claims

        String ltiVersion = idToken.getClaimAsString(LTI_VERSION);
        if (!"1.3.0".equals(ltiVersion)) {
            throwInvalidIdTokenException("Must be LTI 1.3.0 version claim in token.");
        }

        String messageType = idToken.getClaimAsString(MESSAGE_TYPE);
        if (messageType == null || messageType.isEmpty()) {
            throwInvalidIdTokenException("Message type claim missing from token.");
        } else if (!"LtiResourceLinkRequest".equals(messageType)) {
            throwInvalidIdTokenException("Message type claim invalid from token.");
        }

        List<String> roles = idToken.getClaimAsStringList(ROLES);
        if (roles == null || roles.isEmpty()) {
            throwInvalidIdTokenException("Roles claim missing from token.");
        } else {
            roles.forEach(role -> {
                if (!Role.acceptedRole(role)) {
                    throwInvalidIdTokenException("Roles claim invalid from token.");
                }
            });
        }

        String deploymentIdInToken = idToken.getClaimAsString(LTI_DEPLOYMENT_ID);
        if (deploymentIdInToken == null || deploymentIdInToken.isEmpty()) {
            throwInvalidIdTokenException("Deployment ID claim missing from token.");
        } else {
            if (!deploymentId.equals(deploymentIdInToken)) {
                throwInvalidIdTokenException("Deployment ID claim invalid from token.");
            }
        }

        String toolPlatform = idToken.getClaimAsString(PLATFORM_INSTANCE);
        if (toolPlatform == null || toolPlatform.isEmpty()) {
            throwInvalidIdTokenException("Tool Platform claim missing from token.");
        } else {
            JSONObject object = (JSONObject) JSONValue.parse(toolPlatform);
            String guid = object.getAsString("guid");

            if (guid == null || guid.isEmpty()) {
                throwInvalidIdTokenException("Tool Platform GUID claim missing from token.");
            } else if (!guid.matches(UUIDV4_REGEX)) {
                throwInvalidIdTokenException("Tool Platform GUID claim invalid from token.");
            }

        }

        String resourceLink = idToken.getClaimAsString(RESOURCE_LINK);
        if (resourceLink == null || resourceLink.isEmpty()) {
            throwInvalidIdTokenException("Resource Link claim missing from token.");
        } else {
            JSONObject object = (JSONObject) JSONValue.parse(resourceLink);
            String id = object.getAsString("id");

            if (id == null || id.isEmpty()) {
                throwInvalidIdTokenException("Resource Link ID claim missing from token.");
            }

        }

        String custom = idToken.getClaimAsString(CUSTOM);
        if (custom != null && !custom.isEmpty()) {
            JSONObject object = (JSONObject) JSONValue.parse(custom);
            String grade = object.getAsString("grade");

            if (grade == null || grade.isEmpty()) {
                throwInvalidIdTokenException("Resource Link custome.grade claim missing from token.");
            } else if (!INVALID_GRADES.contains(grade)) {
                throwInvalidIdTokenException("Resource Link custome.grade claim invalid value.");
            }

        }

        String nonce = idToken.getClaimAsString("nonce");
        if (nonce == null || nonce.isEmpty() || nonce.equals("null")) {
            throwInvalidIdTokenException("Resource Link nonce claim missing from token.");
        }

        String targetLinkUri = idToken.getClaimAsString(TARGET_LINK_URI);
        if (targetLinkUri == null || targetLinkUri.isEmpty()) {
            throwInvalidIdTokenException("Target Link URI nonce claim missing from token.");
        }

        String context = idToken.getClaimAsString(CONTEXT);
        if (context != null && !context.isEmpty()) {
            JSONObject object = (JSONObject) JSONValue.parse(custom);
            String id = object.getAsString("id");
            if (id == null || id.isEmpty()) {
                throwInvalidIdTokenException("Resource Link context.id claim missing from token.");
            }
        }

    }

    private static void throwInvalidIdTokenException() {
        throwInvalidIdTokenException(null);
    }

    public static void throwInvalidIdTokenException(String message) {
        OAuth2Error invalidIdTokenError = new OAuth2Error(INVALID_ID_TOKEN_ERROR_CODE);
        throw new OAuth2AuthenticationException(invalidIdTokenError, (message != null) ? message : invalidIdTokenError.toString());
    }

}
