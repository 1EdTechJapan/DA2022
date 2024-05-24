package jp.co.example.springboot.validation;

import java.util.Set;

import javax.validation.ConstraintValidatorContext;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import javax.validation.Validator;

import org.springframework.beans.BeanWrapper;




/**
 * 入力チェックUtility
 */
public class ValidationUtility {

    //------------------------------------------------------------------
    //- constructor
    //------------------------------------------------------------------

    /**
     * constructor
     */
    private ValidationUtility() {
        // 外部からの呼び出し禁止
    }




    //----------------------------------------------------------------------
    //- methods
    //----------------------------------------------------------------------

    /**
     * アノテーション引き数に指定したメッセージのConstraintViolationを追加します
     *
     * @param context
     * @param field
     */
    public static void addDefaultMessageConstraintViolation(ConstraintValidatorContext context, String field) {
        context.buildConstraintViolationWithTemplate(context.getDefaultConstraintMessageTemplate())
            .addPropertyNode(field)
            .addConstraintViolation();
    }

    /**
     * 引き数に指定したメッセージのConstraintViolationを追加します
     *
     * @param context
     * @param field
     */
    public static void addMessageConstraintViolation(ConstraintValidatorContext context, String field, String message) {
        context.buildConstraintViolationWithTemplate(message)
            .addPropertyNode(field)
            .addConstraintViolation();
    }

    /**
     * 指定dvoにバリデーションを実行して、エラーがある場合はConstraintViolationExceptionをスローします
     *
     * @param validator
     * @param dvo
     */
    public static <T> void ifHasErrorThrow(Validator validator, T dvo) {
        Set<ConstraintViolation<T>> violations = validator.validate(dvo);
        if (!violations.isEmpty()) throw new ConstraintViolationException(violations);
    }

    /**
     * 数値関連チェック時に、wrapper.field の値を Double として取得します
     * field の許容される型： String/Integer/Long/Float/Double/int/long/float/double
     *
     * @param wrapper
     * @param field
     * @return
     */
    public static  Double beanDoubleValue(BeanWrapper wrapper, String field) {
        if (field.isEmpty()) return null;

        Object obj = wrapper.getPropertyValue(field);
        if (obj == null) return null;

        Double value = null;
        if (obj instanceof String)  {
            try {
                value = Double.valueOf((String)obj);
            } catch(NumberFormatException e) {
                // 数値チェックは他で
                return null;
            }
        }
        else if (obj instanceof Integer) value = ((Integer)obj).doubleValue();
        else if (obj instanceof Long)    value = ((Long)obj).doubleValue();
        else if (obj instanceof Float)   value = ((Float)obj).doubleValue();
        else if (obj instanceof Double)  value = (Double)obj;
        else                             throw new IllegalArgumentException("field type is not allowed: " + obj.getClass());
        return value;
    }




}
