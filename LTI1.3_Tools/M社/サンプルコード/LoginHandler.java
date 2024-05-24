
import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;

import software.amazon.awssdk.http.HttpStatusCode;

/**
 * AWS Lambda 受信ハンドラクラス<br>
 * ログイン開始要求
 * 
 *
 */
public class LoginHandler extends BaseHandler<LoginDto>
	/* BaseHandlerは
	 * RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent>
	 * をインプリメントしています
	 *  */
{

  /**
   * ログイン開始要求
   */
  @Override
  public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent input, Context context)
  {

  	// 要求解析処理
  	LoginDto request = null;
  	try
  	{
  	  request = validate(input);
  	  if (request == null)
  	  {
		return response(HttpStatusCode.BAD_REQUEST, new ApplicationException( "The request is invalid."));
  	  }
  	}
	catch (ApplicationException e) {
            return response(HttpStatusCode.BAD_REQUEST, e);
	}
  	catch (Exception e)
  	{
	    return response(HttpStatusCode.INTERNAL_SERVER_ERROR, e);
  
  	}
  
  	// 認証要求生成処理
  	// 自社独自領域のため詳細は割愛
  	// セッション情報を生成し、認証要求クエリパラメータを生成する
  
  	// 認証要求リダイレクト処理
  	APIGatewayProxyResponseEvent output = new APIGatewayProxyResponseEvent();
	HashMap<String, String> headers = HttpUtility.setRedirectLocation({事前に連携されている認証要求先URL},
		{クエリパラメータ});
  
  	output.setStatusCode(HttpStatusCode.MOVED_TEMPORARILY);
  	output.setHeaders(headers);
  
  	return output;
  
  }

  /**
   * 入力パラメータ解析処理
   * 
     * @param input  Third-party initiated login クエリパラメータ
     * @return null : 失敗<br>
     *          上記以外 : 成功
     * @throws Exception 解析失敗
   */
   @Override
  protected LoginDto validate(Map<String, String> params)
  {
		// 自社独自領域のため詳細は割愛
		// 受信パラメータを検証する

		 return null;
  }

}
