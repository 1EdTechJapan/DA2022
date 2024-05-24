import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.Map;

/**
 * *****************************************************************************
 * OIDCログイン開始Serviceインタフェース
 *
 * <pre>
 * [機能説明]
 * 1.上記の通り
 * [注意事項]
 * (なし)
 * </pre>
 *****************************************************************************
 */
public interface OIDCService {

  /**
   * ***************************************************************************
   * OIDCログインを開始する
   * <pre>
   * [機能説明]
   * 1.上記の通り
   * [注意事項]
   * (なし)
   * </pre>
   *
   * @param oidcLoginInitiationDto OIDC認証用DTO
   * @return リダイレクト情報のmap
   ***************************************************************************
   */

  public Map<String, String> initiation(OIDCLoginInitiationDto oidcLoginInitiationDto)
      throws IOException, GeneralSecurityException;

}
