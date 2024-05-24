<?php
// 
class LtiSSO {

    /**
     * コンストラクタ
     * Lti用のSSOオブジェクト
     *
     * @access public
     */
    public function __construct(){
        
    }

    /**
     * Ltiログイン処理
     * 
     * @param array        $launch_data JWTデータ
     *
     */
    public function lti_login($launch_data) {

        if ($launch_data === null) {
            throw new Exception("No launch data", 1);
        }

        // sub抽出
        $sub = $launch_data['sub'];

        // uuidチェック 正規表現で形式をチェックします
        $UUIDv4 = '/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i';
        if (!preg_match($UUIDv4, $sub)) {
            throw new Exception("Not in UUID format", 1);
        };

        // role抽出(判断できなかったら、先生とする)
        $role = "";
        $role_array = $launch_data['https://purl.imsglobal.org/spec/lti/claim/roles'];

        // 権限チェック
        if (is_array($role_array)) {
            foreach ($role_array as $value) {
                // 先生の権限を持っていたら、先生とする
                if (strpos($value,'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor') !== false ||
                    strpos($value,'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty') !== false) {
                    $role = "teacher";
                    break;
                }
                // 生徒の権限
                if (strpos($value,'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner') !== false ||
                    strpos($value,'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student') !== false) {
                    $role = "student";
                }
            }
        }
        
    }

    // ログイン処理
    // login($sub, $role)

    return;

    }
}
