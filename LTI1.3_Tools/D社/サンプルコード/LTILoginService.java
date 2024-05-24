package com.servername.bridge.service.identity;

import com.auth0.jwk.InvalidPublicKeyException;
import com.auth0.jwk.Jwk;
import com.auth0.jwk.JwkProvider;
import com.auth0.jwk.UrlJwkProvider;
import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.Claim;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.servername.bridge.dao.identity.MEXCBTDeploymentDao;
import com.servername.bridge.dao.identity.PartnerDao;
import com.servername.bridge.db.dbMEXCBTDeploymentEntity;
import com.servername.bridge.db.dbPartnerEntity;
import com.servername.bridge.factory.identity.LoginFactory;
import com.servername.bridge.util.Constants;
import com.servername.bridge.util.OneRosterUtilService;
import com.servername.services.element.identity.Login;
import com.servername.services.element.identity.Nonce;
import com.servername.services.exception.HttpServerErrorInternalException;
import com.servername.services.exception.HttpServiceUnavailableException;
import com.servername.services.exception.HttpUnauthorizedException;
import com.servername.services.persistence.ehcache.CacheName;
import com.servername.services.persistence.ehcache.EhcacheUtil;
import com.servername.services.persistence.sql.Transactional;
import com.servername.services.util.ConstantsBase;
import com.servername.services.util.StringUtil;

import javax.inject.Inject;
import java.net.URL;
import java.security.interfaces.RSAPublicKey;
import java.util.*;
import java.util.stream.Collectors;

public class LTILoginService {
    @Inject
    LoginV4Service loginV4Service;
    @Inject
    PartnerDao partnerDao;
    @Inject
    OneRosterUtilService oneRosterUtilService;
    @Inject
    MEXCBTDeploymentDao mexcbtDeploymentDao;

    private static final String LTI_CLIENT_ID = ConstantsBase.getStringProperty("lti.client.id");
    private static final Set<String> LTI_ROLE_LIBRARY = new HashSet<>(Arrays.asList("http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#None",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#User",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#None",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer"
    ));

    private Set<String> MEXCBTDeploymentIds = null;

    /**
     * Validate that this JWT is a valid signed LTI token
     *
     * @param jwt           The decoded JWT
     * @param partnerEntity The partner the account should be associated with
     * @return
     */
    public DecodedJWT validateJWT(DecodedJWT jwt, String state, dbPartnerEntity partnerEntity) {
        String nonce = jwt.getClaim("nonce").asString();
        Nonce nonceObj = nonce == null ? null : loginV4Service.retrieveNonce(nonce, state);
        JWTVerifier verifier = JWT.require(getAlgorithm(jwt.getAlgorithm(), getPublicKey(jwt.getKeyId(), partnerEntity.getJwkProviderUri())))
                .withIssuer(String.valueOf(partnerEntity.getJwkIssuer()))
                .withAudience(LTI_CLIENT_ID)
                .withClaim("iat", (claim, decodedJWT) -> !claim.isNull())
                .withClaim("exp", (claim, decodedJWT) -> !claim.isNull())
                .build();
        try {
            verifier.verify(jwt);
        } catch (JWTVerificationException e) {
            throw new HttpUnauthorizedException("Token verification failed", e, null);
        }
        if (nonceObj == null) {
            throw new HttpUnauthorizedException("Invalid nonce");
        }
        loginV4Service.clearNonce(nonce);
        return jwt;
    }

    /**
     * Build a signing algorithm object using a public key and an algorithm name
     *
     * @param algorithmName
     * @param key
     */
    private Algorithm getAlgorithm(String algorithmName, RSAPublicKey key) {
        switch (algorithmName) {
            case "RS256":
                return Algorithm.RSA256(key, null);
            case "RS384":
                return Algorithm.RSA384(key, null);
            case "RS512":
                return Algorithm.RSA512(key, null);
        }
        throw new HttpServerErrorInternalException("Can't handle JWT signing algorithm " + algorithmName);
    }

    /**
     * Check the cache for the public key with a given key id from a given provider. If it's not there,
     * fetch it from the provider.
     *
     * @param kid
     * @param providerUri
     * @return an RSAPublicKey
     */
    public RSAPublicKey getPublicKey(String kid, String providerUri) {
        String cacheKey = kid + "_" + providerUri;
        RSAPublicKey key = (RSAPublicKey) EhcacheUtil.get(CacheName.IDENTITY_LTI_PUBLIC_KEY, cacheKey);
        if (key == null) {
            try {
                key = (RSAPublicKey) fetchLTIPublicKey(kid, providerUri).getPublicKey();
            } catch (InvalidPublicKeyException e) {
                throw new HttpServerErrorInternalException("Invalid public key", e);
            }
            EhcacheUtil.put(CacheName.IDENTITY_LTI_PUBLIC_KEY, cacheKey, key, Constants.CACHE_DAY, Constants.CACHE_DAY);
        }
        return key;
    }

