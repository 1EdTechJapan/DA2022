<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Storage;
use App\Models\User;
use App\Models\UserAnswer;
use App\Models\Question;
use App\Models\QuestionChoice;

class XapiController extends Controller
{
    // actor情報の定数
    private const ACTOR_OBJECT_TYPE      = 'Agent';
    private const ACTOR_ACCOUNT_HOMEPAGE = 'https://stg.aiaimonkey.com';

    // verb情報の定数
    private const VERB_ID         = 'http://adlnet.gov/expapi/verbs/answered';
    private const VERB_DISPLAY_EN = 'answered';

    // object情報の定数
    private const OBJECT_OBJECT_TYPE                 = 'Activity';
    private const OBJECT_ID_PREFIX                   = self::ACTOR_ACCOUNT_HOMEPAGE . '/questions/id#';
    private const OBJECT_DEFINITION_TYPE             = 'http://adlnet.gov/expapi/activities/interaction';
    private const OBJECT_DEFINITION_INTERACTION_TYPE = 'choice';

    // context情報の定数
    private const CONTEXT_CONTEXT_ACTIVITIES_CATEGORY_ARRAY = [
        'http://id.tincanapi.com/activity/lrp/ab_aiaimonkey/3.0.0' => 'http://id.tincanapi.com/activitytype/source',
        'https://w3id.org/xapi/ab_aiaimonkey/v/1'                  => 'https://w3id.org/xapi/jpedudataspec/activities/profile',
        'https://w3id.org/xapi/multilangsupport/ja/v/1'            => 'https://w3id.org/xapi/jpedudataspec/activities/profile',
        'https://w3id.org/xapi/jpedudataspec/v/1'                  => 'https://w3id.org/xapi/jpedudataspec/activities/profile'
    ];

    // result情報の定数
    private const RESULT_EXTENTIONS_KEY = 'https://w3id.org/xapi/ab_aiaimonkey/result/extensions/opinion';

    /**
     * 質問に対するユーザーの回答のログをファイルに出力するためのテストAPI
     *
     * @param
     *    Request request   リクエストパラメータ（質問を一意に識別するID）
     *
     * @return array 質問に対するユーザー回答ログ（JSON形式）
     */
    public function testOutputAnswerLog(Request $request) {
        // リクエストパラメータの質問ID（質問を一意に識別するID）を取得
        $question_id = $request['question_id'];

        // 質問に対するユーザーの回答のログをファイルに出力
        $result = $this->outputAnswerLog($question_id);

        // ファイルに保存しているのでjsonの内容を返却する必要がないがテスト結果確認用に返却する
        return response()->json($result);
    }
        
    /**
     * 質問に対するユーザーの回答のログをファイルに出力
     *
     * @param
     *    integer question_id   質問ID（質問を一意に識別するID）
     *
     * @return array 質問に対するユーザー回答ログ
     */
    private function outputAnswerLog($question_id = null) {
        // 質問IDに合致する質問情報の取得
        $question = Question::where('id', $question_id)->first();

        // 質問IDに合致する質問選択肢情報の一覧取得
        $question_choices = QuestionChoice::where('question_id', $question_id)->get();

        // 質問IDに合致するユーザー回答情報の一覧取得
        $user_answers = UserAnswer::where('question_id', $question_id)->get();

        // 取得したユーザー回答数分、json出力用の配列変数に格納
        $results = [];
        foreach ($user_answers as $user_answers) {
            $result = [];

            // ユーザー回答情報のuser_idに合致するユーザー情報の取得
            $user = User::where('id', $user_answers['user_id'])->first();

            // ステートメントIDの格納（UUID v4形式で発行）
            $result['id'] = strval(Str::uuid());            

            // actor情報の格納（ユーザーを一意に識別するaccount_id）
            $result['actor']['objectType'] = self::ACTOR_OBJECT_TYPE;
            $result['actor']['account']['homePage'] = self::ACTOR_ACCOUNT_HOMEPAGE;
            $result['actor']['account']['name'] = strval($user['account_id']);

            // verb情報の格納
            $result['verb']['id'] = self::VERB_ID;
            $result['verb']['display']['en'] = self::VERB_DISPLAY_EN;

            // object情報の格納（質問と質問選択肢）
            $result['object']['objectType'] = self::OBJECT_OBJECT_TYPE;
            $result['object']['id'] = self::OBJECT_ID_PREFIX . $question_id;
            $result['object']['definition']['name']['ja'] = strval($question['content']);
            $result['object']['definition']['type'] = self::OBJECT_DEFINITION_TYPE;
            $result['object']['definition']['interactionType'] = self::OBJECT_DEFINITION_INTERACTION_TYPE;
            $question_number = null;
            // object情報のdefinitionのcorrectResponsesPattern（質問選択肢正解パターン）とchoices（質問選択肢）の格納
            foreach ($question_choices as $question_choice) {
                $choice['id'] = strval($question_choice['number']);
                $choice['description']['ja'] = strval($question_choice['content']);
                $result['object']['definition']['correctResponsesPattern'][] = strval($question_choice['number']);
                $result['object']['definition']['choices'][] = $choice;

                // 質問選択肢のidとユーザー回答のquestion_choice_idが一致する場合は、質問選択肢のnumberを変数に格納（result情報の格納時に使用）
                if ($question_choice['id'] === $user_answers['question_choice_id']) {
                    $question_number = $question_choice['number'];
                }
            }

            // context情報の格納
            $i = 0;
            foreach (self::CONTEXT_CONTEXT_ACTIVITIES_CATEGORY_ARRAY AS $key => $value) {
                $result['context']['contextActivities']['category'][$i]['id'] = $key;
                $result['context']['contextActivities']['category'][$i]['definition']['type'] = $value;
                $i++;
            }

            // result情報の格納（ユーザーの回答とコメント）
            $result['result']['response'] = strval($question_number);
            $result['result']['extensions'][self::RESULT_EXTENTIONS_KEY] = strval($user_answers['comment']);

            // timestampの格納（ユーザーの回答日時）
            $date = new \DateTime($user_answers['updated_at'], new \DateTimeZone('Asia/Tokyo'));
            $result['timestamp'] = $date->format('Y-m-d\TH:i:s') . '+09:00';  
            $results[] = $result;
        }

        // 格納した情報をjson形式に変換してファイルに保存
        $file_name = 'xAPI_user_answer_' . $question_id . '.json';
        Storage::put($file_name, json_encode($results));

        // ファイルに保存しているので結果を返却する必要がないがテスト結果確認用に返却する
        return $results;
    }
}
