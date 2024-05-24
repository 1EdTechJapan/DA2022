module OmniAuth
  module Strategies
    class StudentLti < OmniAuth::Strategies::OpenIDConnect
      # ���ГƎ��̈悱������---
      ## ��������"state"��Cookie�ɕۑ�����
      def new_state
        v = super
        response.set_cookie 'omniauth.state', { domain: cookie_domain, value: v, same_site: 'None', secure: true }
        v
      end

      ## session�܂���Cookie����ۑ�����Ă���"state"���擾���A
      ## �w�Z��FQDN(redirect_uri�ȊO��FQDN)�ŃA�N�Z�X���Ă��Ă���ꍇ�͕ۑ�����Ă���"state"���폜����
      def stored_state
        domain = @env["SERVER_NAME"]
        if domain == redirect_uri_domain
          session['omniauth.state']
        else
          v = super
          v ||= request.cookies['omniauth.state']
          response.delete_cookie 'omniauth.state'
          v
        end
      end

      ## ��������"nonce"��Cookie�ɕۑ�����
      def new_nonce
        v = super
        response.set_cookie 'omniauth.nonce', { domain: cookie_domain, value: v, same_site: 'None', secure: true }
        v
      end

      ## session�܂���Cookie����ۑ�����Ă���"nonce"���擾���A
      ## �w�Z��FQDN(redirect_uri�ȊO��FQDN)�ŃA�N�Z�X���Ă��Ă���ꍇ�͕ۑ�����Ă���"nonce"���폜����
      def stored_nonce
        domain = @env["SERVER_NAME"]
        if domain == redirect_uri_domain
          session['omniauth.nonce']
        else
          v = super
          v ||= request.cookies['omniauth.nonce']
          response.delete_cookie 'omniauth.nonce'
          v
        end
      end

      ## Rack::Response�I�u�W�F�N�g���擾����
      def response
        @response ||= Rack::Response.new
      end

      ## ���_�C���N�g����
      def redirect(uri)
        if options[:iframe]
          response.write("<script type='text/javascript' charset='utf-8'>top.location.href = '#{uri}';</script>")
        else
          response.write("Redirecting to #{uri}...")
          response.redirect(uri)
        end

        response.finish
      end

      ## redirect_uri��FQDN���擾����
      def redirect_uri_domain
        URI.parse(client_options.redirect_uri).host
      end

      ## cookie��domain�����Ɏw�肷��l���擾����
      def cookie_domain
        Rails.application.config.app_name[:student_domain]
      end
      # ���ГƎ��̈悱���܂�---
    end
  end
end
