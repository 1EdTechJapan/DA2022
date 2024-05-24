package jp.co.example.programming.validation.validator;

import java.util.UUID;
import java.util.function.Function;
import java.util.function.Predicate;

import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

import org.springframework.beans.factory.annotation.Autowired;

import jp.co.example.programming.config.ApplicationConfig;
import jp.co.example.programming.data.lti.ResourceLinkData;
import jp.co.example.programming.definition.lti_request;
import jp.co.example.programming.validation.constraints.ResourceLink;
import jp.co.example.springboot.validation.ValidationUtility;




/**
 * ResouceLinkチェックValidator
 */
public class ResouceLinkValidator implements ConstraintValidator<ResourceLink, ResourceLinkData> {

    @Autowired
    ApplicationConfig config;



    @Override
    public void initialize(ResourceLink annotation) {
    }

    @Override
    public boolean isValid(ResourceLinkData data, ConstraintValidatorContext context) {
        context.disableDefaultConstraintViolation();
        Boolean isValid = true;

        // バリデーションエラー時の設定を行い、返り値を返却します
        Function<String, Boolean> violation = (field) -> {
            ValidationUtility.addDefaultMessageConstraintViolation(context, field);
            return false;
        };

        // iss
        if (isInvalidField(data.getIss(), (iss) -> !iss.equals(config.getLtiPlatformId()))) {
            isValid = violation.apply(lti_request.KEY_INIT_ISS);
        }
        // sub
        if (isInvalidFieldAndNotNull(data.getSub(), (sub) -> !isValidUUIDString(sub))) {
            isValid = violation.apply(lti_request.KEY_LINK_SUB);
        }
        // aud
        if (isInvalidField(data.getAud(), (aud) -> !aud.contains(config.getLtiClientId()))) {
            isValid = violation.apply(lti_request.KEY_LINK_AUD);
        }
        // message_type
        if (isInvalidField(data.getMessageType(), (type) -> !type.equals(lti_request.MESSAGE_TYPE))) {
            isValid = violation.apply(lti_request.KEY_LINK_MESSAGE_TYPE);
        }
        // version
        if (isInvalidField(data.getVersion(), (ver) -> !ver.equals(lti_request.LTI_VERSION))) {
            isValid = violation.apply(lti_request.KEY_LINK_VERSION);
        }
        // roles
        if (isInvalidField(data.getRoles(), (roles) -> roles.stream().anyMatch(r -> !lti_request.ROLES.contains(r)))) {
            isValid = violation.apply(lti_request.KEY_LINK_ROLES);
        }
        // deployment_id
        if (isInvalidField(data.getDeploymentId(), (id) -> !id.equals(config.getLtiDeploymentId()))) {
            isValid = violation.apply(lti_request.KEY_LINK_DEPLOYMENT_ID);
        }
        // context/id
        if (isInvalidField(data.getContextId(), (id) -> id.isBlank())) {
            isValid = violation.apply(lti_request.KEY_LINK_CONTEXT + "/" + lti_request.KEY_LINK_CONTEXT_ID);
        }
        // resource_link/id
        if (isInvalidField(data.getResourceLinkId(), (id) -> id.isBlank())) {
            isValid = violation.apply(lti_request.KEY_LINK_RESOURCE_LINK + "/" + lti_request.KEY_LINK_RESOURCE_LINK_ID);
        }
        // target_link_uri
        if (isInvalidField(data.getTargetLinkUri(), (uri) -> !uri.equals(config.getLtiLaunchUrl()))) {
            isValid = violation.apply(lti_request.KEY_LINK_TARGET_LINK_URI);
        }
        // tool_platform/guid
        if (isInvalidFieldAndNotNull(data.getToolPlatformGuid(), (guid) -> !isValidUUIDString(guid))) {
            isValid = violation.apply(lti_request.KEY_LINK_TOOL_PLATFORM + "/" + lti_request.KEY_LINK_TOOL_PLATFORM_GUID);
        }
        // custom/grade
        if (isInvalidFieldAndNotNull(data.getCustomGrade(), (grade) -> !lti_request.GRADE_CODES.contains(grade))) {
            isValid = violation.apply(lti_request.KEY_LINK_CUSTOM + "/" + lti_request.KEY_LINK_CUSTOM_GRADE);
        }

        return isValid;
    }

    /**
     * 文字列がバージョン4のUUID形式かチェックします
     *
     * @param str
     * @return バージョン4のUUID形式の場合はtrue
     */
    private boolean isValidUUIDString(String str) {
        try {
            // 生成したUUIDと一致する、かつUUIDのバージョンが4の場合はtrue
            UUID generatedUUID = UUID.fromString(str);
            return str.equals(generatedUUID.toString()) && generatedUUID.version() == lti_request.UUID_VERSION;
        } catch (Exception e) {
            // 例外（UUID生成が失敗した）の場合はfalse
            return false;
        }
    }

    /**
     * 指定パラメータがnullでない、かつ否定評価式に合致するかチェックします
     *
     * @param <T>
     * @param data
     * @param invalidPredicate
     * @return 指定パラメータがnullでない、かつ否定評価式に合致する場合はtrue
     */
    private <T> boolean isInvalidFieldAndNotNull(T data, Predicate<T> invalidPredicate) {
        return data != null && isInvalidField(data, invalidPredicate);
    }

    /**
     * 指定パラメータが否定評価式に合致するかチェックします
     *
     * @param <T>
     * @param data
     * @param invalidPredicate
     * @return 指定パラメータが否定評価式に合致する場合はtrue
     */
    private <T> boolean isInvalidField(T data, Predicate<T> invalidPredicate) {
        return invalidPredicate.test(data);
    }

}
