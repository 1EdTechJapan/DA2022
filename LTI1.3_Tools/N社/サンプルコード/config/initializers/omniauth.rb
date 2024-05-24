if Rails.application.config.app_name[:omniauth_options].present?
  # config/environments/production.rbに"omniauth_options"の設定がある場合、OmniAuthをミドルウェアとして追加する
  Rails.application.config.middleware.use OmniAuth::Builder do
    require 'omni_auth/strategies/student_lti'

    configure do |config|
      # OmniAuth関連のURLのpathを変更する
      config.path_prefix = '/api/auth'

      # Request phase時のパラメータの入力チェックを行う
      config.request_validation_phase = proc do |env|
        params = Rack::Request.new(env).params

        # "iss"・"login_hint"・"target_link_uri"が空の場合、例外を発生する
        %w[iss login_hint target_link_uri].each do |required_param|
          raise OmniAuth::AuthenticityError, "empty #{required_param}" if params[required_param].blank?
        end
      end
    end

    # providerエントリーを追加する
    Rails.application.config.app_name[:omniauth_options].each do |omniauth_option|
      provider omniauth_option[:name].to_sym, omniauth_option
    end
  end

  # エラー発生時にエラー用pathへリダイレクトする
  OmniAuth.config.on_failure = proc do |env|
    OmniAuth::FailureEndpoint.new(env).redirect_to_failure
  end
end