    /**
     * Fetch a public key from a public directory
     *
     * @param kid
     * @param providerUri
     * @return
     */
    public Jwk fetchLTIPublicKey(String kid, String providerUri) {
        try {
            JwkProvider provider = new UrlJwkProvider(new URL(providerUri));
            return provider.get(kid); //throws Exception when not found or can't get one
        } catch (Exception e) {
            throw new HttpServiceUnavailableException("Unable to fetch LTI public key", e, null, null, null, null);
        }
    }

    /**
     * Use a JWT to log in
     *
     * @param token                         The JWT
     * @param state                         The state string (a signed JWT)
     * @param name
     * @param unvalidatedEmail
     * @param identityID
     * @param arrivalID
     * @param ipAddress
     * @param countryCode
     * @param userAgent
     * @param siteLanguage
     * @param acceptLanguageHeader
     * @param requestedURL
     * @param referringURL
     * @param applicationName
     * @param applicationBuildDate
     * @param isChina
     * @param isMobile
     * @param timezone
     * @param overrideEnvironment
     * @param substituteIfTutorNotAvailable
     * @param forcePreviousAuthenticationId
     * @param deviceId
     * @param jsdkKey
     * @param fields
     * @param roleTypeIDs
     * @return
     */
    public Login loginWithLtiJWT(String token, String state, String name, String unvalidatedEmail, String identityID, String arrivalID, String ipAddress, String countryCode, String userAgent,
                                 String siteLanguage, String acceptLanguageHeader, String requestedURL, String referringURL, String applicationName, String applicationBuildDate,
                                 boolean isChina, boolean isMobile, String timezone, String overrideEnvironment, Boolean substituteIfTutorNotAvailable, String forcePreviousAuthenticationId,
                                 String deviceId, String jsdkKey, Set<String> fields, Set<Integer> roleTypeIDs) {
        DecodedJWT jwt = JWT.decode(token);
        String issuer = jwt.getClaim("iss").asString();
        dbPartnerEntity partner = getPartner(issuer);
        validateJWT(jwt, state, partner);
        String identifier = jwt.getSubject();
        String email = jwt.getClaim("email").asString();
        String foundName = jwt.getClaim("name").asString();
        String messageType = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/message_type").asString();
        String targetLinkUri = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/target_link_uri").asString();
        String deploymentId = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/deployment_id").asString();
        String version = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/version").asString();
        Map<String, Object> context = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/context").asMap();
        Map<String, Object> resourceLink = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/resource_link").asMap();
        Map<String, Object> tool_platform = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/tool_platform").asMap();
        Map<String, Object> custom = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/custom").asMap();
        Claim roleClaim = jwt.getClaim("https://purl.imsglobal.org/spec/lti/claim/roles");
        String roleString = roleClaim.asString();
        List<String> roles = roleClaim.asList(String.class);
        validateIdExists(context, "context");
        validateIdExists(resourceLink, "resource_link");
        validateToolPlatform(tool_platform);
        validateRoles(roles, roleString);
        if (messageType != null && !messageType.equals("LtiResourceLinkRequest")) {
            throw new HttpUnauthorizedException("Invalid message_type");
        }
        if (version != null && !version.equals("1.3.0")) {
            throw new HttpUnauthorizedException("Invalid version");
        }
        validateCustomClaim(custom);
        if (targetLinkUri != null && targetLinkUri.isEmpty()) {
            throw new HttpUnauthorizedException("Invalid target_link_uri");
        }
        if (identifier == null || identifier.isEmpty()) {
            //This is an anonymous login
            return loginV4Service.getAnonymousLogin(null, null, partner.getPartnerId(), partner.getPartnerId(),
                    siteLanguage, acceptLanguageHeader, requestedURL, referringURL, ipAddress, countryCode, userAgent, applicationName,
                    LoginFactory.getApplicationBuildDate(applicationBuildDate), isChina, isMobile, deviceId, jsdkKey, overrideEnvironment);
        }
        StringUtil.validateUUIDs(identifier);
        validateDeploymentId(deploymentId);
        Login login = loginV4Service.partnerLoginIfExists(identifier, identityID, arrivalID, ipAddress, countryCode, userAgent,
                partner.getPartnerId(), siteLanguage, acceptLanguageHeader, requestedURL, referringURL, applicationName, applicationBuildDate,
                isChina, isMobile, overrideEnvironment, forcePreviousAuthenticationId, fields);
        if (login != null) {
            return login;
        }
        String resolvedEmail = email == null ? unvalidatedEmail : email;
        String resolvedName = foundName == null ? name : foundName;
        return loginV4Service.registerAndLoginLTI(resolvedName, identityID, arrivalID, ipAddress, countryCode, userAgent, partner.getPartnerId(), siteLanguage, acceptLanguageHeader, requestedURL, referringURL, applicationName, applicationBuildDate, isChina, isMobile, timezone, overrideEnvironment, substituteIfTutorNotAvailable, forcePreviousAuthenticationId, fields, roleTypeIDs, resolvedEmail, identifier);
    }

