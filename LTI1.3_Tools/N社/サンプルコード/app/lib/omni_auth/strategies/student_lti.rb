module OmniAuth
  module Strategies
    class StudentLti < OmniAuth::Strategies::OpenIDConnect
      # 弊社独自領域ここから---
      ## 生成した"state"をCookieに保存する
      def new_state
        v = super
        response.set_cookie 'omniauth.state', { domain: cookie_domain, value: v, same_site: 'None', secure: true }
        v
      end

      ## sessionまたはCookieから保存されている"state"を取得し、
      ## 学校のFQDN(redirect_uri以外のFQDN)でアクセスしてきている場合は保存されている"state"を削除する
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

      ## 生成した"nonce"をCookieに保存する
      def new_nonce
        v = super
        response.set_cookie 'omniauth.nonce', { domain: cookie_domain, value: v, same_site: 'None', secure: true }
        v
      end

      ## sessionまたはCookieから保存されている"nonce"を取得し、
      ## 学校のFQDN(redirect_uri以外のFQDN)でアクセスしてきている場合は保存されている"nonce"を削除する
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

      ## Rack::Responseオブジェクトを取得する
      def response
        @response ||= Rack::Response.new
      end

      ## リダイレクトする
      def redirect(uri)
        if options[:iframe]
          response.write("<script type='text/javascript' charset='utf-8'>top.location.href = '#{uri}';</script>")
        else
          response.write("Redirecting to #{uri}...")
          response.redirect(uri)
        end

        response.finish
      end

      ## redirect_uriのFQDNを取得する
      def redirect_uri_domain
        URI.parse(client_options.redirect_uri).host
      end

      ## cookieのdomain属性に指定する値を取得する
      def cookie_domain
        Rails.application.config.app_name[:student_domain]
      end
      # 弊社独自領域ここまで---
    end
  end
end
