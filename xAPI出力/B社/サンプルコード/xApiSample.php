<?php

namespace App\Http\Controllers;

use App\Models\Server;
use App\Models\Course;
use Carbon\Carbon;

/**
 *  xApiに関連する操作をまとめたクラス
 */
class xApiController 
{
    /**
     *  LRSにステートメントを送信する
     *
     */
    public function sendStatement( ){
        // 仮の成績情報
        $study_logs = [];
        $log1 = [
            "user" => "C2EA034D-9BF1-465F-8193-542B67F3A665",
            "server_id" => 1,
            "ug_id" => "LTI_TEST",
            "course" => "SJ01",
            "avg_score" => 99.25,
            "progress" => 23.33,
            "access" => 25,
            "total_study" => "PT4H35M20.00S",
            "start" => "2023-01-10",
            "end" => "2023-02-10",
        ];
        $log2 = [
            "user" => "8BC46A9E-1D63-4F5C-A785-E990EE8D1284",
            "server_id" => 1,
            "ug_id" => "LTI_TEST",
            "course" => "SG01",
            "avg_score" => 0,
            "progress" => 0,
            "access" => 1,
            "total_study" => "PT1H35M20.00S",
            "start" => "2023-01-09",
            "end" => "2023-02-10",
        ];
        $study_logs[] = $log1;
        $study_logs[] = $log2; 
       
        $array_statement = [];
        foreach($study_logs as $log){
            $array_statement[] = $this->makeProgressedCourseStatement($log);
        }
        
        $statements = json_encode($array_statement);
        
        // ユーザー情報
        $user = config('my_app.lrs_user');
        $pass = config('my_app.lrs_pass');

        // LRSエンドポイント
        $lrs_url = config('my_app.lrs_endpoint')."statements" ;

        $headers = array(
            'Content-Type: application/json',
            'Authorization: Basic ' . base64_encode($user.':'.$pass),
            'X-Experience-API-Version: 1.0.1'
        );

        // 送信（json形式・post）
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
        curl_setopt($ch, CURLOPT_POSTFIELDS, $statements);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_URL, $lrs_url);
        $result=curl_exec($ch); // 正常ならステートメントのIDが配列で返される
        
        curl_close($ch);
    }

    /**
     * ステートメントのActor要素を返す
     * 
     * @param string $user
     * @param int $server_id
     * @return array
     */
    public function makeActor($user, $server_id){
        // Serverクラスのメソッドに$server_idを引数として渡し、$server_url(サービスのURL)を受け取る
        $server_url = Server::find($server_id)->url;
        $actor = [];
        $actor["objectType"] = "Agent";
        $actor["account"] = [
            "homePage" => $server_url,
            "name" => $user
        ];
        return $actor;
    }
    
    /**
     * ステートメントのCategory要素を返す。
     * 
     * Categoryはステートメントを分類する。使用プロファイルや事業者情報を記載
     * 
     * @return array
     */
    public function makeContextCategory(){
        $category = array(
            [
                "id" => "http://id.tincanapi.com/activity/lrp/ATRLT_ATRCALL/14",
                "definition" => [ 
                    "type" => "http://id.tincanapi.com/activitytype/source"
                ]
            ],
            [
                "id" => "https://w3id.org/xapi/multilangsupport/ja/v/1",
                "definition" => [
                    "type" => "https://w3id.org/xapi/jpedudataspec/activities/profile"
                ]
            ],
            [
                "id" => "https://w3id.org/xapi/jpedudataspec/v/1",
                "definition" => [
                    "type" => "https://w3id.org/xapi/jpedudataspec/activities/profile"
                ]
            ],
            [
                "id" => "https://w3id.org/xapi/atrcallbrix/v/1",
                "definition" => [
                    "type" => "https://w3id.org/xapi/jpedudataspec/activities/profile"
                ]
            ],

        );
       
        return $category;
    }

    /**
     * ステートメントに用いるコース（Activity）の要素を返す
     *
     * @param string $brix_course
     * @return array
     */
    public function makeActivityCourse($brix_course){
        $course = Course::find($brix_course);
        $course_name = $course->name;
        $course_desc = $course->description;
        $activity = [];
        $activity["id"] = "http://adlnet.gov/courses/". $brix_course;
        $activity["definition"] = [
            "name" => [
                "ja" => $course_name
            ],
            "description" => [
                "ja" => $course_desc
            ],
            "type" => "http://adlnet.gov/expapi/activities/course"
        ];
       
        return $activity;
    }

    /**
     * ステートメントを生成し、返す
     *
     * @param array $study_log
     * @return array
     */
    public function makeProgressedCourseStatement( $study_log ){
        $statement = [];
        // actor
        $statement["actor"] = $this->makeActor($study_log["user"], $study_log["server_id"]);
        
        // verb
        $verb = [
            "id" => "http://adlnet.gov/expapi/verbs/progressed",
            "display" => [
                "en-US" => "progressed" 
            ]
        ];        
        $statement["verb"] = $verb;

        // object
        $course_array = $this->makeActivityCourse($study_log['course']); // コースの情報を取得
        $object = [
            "objectType" => "Activity",
            "id" => $course_array["id"],
            "definition" => $course_array["definition"]
        ] ;
        $statement["object"] = $object;

        // result
        $result = [
            "score" => [
                "scaled" => $study_log["avg_score"] / 100,
                "raw" => $study_log["avg_score"],
                "max" => 100,
                "min" => 0
            ],
            "success" => true,
            "duration" => $study_log["total_study"], // 期間
            "extensions" => [
                "https://w3id.org/xapi/atrcallbrix/result/extensions/progress" => $study_log["progress"], //進捗率
                "https://w3id.org/xapi/atrcallbrix/result/extensions/access" => $study_log["access"], // 実施回数
            ]
        ];
        $statement["result"] = $result;

        // context
        $context = [
            "contextActivities" => [
                "category" => $this->makeContextCategory(), // 参照しているプロファイル、事業者情報など
                "grouping" => [ 
                    $this->makeActivityCourse($study_log['course'])
                ]
            ], 
            "extensions" => [
                "https://w3id.org/xapi/atrcallbrix/startdate" => $study_log["start"],
                "https://w3id.org/xapi/atrcallbrix/enddate" => $study_log["end"],
                "https://w3id.org/xapi/atrcallbrix/recordid" => $study_log["user"]
            ],
            
        ];
        $statement["context"] = $context;
        
        // timestamp
        $cb = New Carbon();
        $timestamp = $cb->format('Y-m-d\TH:i:s.vP'); //ISO8601 UTC ミリ秒表示　推奨
        $statement["timestamp"] = $timestamp;

        return $statement;
    }

}
