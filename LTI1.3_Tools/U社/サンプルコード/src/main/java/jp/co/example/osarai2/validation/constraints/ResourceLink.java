package jp.co.example.osarai2.validation.constraints;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

import javax.validation.Constraint;
import javax.validation.Payload;
import javax.validation.ReportAsSingleViolation;

import jp.co.example.osarai2.validation.validator.ResouceLinkValidator;




/**
 * ResouceLinkチェックAnnotation
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = {ResouceLinkValidator.class})
@ReportAsSingleViolation
public @interface ResourceLink {

    String message() default "{application.validation.invalid.message}";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};

    @Target(ElementType.TYPE)
    @Retention(RetentionPolicy.RUNTIME)
    @Documented
    public static @interface List {
        ResourceLink[] value();
    }




}
