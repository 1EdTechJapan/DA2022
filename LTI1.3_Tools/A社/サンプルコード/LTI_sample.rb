require 'jwt'
require 'digest'
require "net/http"

###
# ユーザー認証を行い、認可トークンを発行する。
# 以下全て、Ruby on Rails 仕様に準拠しています。
class UsersController < ApplicationController
  UUID_PATTERN = /\A([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})\Z/
  UUID_VALID   = /\A([0-9a-f]{8})-([0-9a-f]{4})-([1-5][0-9a-f]{3})-([0-9a-f]{4})-([0-9a-f]{12})\Z/
  UUID_V4      = /\A([0-9a-f]{8})-([0-9a-f]{4})-([4][0-9a-f]{3})-([0-9a-f]{4})-([0-9a-f]{12})\Z/

  CLAIM = 'https://purl.imsglobal.org/spec/lti/claim'

  DRAFT_OPERATOR_ROLES = %w(
    http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper
  )

  TENANT_OPERATOR_ROLES = %w(
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor
    http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor
    http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor
  )

  TENANT_ADMIN_ROLES = %w(
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator
    http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator
  )

  LEARN_ROLES = %w(
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student
    http://purl.imsglobal.org/vocab/lis/v2/membership#Learner
    http://purl.imsglobal.org/vocab/lis/v2/membership#Member
  )

  DENY_ROLES = %w(
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#None
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other  
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent
    http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff
    http://purl.imsglobal.org/vocab/lis/v2/membership#Manager
    http://purl.imsglobal.org/vocab/lis/v2/membership#Officer
    http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin
    http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator
    http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator
    http://purl.imsglobal.org/vocab/lis/v2/system/person#None
    http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin
    http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport
    http://purl.imsglobal.org/vocab/lis/v2/system/person#User
  )

  ###
  # OIDC - Init Login リクエスト
  #
  def login_with_lti_init
    action, service_name, iss, login_hint, target_link_uri, client_id, lti_deployment_id, lti_message_hint, cid, page, * = params.values_at "action", "service_name", "iss", "login_hint", "target_link_uri", "client_id", "lti_deployment_id", "lti_message_hint", "cid", "page"

    # 学習eポータル事業者ごとのカスタマイズ設定値に切り替え
    Custom.setup! iss, service_name
    Custom['LTI1.3'] => init:, timeout:, redirect_uri:
    init => scope:, prompt:, response_mode:, response_type:


    raise NotFound unless [service_name, iss, login_hint, target_link_uri].all? &:present?
    
    # state, iss, および弊社独自拡張パラメーターを取り扱い
    state = SecureRandom.uuid
    nonce = SecureRandom.uuid

    set_bare_session({ service_name:, iss:, cid:, page: }, state, timeout)

    args = { state:, nonce:, scope:, prompt:, response_mode:, response_type:, client_id:, login_hint:, redirect_uri:, lti_message_hint: }

    # OIDC - 認証リクエスト
    redirect_to "#{target_link_uri}?#{args.to_query}", allow_other_host: true

  rescue NoMatchingPatternKeyError
    raise NotFound
  end

  ###
  # LTI - ResourceLinkRequest
  #
  def login_with_lti_resource
    action, service_name, state, id_token_code,* = params.values_at "action", "service_name", "state", "id_token"
    lti_init_service_name, lti_init_iss, cid, page  = del_bare_session(state).values_at('service_name', 'iss', 'cid', 'page')

    raise NotFound unless [state, lti_init_iss, id_token_code].all? &:present?

    # 学習eポータル事業者ごとのカスタマイズ設定値に切り替え
    Custom.setup! lti_init_iss, service_name
    timeout, saler_code, jwks_uri, jwt_key, algorithm, endpoint_uri,* = Custom['LTI1.3'].values_at :timeout, :saler, :jwks_uri, :jwt_key, :jwt_algorithm, :endpoint_uri

    id_token, jwk =
      case
      when jwt_key
        jwt_rsa = OpenSSL::PKey::RSA.new jwt_key
        JWT.decode(id_token_code, jwt_rsa, true, algorithm:)
      when jwks = LtiJob.jwks
        JWT.decode(id_token_code, nil, true, algorithms: [algorithm], jwks:)
      else
        raise JWT::VerificationError
      end

    iss, login_id, aud, exp, iat, nonce, email, display_name, bare_deployment_id, * = id_token.values_at(
      'iss',
      'sub',
      'aud',
      'exp',
      'iat',
      'nonce',
      'email',
      'name',
      'deployment_id'
    )
    message_type, version, lti_authority, deployment_id, lti_context, lti_resource_link, target_link_uri, lti_tool_platform, * = id_token.values_at(
      "#{CLAIM}/message_type",
      "#{CLAIM}/version",
      "#{CLAIM}/roles",
      "#{CLAIM}/deployment_id",
      "#{CLAIM}/context",
      "#{CLAIM}/resource_link",
      "#{CLAIM}/target_link_uri",
      "#{CLAIM}/tool_platform"
    )
    
    nonce_key = "#{nonce}:#{exp}"
    if get_bare_session(nonce_key).empty?
      set_bare_session({ exp:, iat: }, nonce_key, timeout)
    else
      raise BadRequest
    end

    # message_type, version による処理の切り分け。
    case [message_type, version]
    in ['LtiResourceLinkRequest', '1.3.0']
      # initLoginリクエストと継続したリクエストであること。
      raise BadRequest unless [service_name, iss] == [lti_init_service_name, lti_init_iss]

      # 学校コードのフォーマットでなくてはならない。
      if deployment_id && deployment_id[/^S_/]
        school_code = deployment_id[2..]
        combined_school_code = "#{saler_code}::#{school_code}"

        # 必須項目の存在を確認
        raise NotFound unless [
          iss, exp, iat, nonce, target_link_uri, message_type, version, lti_authority,
          aud,
          lti_context,
          lti_resource_link,
        ].all? &:present?

        # 必須項目の存在を確認（詳細）
        raise NotFound unless [
          aud.filter {|s| s.present? }
          lti_context['id'],
          lti_resource_link['id'],
        ].all? &:present?

        # 必須項目の形式チェック
        raise Forbidden unless UUID_V4 === lti_tool_platform['guid']

        # 事業者との契約を確認しています。
        # ...
        sales_contract = # 独自仕様部分となるので、割愛します。
        raise NotAcceptable, "sales_contract by #{combined_school_code} not found" if sales_contract.blank?

        roles = # 独自仕様部分となるので、割愛します。
        raise NotAcceptable, "role not found" if roles.blank?

      else
        raise NotAcceptable, "deployment_id not found"
      end
    else
      # 独自仕様部分となるので、割愛します。
      # ...
    end

    # 利用者を特定します。（匿名での利用は行っていません。）
    @user = User.find_or_initialize_by(login_id:)
    # 独自仕様部分となるので、割愛します。

    # CLAIM roles に基づいて権限設定値を振り分けます。
    is_larning = (LEARN_ROLES & lti_authority).present?
    @user.is_tenant_admin = (TENANT_ADMIN_ROLES & lti_authority).present?
    @user.is_tenant_operator = (TENANT_OPERATOR_ROLES & lti_authority).present?
    @user.is_draft_operator = (DRAFT_OPERATOR_ROLES & lti_authority).present?

    # 当ツールで認可しないロールについて
    raise Forbidden if (DENY_ROLES & lti_authority).present?
    # 認可対象のロールでなく、認可しないロールにも該当しないような異常値について
    raise BadRequest unless is_larning || @user.is_tenant_admin || @user.is_tenant_operator || @user.is_draft_operator

    @user.save!
    @old_role_ids = @user.role_ids

    @user.roles = roles

    token = create_session(@user, state)

    args = {JWT: token}
    args = args.merge(cid:, page:) if cid

    redirect_to "#{endpoint_uri}?#{args.to_query}", allow_other_host: true
  end


  private

  def set_bare_session(value, session_id, timeout = Settings.redis.timeout)
    REDIS.mapped_hmset(session_id, value)
    REDIS.expire(session_id, timeout)
  end

  # セッションに値を記録し、認可トークンを発行します。
  def create_session(user, session_id = SecureRandom.uuid)
    service_name = params["service_name"]
    device_id = params[:device_id] || ''

    payload, jwt_key, algorithm,* = Custom['Session'].values_at :payload, :jwt_key, :jwt_algorithm

    payload = payload.merge(
      sub: user.id,
      session_id:,
      # 独自仕様部分となるので、割愛します。
    )
    payload[:is_service_admin] = true if user.service_admin?
    payload[:is_tenant_admin]   = true if user.tenant_admin?
    payload[:is_tenant_operator] = true if user.tenant_operator?
    payload[:is_draft_operator] = true if user.draft_operator?
    set_bare_session # 独自仕様部分となるので、割愛します。

    JWT.encode payload, jwt_key, algorithm
  end
end