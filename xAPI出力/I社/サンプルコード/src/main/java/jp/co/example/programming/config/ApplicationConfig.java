package jp.co.example.programming.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import lombok.Getter;




/**
 * application.yml取得用クラス
 */
@Component("ApplicationConfig")
public class ApplicationConfig {

    /**
     * xAPI プロファイルテンプレートファイルパス
     */
    @Getter
    @Value("${settings.xapi.profile.template-file}")
    private String xapiProfileTemplateFile;

    /**
     * xAPI プロファイル出力パス
     */
    @Getter
    @Value("${settings.xapi.profile.output-path}")
    private String xapiProfileOutputPath;



}
