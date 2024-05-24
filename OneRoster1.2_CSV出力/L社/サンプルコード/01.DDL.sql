-- Project Name : OneRoster CSV出力

SET NOCOUNT ON
GO

-- OneRoster academicSessions.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[academicSessions]
GO

CREATE TABLE [one].[academicSessions] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [title] nvarchar(10) NOT NULL
  , [type] varchar(20) NOT NULL
  , [startDate] date NOT NULL
  , [endDate] date NOT NULL
  , [parentSourcedId] uniqueidentifier
  , [schoolYear] varchar(4) NOT NULL
  , CONSTRAINT [one_academicSessions_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_academicSessions_IX1]
  ON [one].[academicSessions]([outputId])
GO

-- OneRoster classes.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[classes]
GO

CREATE TABLE [one].[classes] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [title] nvarchar(50) NOT NULL
  , [grades] varchar(2)
  , [courseSourcedId] uniqueidentifier NOT NULL
  , [classCode] varchar(10)
  , [classType] varchar(20) NOT NULL
  , [location] nvarchar(50)
  , [schoolSourcedId] uniqueidentifier NOT NULL
  , [termSourcedIds] uniqueidentifier NOT NULL
  , [subjects] nvarchar(20)
  , [subjectCodes] varchar(4)
  , [periods] varchar(20)
  , [resoureces] nvarchar(50)
  , [metadata_jp_specialNeeds] bit DEFAULT 0 NOT NULL
  , [clsno] varchar(6) NOT NULL
  , CONSTRAINT [one_classes_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_classes_IX1]
  ON [one].[classes]([outputId],[clsno])
GO

-- OneRoster courses.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[courses]
GO

CREATE TABLE [one].[courses] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [schoolYearSourcedId] uniqueidentifier
  , [title] nvarchar(50) NOT NULL
  , [courseCode] varchar(20)
  , [grades] varchar(2)
  , [orgSourcedId] uniqueidentifier NOT NULL
  , [subjects] nvarchar(20)
  , [subjectCodes] varchar(5)
  , [originGrade] varchar(2) NOT NULL
  , CONSTRAINT [one_courses_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_courses_IX1]
  ON [one].[courses]([outputId],[schoolYearSourcedId],[orgSourcedId],[originGrade])
GO

-- OneRoster enrollments.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[enrollments]
GO

CREATE TABLE [one].[enrollments] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [classSourcedId] uniqueidentifier NOT NULL
  , [schoolSourcedId] uniqueidentifier NOT NULL
  , [userSourcedId] uniqueidentifier NOT NULL
  , [role] varchar(20) NOT NULL
  , [primary] bit DEFAULT 0 NOT NULL
  , [beginDate] date
  , [endDate] date
  , [metadata_jp_shussekiNo] smallint
  , [metadata_jp_publicFlg] bit DEFAULT 1 NOT NULL
  , CONSTRAINT [one_enrollments_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_enrollments_IX1]
  ON [one].[enrollments]([outputId],[classSourcedId],[schoolSourcedId],[userSourcedId])
GO

-- OneRoster orgs.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[orgs]
GO

CREATE TABLE [one].[orgs] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [name] nvarchar(50) NOT NULL
  , [type] varchar(20) NOT NULL
  , [identifier] varchar(20)
  , [parentSourcedId] uniqueidentifier
  , [shozokuCode] varchar(8) NOT NULL
  , [sclkind] varchar(1) NOT NULL
  , CONSTRAINT [one_orgs_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_orgs_IX1]
  ON [one].[orgs]([outputId],[shozokuCode],[sclkind])
GO

-- OneRoster roles.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[roles]
GO

CREATE TABLE [one].[roles] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [userSourcedId] uniqueidentifier NOT NULL
  , [roleType] varchar(20) NOT NULL
  , [role] varchar(20) NOT NULL
  , [beginDate] date
  , [endDate] date
  , [orgSourcedId] uniqueidentifier NOT NULL
  , [userProfileSourcedId] uniqueidentifier
  , CONSTRAINT [one_roles_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_roles_IX1]
  ON [one].[roles]([outputId],[userSourcedId],[orgSourcedId],[userProfileSourcedId])
GO

-- OneRoster users.csvに出力する情報格納テーブル
DROP TABLE IF EXISTS [one].[users]
GO

CREATE TABLE [one].[users] (
  [outputId] uniqueidentifier NOT NULL
  , [sourcedId] uniqueidentifier NOT NULL
  , [status] varchar(20)
  , [dateLastModified] datetime2
  , [enabledUser] bit DEFAULT 1 NOT NULL
  , [username] varchar(100) NOT NULL
  , [userIds] varchar(50)
  , [givenName] nvarchar(100) NOT NULL
  , [familyName] nvarchar(100) NOT NULL
  , [middleName] nvarchar(100)
  , [identifier] varchar(50)
  , [email] varchar(254)
  , [sms] varchar(20)
  , [phone] varchar(20)
  , [agentSourcedIds] uniqueidentifier
  , [grades] varchar(2)
  , [password] varchar(200)
  , [userMasterIdentifier] uniqueidentifier
  , [resourceSourcedIds] varchar(20)
  , [preferredGivenName] nvarchar(100)
  , [preferredMiddleName] nvarchar(100)
  , [preferredFamilyName] nvarchar(100)
  , [primaryOrgSourcedId] uniqueidentifier
  , [pronouns] nvarchar(10)
  , [metadata_jp_kanaGivenName] nvarchar(100)
  , [metadata_jp_kanaFamilyName] nvarchar(100)
  , [metadata_jp_kanaMiddleName] nvarchar(100)
  , [metadata_jp_homeClass] uniqueidentifier
  , [datakind] varchar(20)
  , [kmUsercode] varchar(10)
  , CONSTRAINT [one_users_PKC] PRIMARY KEY ([sourcedId])
)
GO

CREATE INDEX [one_users_IX1]
  ON [one].[users]([outputId],[userMasterIdentifier],[primaryOrgSourcedId],[metadata_jp_homeClass],[datakind],[kmUsercode])
GO


SET NOCOUNT OFF
GO

