/*
 * OneRosterCSV�o�� �X�g�A�h�v���V�[�W��
 *
 * �uOneRosterCSV���ڒ�`�� JapanProfile v.1.2�Łv�̏o�͎d�l�ɑ�����CSV�o�͗p���R�[�h��
 *  �֘A�e�[�u���ɍ쐬����B
 *
 *   @in_nendo      int �o�͑Ώ۔N�x
 *   @in_kijunDate  VARCHAR(8) �o�͑Ώۊ�� �����t���_�ōݐЂ��Ă���҂��o�͑ΏۂƂ���B
 */
DROP PROCEDURE IF EXISTS one.spCreateBulkCSV
GO

CREATE PROCEDURE one.spCreateBulkCSV
    @in_nendo int
   ,@in_kijunDate VARCHAR(8)
AS
BEGIN
    DECLARE @outputId UNIQUEIDENTIFIER = LOWER(NEWID());   --�o�͏���ID
    DECLARE @academicSessionSrcId UNIQUEIDENTIFIER;

DECLARE @STARTDATETIME_ALL datetime2 = SYSDATETIME();
DECLARE @STARTDATETIME datetime2;

    -- academicSessions ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateAcademicSessions
        @outputId, @in_nendo, @sourcedId = @academicSessionSrcId OUTPUT;

    -- orgs ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateOrgs
        @outputId, @in_nendo;

    -- courses ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateCourses
        @outputId, @in_nendo, @academicSessionSrcId;

    -- classes ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateClasses
        @outputId, @in_nendo, @academicSessionSrcId;

    -- users ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateUsers
        @outputId, @in_nendo, @academicSessionSrcId, @in_kijunDate;

    -- roles ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateRoles
        @outputId, @in_nendo;

    -- enrollments ���R�[�h�ǉ�
SET @STARTDATETIME = SYSDATETIME()
    EXECUTE one.spCreateEnrollments
        @outputId, @in_nendo, @in_kijunDate;

    RETURN;
END;
