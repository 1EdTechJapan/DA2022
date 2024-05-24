module Api
  module Student
    # 生徒がLTIを通じてログインするためのController
    class LtiController < ApplicationController
      # 弊社独自領域ここから---
      ## 各メソッド実行前に認証チェックを行わない
      skip_before_action :my_authenticate_user
      # ---弊社独自領域ここまで

      # ResourceLinkRequestにより実行されるメソッド
      # Callback URLへPOST疑似リダイレクトする
      def implicit_back
        domain = request.headers["SERVER_NAME"]

        render html: Repost::Senpai.perform(
          "https://#{domain}:#{request.port}/api/auth/student_lti/callback",
          params: { utf8: params[:utf8], id_token: params[:id_token], state: params[:state], commit: params[:commit] }
        ).html_safe
      end

      # Callback phase後に実行されるメソッド
      # omniauth_openid_connectではチェックできていないパラメータの入力チェックを行い、エラー出力、またはログインする
      def launches
        # パラメータの入力チェックを行う
        valid_lti_params

        # 弊社独自領域ここから---
        ## "sub"で生徒をデータベースから検索する
        student_info = if auth_hash['uid'].present?
                         StudentInfo.joins(:student)
                                    .where(student: {
                                             uuid: auth_hash['uid'],
                                             id_status: %i[active locked]
                                           })
                                    .order(nendo: :desc).first
                       end
        ## 生徒が見つからない場合、エラーをレスポンスする
        if student_info.blank?
          render_err 'UUIDが一致する児童生徒が見つかりません。'
          return
        end

        ## 生徒が所属する学校をデータベースから取得する
        school = student_info.school

        ## 学校毎に分かれているFQDNを取得する
        to_domain = if school.student_domain
                      "#{school.student_domain}#{Rails.application.config.app_name[:student_domain]}"
                    end
        ## FQDNが無い場合、エラーをレスポンスする
        if to_domain.blank?
          render_err '学校のドメインが設定されていません。'
          return
        end
        ## アクセスしてきているURLのFQDNと学校のFQDNが違う場合、学校のFQDNに置換してPOST疑似リダイレクトする
        domain = request.headers["SERVER_NAME"]
        if domain != to_domain
          render html: Repost::Senpai.perform(
            "https://#{to_domain}:#{request.port}/api/auth/student_lti/callback",
            params: { utf8: params[:utf8], id_token: params[:id_token], state: params[:state], commit: params[:commit] }
          ).html_safe
          return
        end

        logger.info 'Sucessfully logged'
        logger.info "UUID: #{auth_hash['uid']}"
        ## 生徒アカウントのロック状態を確認する(認証失敗が規定回数を超える、または手動変更でアカウントがロックできる仕様)
        error = SessionController.check_lock student_info
        if error.present?
          ## ロックされている場合、エラーをレスポンスする
          render_err "ログインに失敗しました。\nError: #{error}"
        else
          ## そうでない場合、ログイン処理を行い、ログイン直後の画面へリダイレクトする
          SessionController.before_sign_in student_info, request
          bypass_sign_in student_info.student
          student_info.student.need_password_change = false
          student_info.student.save!
          redirect_to '/#/student'
        end
        # ---弊社独自領域ここまで
      end

      # omniauth_openid_connectによる処理(Request phase・Callback phase)中にエラーが発生した際にリダイレクトされることにより実行されるメソッド
      # エラーをレスポンスする
      def failure
        render_err "ログインに失敗しました。\nError: #{params[:message]}"
      end

      private

      # プラットフォームから返ってきた情報を取得する
      def auth_hash
        request.env['omniauth.auth']
      end

      CLAIM = 'https://purl.imsglobal.org/spec/lti/claim/'.freeze # 末尾スラッシュ有
      # omniauth_openid_connectではチェックできていないパラメータの入力チェックを行う
      def valid_lti_params
        # "sub"が空か無効値の場合、例外を発生する
        uid = auth_hash['uid']
        unless uid.present? && valid_uuid?(uid)
          raise InvalidLtiParam, { param_key: 'sub', param_value: uid }
        end

        # "iat"が空か0の場合、例外を発生する
        iat = auth_hash.extra.raw_info['iat']
        raise InvalidLtiParam, { param_key: 'iat', param_value: iat } if iat.blank? || iat.zero?

        # "message_type"が「LtiResourceLinkRequest」でない場合、例外を発生する
        message_type = auth_hash.extra.raw_info["#{CLAIM}message_type"]
        unless message_type == 'LtiResourceLinkRequest'
          raise InvalidLtiParam, { param_key: 'message_type', param_value: message_type }
        end

        # "version"が「1.3.0」でない場合、例外を発生する
        version = auth_hash.extra.raw_info["#{CLAIM}version"]
        raise InvalidLtiParam, { param_key: 'version', param_value: version } unless version == '1.3.0'

        # "roles"が空か無効値の場合、例外を発生する
        roles = auth_hash.extra.raw_info["#{CLAIM}roles"]
        raise InvalidLtiParam, { param_key: 'roles', param_value: roles } unless roles.present? && valid_roles?

        # "deployment_id"が空か無効値の場合、例外を発生する
        deployment_id = auth_hash.extra.raw_info["#{CLAIM}deployment_id"]
        unless deployment_id.present? && deployment_id.ascii_only? && deployment_id.length <= 255 &&
               deployment_id.start_with?('S_', 'B_', 'P_')
          raise InvalidLtiParam, { param_key: 'deployment_id', param_value: deployment_id }
        end

        # "context/id"が空の場合、例外を発生する
        context_id = auth_hash.extra.raw_info["#{CLAIM}context"]&.[]('id')
        unless context_id.present?
          raise InvalidLtiParam, { param_key: 'context.id', param_value: context_id }
        end

        # "resource_link/id"が空の場合、例外を発生する
        resource_link_id = auth_hash.extra.raw_info["#{CLAIM}resource_link"]&.[]('id')
        unless resource_link_id.present?
          raise InvalidLtiParam, { param_key: 'resource_link.id', param_value: resource_link_id }
        end

        # "target_link_uri"が空の場合、例外を発生する
        target_link_uri = auth_hash.extra.raw_info["#{CLAIM}target_link_uri"]
        unless target_link_uri.present?
          raise InvalidLtiParam, { param_key: 'target_link_uri', param_value: target_link_uri }
        end

        # "tool_platform"claimが存在し、かつ"tool_platform/guid"が空か無効値の場合、例外を発生する
        tool_platform = auth_hash.extra.raw_info["#{CLAIM}tool_platform"]
        if tool_platform.present?
          guid = tool_platform['guid']
          unless guid.present? && valid_uuid?(guid)
            raise InvalidLtiParam, { param_key: 'tool_platform.guid', param_value: guid }
          end
        end

        # "custom/grade"が空か無効値の場合、例外を発生する
        grade = auth_hash.extra.raw_info["#{CLAIM}custom"]&.[]('grade')
        unless grade.blank? || grade =~ /\A(P[1-6]|J[1-3]|H[1-3]|E[1-3])\z/i
          raise InvalidLtiParam, { param_key: 'custom.grade', param_value: grade }
        end
      end

      VOCAB_LIS = 'http://purl.imsglobal.org/vocab/lis/v2/'.freeze # 末尾スラッシュ有
      SYSTEM_ROLE = "#{VOCAB_LIS}system/person#".freeze # 末尾#有
      INSTITUTION_ROLE = "#{VOCAB_LIS}institution/person#".freeze # 末尾#有
      CONTEXT_ROLE = "#{VOCAB_LIS}membership#".freeze # 末尾#有
      CONTEXT_SUB_ROLE = "#{VOCAB_LIS}membership/".freeze # 末尾スラッシュ有
      ROLES = {
        # システムロール
        SYSTEM_ROLE => [
          'Administrator', 'None', # core
          'AccountAdmin', 'Creator', 'SysAdmin', 'SysSupport', 'User' # non-core
        ].freeze,
        # 教育機関ロール
        INSTITUTION_ROLE => [
          'Administrator', 'Faculty', 'Guest', 'None', 'Other', 'Staff', 'Student', # core
          'Alumni', 'Instructor', 'Learner', 'Member', 'Mentor', 'Observer', 'ProspectiveStudent' # non-core
        ].freeze,
        # コンテキストロール
        CONTEXT_ROLE => [
          'Administrator', 'ContentDeveloper', 'Instructor', 'Learner', 'Mentor', # core
          'Manager', 'Member', 'Officer' # non-core
        ].freeze,
        # コンテキストサブロール
        "#{CONTEXT_SUB_ROLE}Administrator#" => %w[
          Administrator Developer ExternalDeveloper ExternalSupport ExternalSystemAdministrator Support
          SystemAdministrator
        ].freeze,
        "#{CONTEXT_SUB_ROLE}ContentDeveloper#" => %w[
          ContentDeveloper ContentExpert ExternalContentExpert Librarian
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Instructor#" => %w[
          ExternalInstructor Grader GuestInstructor Lecturer PrimaryInstructor SecondaryInstructor TeachingAssistant
          TeachingAssistantGroup TeachingAssistantOffering TeachingAssistantSection TeachingAssistantSectionAssociation
          TeachingAssistantTemplate
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Learner#" => %w[
          ExternalLearner GuestLearner Instructor Learner NonCreditLearner
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Manager#" => %w[
          AreaManager CourseCoordinator ExternalObserver Manager Observer
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Member#" => %w[
          Member
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Mentor#" => %w[
          Advisor Auditor ExternalAdvisor ExternalAuditor ExternalLearningFacilitator ExternalMentor ExternalReviewer
          ExternalTutor LearningFacilitator Mentor Reviewer
        ].freeze,
        "#{CONTEXT_SUB_ROLE}Officer#" => %w[
          Chair Communications Secretary Treasurer Vice-Chair
        ].freeze
      }.freeze

      # "roles"が有効値かどうか判定する
      # @return 有効値: true/無効値: false
      def valid_roles?
        roles = auth_hash.extra.raw_info["#{CLAIM}roles"]
        # "roles"が空の場合、falseを返す
        return false if roles.blank?

        # "roles"にロール一覧に無い値が含まれる場合、falseを返す
        roles.each do |role|
          key = ROLES.keys.find { |k| role.start_with? k }
          return false if key.blank?

          return false unless ROLES[key].include?(role.delete_prefix(key))
        end
        # trueを返す
        true
      end

      # UUID(version4)として有効値かどうか判定する(有効値: true/無効値: false)
      # @param value 判定する値
      # @return 有効値: true/無効値: false
      def valid_uuid?(value)
        value =~ /\A[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}\z/i
      end

      # LTIパラメータ不正Error
      class InvalidLtiParam < StandardError
        attr_accessor :param_key, :param_value

        def initialize(data)
          super
          self.param_key = data[:param_key]
          self.param_value = data[:param_value]
        end

        def message
          "ログインに失敗しました。\nError: Invalid '#{param_key}' parameter"
        end
      end

      # 弊社独自領域ここから---
      ## 例外が発生した際に実行されるメソッド
      ## エラーをレスポンスする
      def render_500(e)
        logger.error "500 error #{e.message}"
        logger.error(e.backtrace.join("\n"))
        render_err e.message
      end
      # ---弊社独自領域ここまで
    end
  end
end
