from urllib.parse import urlparse
import os

# LTI1.3 liblary
from pylti1p3.contrib.flask import (
    FlaskOIDCLogin,
    FlaskMessageLaunch,
    FlaskRequest,
    FlaskCacheDataStorage,
)
from flask_caching import Cache
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.registration import Registration
from pylti1p3.exception import LtiException, OIDCException
from flask import Flask, request, render_template

# ここまで
import json


class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


app = Flask("lti", template_folder="templates")
config = {
    "DEBUG": True,
    "ENV": "development",
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 600,
    "SECRET_KEY": "replace-me",
    "SESSION_TYPE": "filesystem",
    "SESSION_COOKIE_NAME": "pylti1p3-flask-app-sessionid",
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SECURE": True,  # should be True in case of HTTPS usage (production)
    "SESSION_COOKIE_SAMESITE": None,  # should be 'None' in case of HTTPS usage (production)
    "DEBUG_TB_INTERCEPT_REDIRECTS": False,
}
app.config.from_mapping(config)
cache = Cache(app)
log = app.logger


class ExtendedFlaskMessageLaunch(FlaskMessageLaunch):
    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just skip nonce validation.
        """
        iss = self.get_iss()

        deep_link_launch = self.is_deep_link_launch()
        if (
            iss == "https://lti-ri.imsglobal.org"
            or "https://api.ltiorc.edustd.jp/platform/LT3GEJT5FN"
            and deep_link_launch
        ):
            return self
        return super().validate_nonce()


def get_domein_from_url(url):
    """
    URLからドメイン部分を取得する。
    Param URL
    Returns: ドメイン
    """
    try:
        domein = urlparse(url).hostname
        return domein
    except Exception:
        return None


def get_lti_config_path():
    """
    復号に必要なファイルの参照を行う
    Returns:
        config
    """
    return os.path.join(app.root_path, "lti-configs", "setting.json")


def get_launch_data_storage():
    """
    キャッシュを参照する
    Returns:
        cache
    """
    return FlaskCacheDataStorage(cache)


def get_jwk_from_public_key(key_name):
    """_summary_

    Args:
        key_name (_type_): str

    Returns:
        jwk:str
    """

    key_path = os.path.join(app.root_path, "lti-configs", key_name)
    f = open(key_path, "r")
    key_content = f.read()
    jwk = Registration.get_jwk(key_content)
    f.close()
    return jwk


@app.route("/login", methods=["POST", "GET"])
def oidc_login():
    """
    ログイン認証を行うメソッド
    retun oidc_login relult
    """
    try:

        tool_conf = ToolConfJsonFile(get_lti_config_path())
        launch_data_storage = get_launch_data_storage()
        flask_request = FlaskRequest()
        target_link_uri = flask_request.get_param("target_link_uri")
        if not target_link_uri:
            raise Exception('Missing "target_link_uri" param')
        """
        oidcログイン用にデータを加工する
        """
        oidc_login = FlaskOIDCLogin(
            flask_request, tool_conf, launch_data_storage=launch_data_storage
        )
        return oidc_login.enable_check_cookies().redirect(target_link_uri)

    except Exception as e:
        error = {"errorMessage": e}
        return render_template("false.html", **error)
    except OIDCException as e:
        error = {"errorMessage": e}
        return render_template("false.html", **error)
    except TypeError as e:
        error = {"errorMessage": "Invalid value"}
        return render_template("false.html", **error)


@app.route("/launch/", methods=["POST"])
def launch():
    """
    認証後に必要となるUR・Lメールアドレス・名前を返すメソッド
    こちらのパラメータを用いて設定を行う
    returm launch result
    """
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    """
    復号を行う
    """
    try:

        message_launch = ExtendedFlaskMessageLaunch(
            request=flask_request,
            tool_config=tool_conf,
            launch_data_storage=launch_data_storage,
        )
        message_launch_data = message_launch.get_launch_data()
        # メールアドレス委は必ず必要なため存在しない場合はバリでーションで落とす。)
        if message_launch_data.get("email") == None:
            raise LtiException("Email doesn't exist")
        if message_launch_data.get("sub") == None:
            raise LtiException("sub doesn't exist")
        # サンプルコード用本来であればここでデータベースト疎通を取る
        if (
            message_launch_data.get("sub")
            != json.load(open("sub.json", "r"))[message_launch_data.get("iss")]
        ):
            raise LtiException("Invalid sub")
        domein = get_domein_from_url(
            message_launch_data.get(
                "https://purl.imsglobal.org/spec/lti/claim/custom"
            ).get("url")
        )
        if domein == None:
            raise LtiException("Invalid URL")

    except LtiException as e:
        log.error(e)
        # バリデーションで落ちた場合エラーメッセージを返却する
        error = {"errorMessage": e}
        return render_template("false.html", **error)
    except TypeError as e:
        error = {"errorMessage": "Invalid value"}
        return render_template("false.html", **error)
    difficulty = message_launch_data.get(
        "https://purl.imsglobal.org/spec/lti/claim/custom", {}
    ).get("difficulty", None)
    if not difficulty:
        difficulty = request.args.get("difficulty", "normal")

    post_data = {
        "email": message_launch_data.get("email"),
        "name": message_launch_data.get("name"),
        "url": domein,
    }
    ##下にpostデータの送信先を記述する。サンプルコードには非公開
    # 独自関数

    return render_template("index.html", **post_data)


##ローカルテスト用
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
