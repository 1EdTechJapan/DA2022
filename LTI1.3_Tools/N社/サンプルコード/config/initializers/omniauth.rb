if Rails.application.config.app_name[:omniauth_options].present?
  # config/environments/production.rb��"omniauth_options"�̐ݒ肪����ꍇ�AOmniAuth���~�h���E�F�A�Ƃ��Ēǉ�����
  Rails.application.config.middleware.use OmniAuth::Builder do
    require 'omni_auth/strategies/student_lti'

    configure do |config|
      # OmniAuth�֘A��URL��path��ύX����
      config.path_prefix = '/api/auth'

      # Request phase���̃p�����[�^�̓��̓`�F�b�N���s��
      config.request_validation_phase = proc do |env|
        params = Rack::Request.new(env).params

        # "iss"�E"login_hint"�E"target_link_uri"����̏ꍇ�A��O�𔭐�����
        %w[iss login_hint target_link_uri].each do |required_param|
          raise OmniAuth::AuthenticityError, "empty #{required_param}" if params[required_param].blank?
        end
      end
    end

    # provider�G���g���[��ǉ�����
    Rails.application.config.app_name[:omniauth_options].each do |omniauth_option|
      provider omniauth_option[:name].to_sym, omniauth_option
    end
  end

  # �G���[�������ɃG���[�ppath�փ��_�C���N�g����
  OmniAuth.config.on_failure = proc do |env|
    OmniAuth::FailureEndpoint.new(env).redirect_to_failure
  end
end
