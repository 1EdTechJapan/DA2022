/*
 * OneRosterCSV出力 ストアドプロシージャ
 *
 * 「OneRosterCSV項目定義書 JapanProfile v.1.2版」の出力仕様に則ったCSV出力用レコードを
 *  関連テーブルに作成する。
 *
 *   @in_nendo      int 出力対象年度
 *   @in_kijunDate  VARCHAR(8) 出力対象基準日 当日付時点で在籍している者を出力対象とする。
 */
DROP PROCEDURE IF EXISTS one.spCreateBulkCSV
GO

CREATE PROCEDURE one.spCreateBulkCSV
    @in_nendo int
   ,@in_kijunDate VARCHAR(8)
AS
BEGIN
    DECLARE @outputId UNIQUEIDENTIFIER = LOWER(NEWID());   --出力処理ID
    DECLARE @academicSessionSrcId UNIQUEIDENTIFIER;

DECLARE @STARTDATETIME_ALL datetime2 = SYSDATETIME();
DECLARE @STARTDATETIME datetime2;

    -- academicSessions レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateAcademicSessions
        @outputId, @in_nendo, @sourcedId = @academicSessionSrcId OUTPUT;

    -- orgs レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateOrgs
        @outputId, @in_nendo;

    -- courses レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateCourses
        @outputId, @in_nendo, @academicSessionSrcId;

    -- classes レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateClasses
        @outputId, @in_nendo, @academicSessionSrcId;

    -- users レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateUsers
        @outputId, @in_nendo, @academicSessionSrcId, @in_kijunDate;

    -- roles レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateRoles
        @outputId, @in_nendo;

    -- enrollments レコード追加
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateEnrollments
        @outputId, @in_nendo, @in_kijunDate;

    RETURN;
END;