    /**
     * Use the issuer claim of a JWT to identify the issuing Partner
     *
     * @param issuer The issuer claim
     * @return A partner database entity
     */
    @Transactional
    public dbPartnerEntity getPartner(String issuer) {
        if (issuer == null) {
            throw new HttpUnauthorizedException("Issuer claim not found");
        }
        dbPartnerEntity partner = partnerDao.retrievePartnerByIssuer(issuer);
        if (partner == null || partner.getJwkProviderUri() == null) {
            throw new HttpUnauthorizedException("Not a valid LTI issuer: " + issuer);
        }
        return partner;
    }

    private void validateIdExists(Map<String, Object> map, String mapName) {
        if (map == null || !map.containsKey("id")) {
            return;
        }
        Object id = map.get("id");
        if (!(id instanceof String) || ((String) id).isEmpty()) {
            throw new HttpUnauthorizedException("Invalid token: invalid " + mapName + "/id");
        }
    }

    private void validateToolPlatform(Map<String, Object> toolPlatform) {
        if (toolPlatform == null || !toolPlatform.containsKey("guid")) {
            return;
        }
        Object guid = toolPlatform.get("guid");
        if (!(guid instanceof String) || ((String) guid).isEmpty()) {
            throw new HttpUnauthorizedException("Invalid token: invalid tool platform");
        }
        String guidString = (String) guid;
        StringUtil.validateUUIDs(guidString);
    }

    private void validateCustomClaim(Map<String, Object> custom) {
        if (custom == null || !custom.containsKey("grade")) {
            //Leaving the grade out is valid
            return;
        }
        Object grade = custom.get("grade");
        if (!(grade instanceof String)) {
            throw new HttpUnauthorizedException("Invalid grade");
        }
        String gradeString = (String) grade;
        if (!oneRosterUtilService.gradeIsValid(gradeString)) {
            throw new HttpUnauthorizedException("Invalid grade");
        }
    }

    private void validateRoles(List<String> roles, String roleString) {
        //Roles is expected to be an array, in which case roles will exist and roleString will be null. If the roles claim is a string or is missing entirely, fail.
        if (roles == null || roleString != null) {
            throw new HttpUnauthorizedException("Roles not found");
        }
        if (roles.isEmpty()) { //The LTI standards allow an empty roles array, but MEXCBT's implementation does not
            throw new HttpUnauthorizedException("Roles not found");
        }
        //If the array is not empty, it must contain at least one recognized role, and is allowed to also contain non-recognized roles
        if (roles.stream().noneMatch(LTI_ROLE_LIBRARY::contains)) {
            throw new HttpUnauthorizedException("No recognized role found in roles");
        }
    }

    private void validateDeploymentId(String deploymentId) {
        if (StringUtil.anyEmptyOrNull(deploymentId)) {
            throw new HttpUnauthorizedException("Invalid token: missing deployment_id");
        }
        if (MEXCBTDeploymentIds == null) {
            fetchDeploymentIds();
        }
        if (!MEXCBTDeploymentIds.contains(deploymentId)) {
            throw new HttpUnauthorizedException("Invalid deployment id");
        }
    }

    @Transactional
    private void fetchDeploymentIds() {
        List<dbMEXCBTDeploymentEntity> deploymentEntities = mexcbtDeploymentDao.getAll();
        MEXCBTDeploymentIds = deploymentEntities.stream().map(dbMEXCBTDeploymentEntity::getIdCode).collect(Collectors.toSet());
    }
}