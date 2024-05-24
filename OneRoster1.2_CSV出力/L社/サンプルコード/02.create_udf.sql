/*
 * ������ϊ��ƃ_�u���N�H�[�e�[�V�����ɂ��G�X�P�[�v���s��
 *
 *   @val �����Ώۂ̒l
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
