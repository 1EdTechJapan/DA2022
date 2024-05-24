LTI v1.3 Core Tool

必要環境

ruby '3.2.0'


外部参照ファイル

gem 'rails', '~> 7.0.1'
gem 'jwt'
gem 'ros-apartment'
gem 'pg', '~> 1.4.4'
gem 'actionpack-action_caching'


機能

1. OIDC - Init Login リクエスト
  def login_with_lti_init

2. LTI - ResourceLinkRequest
  def login_with_lti_resource

