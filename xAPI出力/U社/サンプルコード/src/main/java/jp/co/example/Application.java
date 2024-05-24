package jp.co.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.AnnotationBeanNameGenerator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.web.client.RestTemplate;

import jp.co.example.springboot.FQCNBeanNameGenerator;




/**
 * Spring Boot 起動クラス
 */
@SpringBootApplication
@ComponentScan(nameGenerator = FQCNBeanNameGenerator.class)
@EnableScheduling
public class Application extends AnnotationBeanNameGenerator {




    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    public RestTemplate getRestTemplate() {
       return new RestTemplate();
    }



}
