package jp.co.example.osarai2.definition;

import java.util.Arrays;
import java.util.List;

import org.springframework.stereotype.Component;

/**
 * LTIリクエストの定数定義
 */
@Component("lti_request")
public class lti_request {

    //------------------------------------------------------------------
    //- パラメーター名
    //------------------------------------------------------------------

    // initiation
    public static final String KEY_INIT_ISS = "iss";
    public static final String KEY_INIT_LOGIN_HINT = "login_hint";
    public static final String KEY_INIT_TARGET_LINK_URI = "target_link_uri";
    public static final String KEY_INIT_CLIENT_ID = "client_id";
    public static final String INIT_DEPLOYMENT_ID = "lti_deployment_id";
    public static final String KEY_INIT_MESSAGE_HINT = "lti_message_hint";
    public static final String KEY_INIT_RESPONSE_TYPE = "response_type";
    public static final String INIT_RESPONSE_MODE = "response_mode";
    public static final String KEY_INIT_SCOPE = "scope";
    public static final String KEY_INIT_PROMPT = "prompt";
    public static final String KEY_INIT_REDIRECT_URI = "redirect_uri";

    // resource link
    public static final String KEY_LINK_STATE = "state";
    public static final String KEY_LINK_SUB = "sub";
    public static final String KEY_LINK_AUD = "aud";
    public static final String KEY_LINK_EXP = "exp";
    public static final String KEY_LINK_IAT = "iat";
    public static final String KEY_LINK_NONCE = "nonce";
    public static final String KEY_LINK_AZP = "azp";
    public static final String KEY_LINK_NAME = "name";
    public static final String KEY_LINK_GIVEN_NAME = "given_name";
    public static final String KEY_LINK_FAMILY_NAME = "family_name";
    public static final String KEY_LINK_MIDDLE_NAME = "middle_name";
    public static final String KEY_LINK_PICTURE = "picture";
    public static final String KEY_LINK_EMAIL = "email";
    public static final String KEY_LINK_MESSAGE_TYPE = "https://purl.imsglobal.org/spec/lti/claim/message_type";
    public static final String KEY_LINK_VERSION = "https://purl.imsglobal.org/spec/lti/claim/version";
    public static final String KEY_LINK_ROLES = "https://purl.imsglobal.org/spec/lti/claim/roles";
    public static final String KEY_LINK_ROLE_SCOPE_MENTOR = "https://purl.imsglobal.org/spec/lti/claim/role_scope_mentor";
    public static final String KEY_LINK_TARGET_LINK_URI = "https://purl.imsglobal.org/spec/lti/claim/target_link_uri";
    public static final String KEY_LINK_DEPLOYMENT_ID = "https://purl.imsglobal.org/spec/lti/claim/deployment_id";
    public static final String KEY_LINK_CONTEXT = "https://purl.imsglobal.org/spec/lti/claim/context";
    public static final String KEY_LINK_CONTEXT_ID = "id";
    public static final String KEY_LINK_CONTEXT_LABEL = "label";
    public static final String KEY_LINK_CONTEXT_TITLE = "title";
    public static final String KEY_LINK_CONTEXT_TYPE = "type";
    public static final String KEY_LINK_RESOURCE_LINK = "https://purl.imsglobal.org/spec/lti/claim/resource_link";
    public static final String KEY_LINK_RESOURCE_LINK_ID = "id";
    public static final String KEY_LINK_RESOURCE_LINK_DESCRPTION = "description";
    public static final String KEY_LINK_RESOURCE_LINK_TITLE = "title";
    public static final String KEY_LINK_TOOL_PLATFORM = "https://purl.imsglobal.org/spec/lti/claim/tool_platform";
    public static final String KEY_LINK_TOOL_PLATFORM_GUID = "guid";
    public static final String KEY_LINK_TOOL_PLATFORM_CONTACT_EMAIL = "contact_email";
    public static final String KEY_LINK_TOOL_PLATFORM_DESCRIPTION = "description";
    public static final String KEY_LINK_TOOL_PLATFORM_NAME = "name";
    public static final String KEY_LINK_TOOL_PLATFORM_URL = "url";
    public static final String KEY_LINK_TOOL_PLATFORM_PRODUCT_FAMILY_CODE = "product_family_code";
    public static final String KEY_LINK_TOOL_PLATFORM_VERSION = "version";
    public static final String KEY_LINK_LAUNCH_PRESENTATION = "https://purl.imsglobal.org/spec/lti/claim/launch_presentation";
    public static final String KEY_LINK_LAUNCH_PRESENTATION_DOCUMENT_TARGET = "document_target";
    public static final String KEY_LINK_LAUNCH_PRESENTATION_HEIGHT = "height";
    public static final String KEY_LINK_LAUNCH_PRESENTATION_WIDTH = "width";
    public static final String KEY_LINK_LAUNCH_PRESENTATION_RETURN_URL = "return_url";
    public static final String KEY_LINK_LAUNCH_PRESENTATION_LOCALE = "locale";
    public static final String KEY_LINK_LIS = "https://purl.imsglobal.org/spec/lti/claim/lis";
    public static final String KEY_LINK_LIS_PERSON_SOURCEDID = "person_sourcedid";
    public static final String KEY_LINK_LIS_COURSE_OFFERING_SOURCEDID = "course_offering_sourcedid";
    public static final String KEY_LINK_LIS_COURSE_SECTION_SOURCEDID = "course_section_sourcedid";
    public static final String KEY_LINK_CUSTOM = "https://purl.imsglobal.org/spec/lti/claim/custom";
    public static final String KEY_LINK_CUSTOM_GRADE = "grade";
    public static final String KEY_LINK_CUSTOM_CLASSNAME = "classname";



    //------------------------------------------------------------------
    //- パラメーター値
    //------------------------------------------------------------------

    public static final int UUID_VERSION = 4;
    public static final String MESSAGE_TYPE = "LtiResourceLinkRequest";
    public static final String LTI_VERSION = "1.3.0";
    public static final List<String> GRADE_CODES = Arrays.asList(
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
        "J1",
        "J2",
        "J3",
        "H1",
        "H2",
        "H3",
        "E1",
        "E2",
        "E3"
    );
    public static final List<String> ROLES = Arrays.asList(
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
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
    );


    //------------------------------------------------------------------
    //- constructor
    //------------------------------------------------------------------

    /**
     * constructor（外部new禁止）
     */
    protected lti_request() {
    }




}
