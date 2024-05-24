package jp.co.example.springboot;

import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.annotation.AnnotationBeanNameGenerator;




/**
 * ComponentScan用のComponent作成クラス
 */
public class FQCNBeanNameGenerator extends AnnotationBeanNameGenerator {




    @Override
    protected String buildDefaultBeanName(BeanDefinition definition) {
        return definition.getBeanClassName();
    }




}
