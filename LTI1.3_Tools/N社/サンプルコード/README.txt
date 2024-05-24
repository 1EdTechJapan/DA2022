■動作環境
下記で動作を確認しております。
　OS:Amazon Linux 2
　言語:Ruby(3.0.2)
　フレームワーク:Rails(6.1.4.1)

■使用ライブラリ
下記のライブラリを使用しております。
　omniauth_openid_connect　→メインで使用する、OIDCのためのライブラリです。
　　https://github.com/omniauth/omniauth_openid_connect
　omniauth-rails_csrf_protection　→omniauth_openid_connectの内部で使用されているomniauthで必要とされる、CSRF対策のためのライブラリです。
　　https://github.com/cookpad/omniauth-rails_csrf_protection
　repost　→POSTによる疑似リダイレクトのためのライブラリです。
　　https://github.com/vergilet/repost

下記をGemfileに追記し、「bundle install」を実行してください。
-----
gem 'omniauth_openid_connect'
gem 'omniauth-rails_csrf_protection'
gem 'repost'
-----

■実行準備
下記のような設定をconfig/environments/production.rbに追記してください。
-----
  config.app_name = {
    omniauth_options: [
      {
        name: 'student_lti',
        issuer: '<issuer>',

        scope: [:openid],

        response_type: :id_token,
        response_mode: :form_post,

        allow_authorize_params: [:lti_message_hint],

        prompt: :none,

        client_options: {
          scheme: 'https',
          host: '<プラットフォームのFQDN>',
          port: 443,

          identifier: '<client_id>',
          jwks_uri: '<プラットフォームのJWKS URL>',
          authorization_endpoint: '<OIDC AuthenticationエンドポイントURLのpath部分>',
          redirect_uri: 'https://<ツールのFQDN>/api/student/lti/implicit_back'
        }
      }
    ]
  }
-----

下記の設定をconfig/application.rbに追記してください。
-----
    config.autoload_paths += %W(#{config.root}/app/lib)
-----

下記のように設定をconfig/routes.rbに追記してください。
-----
Rails.application.routes.draw do
  scope :api do
    scope :student do
      post 'lti/implicit_back' => 'api/student/lti#implicit_back'
    end
    match 'auth/student_lti/callback', via: %i[get post], to: 'api/student/lti#launches'
    match 'auth/failure', via: %i[get post], to: 'api/student/lti#failure'
  end
end
-----