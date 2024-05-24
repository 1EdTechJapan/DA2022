/*
 * 文字列変換とダブルクォーテーションによるエスケープを行う
 *
 *   @val 処理対象の値
 */
DROP FUNCTION IF EXISTS one.ufnAddQuate
GO

CREATE FUNCTION one.ufnAddQuate (
    @val nvarchar(2000)
)
RETURNS nvarchar(2000)
AS
BEGIN
    IF @val IS NULL BEGIN
        RETURN '""'
    END

    RETURN '"' + REPLACE(@val,'"','""') + '"'

END

GO
