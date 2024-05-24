	
	/**
	 * ログイン xAPIデータ生成
	 * 
	 * @param array $data HPアドレス、生徒ID(UUID)、ログイン時のURL、ログイン時間を設定
	 * @return string jsonデータ
	 */
	function login_xAPI_json($data){
		
		$json_data = NULL;
		
		if (is_array($data)) {
			
			$json_array = array();
			
			// UUID生成
			$uuid = create_UUID();

			// JSON生成配列作成
			$json_array['id']								= $uuid;
			
			$json_array['actor']['objectType']				= 'Agent';
			$json_array['actor']['account']['homePage']		= $data[HPアドレス];
			$json_array['actor']['account']['name']			= $data[生徒ID(UUID)];
			
			$json_array['verb']['id']						= 'https://w3id.org/xapi/adl/verbs/logged-in';
			$json_array['verb']['display']['en-US']			= 'logged-in';
			
			$json_array['object']['id']						= $data[ログイン時のURL];
			$json_array['object']['objectType']				= 'Activity';
			
			$json_array['context']['platform']				= 'service_name';
			$json_array['context']['language']				= 'ja-JP';
			
			$category_tmp = array();
			$category_tmp['id']						= 'http://id.tincanapi.com/activity/lrp/[ツール名]/[バージョン]';
			$category_tmp['definition']['type']		= 'http://id.tincanapi.com/activitytype/source';
			$json_array['context']['contextActivities']['category'][]	= $category_tmp;
			
			$json_array['timestamp']						= date('c', strtotime($data[ログイン時間]));
			
			$json_data = json_encode($json_array);
		}
		
		return $json_data;
	}
	
	/**
	 * ログアウト xAPIデータ生成
	 * 
	 * @param array $data HPアドレス、生徒ID(UUID)、ログアウト時のURL、ログアウト時間を設定
	 * @return string jsonデータ
	 */
	function logout_xAPI_json($data){
		
		$json_data = NULL;
		
		if (is_array($data)) {
			
			$json_array = array();
			
			// UUID生成
			$uuid = create_UUID();

			// JSON生成配列作成
			$json_array['id']								= $uuid;
			
			$json_array['actor']['objectType']				= 'Agent';
			$json_array['actor']['account']['homePage']		= $data[HPアドレス];
			$json_array['actor']['account']['name']			= $data[生徒ID(UUID)];
			
			$json_array['verb']['id']						= 'https://w3id.org/xapi/adl/verbs/logged-out';
			$json_array['verb']['display']['en-US']			= 'logged-out';
			
			$json_array['object']['id']						= $data[ログアウト時のURL];
			$json_array['object']['objectType']				= 'Activity';
			
			$json_array['context']['platform']				= 'service_name';
			$json_array['context']['language']				= 'ja-JP';
			
			$category_tmp = array();
			$category_tmp['id']						= 'http://id.tincanapi.com/activity/lrp/[ツール名]/[バージョン]';
			$category_tmp['definition']['type']		= 'http://id.tincanapi.com/activitytype/source';
			$json_array['context']['contextActivities']['category'][]	= $category_tmp;
			
			$json_array['timestamp']						= date('c', strtotime($data[ログアウト時間]));
			
			$json_data = json_encode($json_array);
		}
		
		return $json_data;
	}
	
	/**
	 * ドリル開始 xAPIデータ生成
	 * 
	 * @param array $data HPアドレス、生徒ID(UUID)、ドリル開始時のURL、ドリル開始時間を設定
	 * @return string jsonデータ
	 */
	function drill_start_xAPI_json($data){
		
		$json_data = NULL;
		
		if (is_array($data)) {
			
			$json_array = array();
			
			// UUID生成
			$uuid = create_UUID();

			// JSON生成配列作成
			$json_array['id']								= $uuid;
			
			$json_array['actor']['objectType']				= 'Agent';
			$json_array['actor']['account']['homePage']		= $data[HPアドレス];
			$json_array['actor']['account']['name']			= $data[生徒ID(UUID)];
			
			$json_array['verb']['id']						= 'http://adlnet.gov/expapi/verbs/attempted';
			$json_array['verb']['display']['en-US']			= 'attempted';
			
			$json_array['object']['id']						= $data[ドリル開始時のURL];
			$json_array['object']['objectType']				= 'Activity';
			
			$json_array['context']['platform']				= 'service_name';
			$json_array['context']['language']				= 'ja-JP';
			
			$category_tmp = array();
			$category_tmp['id']						= 'http://id.tincanapi.com/activity/lrp/[ツール名]/[バージョン]';
			$category_tmp['definition']['type']		= 'http://id.tincanapi.com/activitytype/source';
			$json_array['context']['contextActivities']['category'][]	= $category_tmp;
			
			$json_array['timestamp']						= date('c', strtotime($data['ドリル開始時間']));
			
			$json_data = json_encode($json_array);
		}
		
		return $json_data;
	}
	
	/**
	 * ドリル終了 xAPIデータ生成
	 * 
	 * @param array $data HPアドレス、生徒ID(UUID)、ドリル終了時のURL、ドリル終了時間を設定
	 * @return string jsonデータ
	 */
	function drill_end_xAPI_json($data){
		
		$json_data = NULL;
		
		if (is_array($data)) {
			
			$json_array = array();
			
			// UUID生成
			$uuid = create_UUID();

			// JSON生成配列作成
			$json_array['id']								= $uuid;
			
			$json_array['actor']['objectType']				= 'Agent';
			$json_array['actor']['account']['homePage']		= $data[HPアドレス];
			$json_array['actor']['account']['name']			= $data[生徒ID(UUID)];
			
			$json_array['verb']['id']						= 'http://adlnet.gov/expapi/verbs/exited';
			$json_array['verb']['display']['en-US']			= 'exited';
			
			$json_array['object']['id']						= $data[ドリル終了時のURL];
			$json_array['object']['objectType']				= 'Activity';
			
			$json_array['context']['platform']				= 'service_name';
			$json_array['context']['language']				= 'ja-JP';
			
			$category_tmp = array();
			$category_tmp['id']						= 'http://id.tincanapi.com/activity/lrp/[ツール名]/[バージョン]';
			$category_tmp['definition']['type']		= 'http://id.tincanapi.com/activitytype/source';
			$json_array['context']['contextActivities']['category'][]	= $category_tmp;
			
			$json_array['timestamp']						= date('c', strtotime($data['ドリル開始時間']));
			
			$json_data = json_encode($json_array);
		}
		
		return $json_data;
	}

	/**
	 * 学習回答 xAPIデータ生成
	 * 
	 * @param array $data 問題形式、正解設定、正誤判定、解答、HPアドレス、生徒ID(UUID)、問題解答時のURL、単元情報、問題文、解答時間、問題解答日時を設定
	 * @return string jsonデータ
	 */
	function study_xAPI_json($data){
		
		$json_data = NULL;
		
		if (is_array($data)) {
			
			$json_array = array();
			
			// 問題タイプ判断
			$interactionType = "";
			switch($data['問題形式']) {
				case aa :
					$interactionType = "choice";
					break;
				case bb :
					$interactionType = "fill-in";
					break;
				case cc :
					$interactionType = "long-fill-in";
					break;
				default:
					$interactionType = "other";
			}
			
			// 選択肢情報生成
			$choice = NULL;
			if ($interactionType == "choice") {
				// 選択肢成形
			}
			
			// 正解設定
			$correct = $data['正解設定'];
			
			// 正誤判定
			if ($data['正解'] == '正解') { $success = true; }
			if ($data['正解'] == '不正解') { $success = false; }
			
			// 解答を加工
			$answer = $data['解答'];
			
			// UUID生成
			$uuid = create_UUID();

			// JSON生成配列作成
			$json_array['id']												= $uuid;
			
			$json_array['actor']['objectType']								= 'Agent';
			$json_array['actor']['account']['homePage']						= $data[HPアドレス];
			$json_array['actor']['account']['name']							= $data[生徒ID(UUID)];
			
			$json_array['verb']['id']										= 'http://adlnet.gov/expapi/verbs/answered';
			$json_array['verb']['display']['en-US']							= 'answered';
			
			$json_array['object']['id']										= $data[問題解答時のURL];
			$json_array['object']['objectType']								= 'Activity';
			$json_array['object']['definition']['name']['ja-JP']			= $data['単元情報'];
			$json_array['object']['definition']['description']['ja-JP']		= $data['問題文'];
			$json_array['object']['definition']['type']						= 'https://adlnet.gov/expapi/activities/cmi.interaction';
			$json_array['object']['definition']['interactionType']			= $interactionType;
			$json_array['object']['definition']['correctResponsesPattern']	= $correct;
			if ($choice) {
				$json_array['object']['definition']['choices']				= $choice;
			}
			
			$json_array['result']['success']								= $success;
			$json_array['result']['response']								= $answer;
			$json_array['result']['completion']								= true;
			$json_array['result']['duration']								= "PT".$data['解答時間'].".00S";
			
			$category_tmp = array();
			$category_tmp['id']						= 'http://id.tincanapi.com/activity/lrp/[ツール名]/[バージョン]';
			$category_tmp['definition']['type']		= 'http://id.tincanapi.com/activitytype/source';
			$json_array['context']['contextActivities']['category'][]	= $category_tmp;
			
			$json_array['timestamp']										= date('c', strtotime($data['問題解答日時']));
			
			$json_data = json_encode($json_array);
		}
		
		return $json_data;
	}
