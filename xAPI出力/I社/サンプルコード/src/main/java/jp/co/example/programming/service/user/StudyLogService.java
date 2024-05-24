package jp.co.example.programming.service.user;

import java.io.File;
import java.net.InetAddress;
import java.util.Properties;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import jp.co.example.programming.config.ApplicationConfig;
import jp.commoncode.common.EncodingConst;
import jp.commoncode.common.FileUtility;
import jp.commoncode.common.TemplateLoader;
import jp.commoncode.common.TimeUtility;

@Service
public class StudyLogService {

    @Autowired
    private ApplicationConfig config;

    /**
     * 学習ログ、学習者進度、学習月カウント、学習日カウントを登録/更新します
     *
     * @param studyRequest
     * @return
     */
    public void create(/* StudyRequest studyRequest */) {
        // 送信された学習データをDBへ保存
        // 自社独自領域のため割愛

        // xAPIデータ出力
        try {
            String userId    = "dfbed5bd-613c-465b-a7c3-f6242ad2087f";
            String studyPath = "https://example.com/study";
            String stageName = "stage name";

            // テンプレートファイルの置換情報
            Properties props = new Properties();
            props.put("HOST_NAME",  InetAddress.getLocalHost().getHostName());
            props.put("UUID",       UUID.randomUUID().toString());
            props.put("USER_UUID",  userId);
            props.put("STUDY_PATH", studyPath);
            props.put("STAGE_NAME", stageName);

            // テンプレートファイルを読み込み、置換情報をもとに置換した状態で取得
            String profile = TemplateLoader.getTemplate(config.getXapiProfileTemplateFile(), props);

            // ファイルに出力
            String path     = config.getXapiProfileOutputPath() + userId + File.separator;
            String fileName = TimeUtility.createTimestamp().getTime() + ".json";
            FileUtility.writeFile(path + fileName, profile.getBytes(EncodingConst.UTF8));

        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

}
