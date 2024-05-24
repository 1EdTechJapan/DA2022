using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Web.UI.WebControls;
using Microsoft.VisualBasic.FileIO;
using MongoDB.Bson;
using MongoDB.Bson.Serialization;
using MongoDB.Driver;

namespace OneRosterCSV
{
    public partial class Start : System.Web.UI.Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {
        }

        /// <summary>
        /// 校務支援システムのデータをmongodbへ変換
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        protected void ButtonKoumuToOneRoster_Click(object sender, EventArgs e)
        {
            // REST用のコレクションにデータを変換(CSV用はREST用をベースに再変換する)
            ProprietaryConverter p = new ProprietaryConverter();
            p.ToMongodbProprietary();
            // p.ToMongodbSample();
        }

        #region OneRosterCSVメイン

        private struct OneRosterDataCount
        {
            public int academicSessions;
            public int classes;
            public int courses;
            public int demographics;
            public int enrollments;
            public int orgs;
            public int users;
            public int roles;
            public int userProfile;
        }

        /// <summary>
        /// OneRosterCSVのzipファイルをダウンロード
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        protected void ButtonOneRosterCSVDownload_Click(object sender, EventArgs e)
        {
            // REST用のコレクションからヘッダなどを合わせたCSV用のコレクションを作成しCSV出力
            OneRosterDataCount c = new OneRosterDataCount();
            c.academicSessions = createAcademicSessions();
            c.classes = createClasses();
            c.courses = createCourses();
            c.demographics = createDemographics();
            c.enrollments = createEnrollments();
            c.orgs = createOrgs();
            c.users = createUsers();
            c.roles = createRoles();
            c.userProfile = createUserProfiles();

            // データ件数に応じてmanifest作成しCSV出力
            createManifest(c);

            // ZIPに圧縮しダウンロードする
            downloadOneRosterCSV(c);
        }

        #endregion

        #region manifest.csv出力

        /// <summary>
        /// OneRosterCSVのmanifestを出力
        /// </summary>
        private void createManifest(OneRosterDataCount c)
        {
            // データ数に応じてファイルのvalueをbulkかabsentに設定したcsv_manifestを作成しcsv出力
            List<Models.Manifest.Manifest> manifests = new List<Models.Manifest.Manifest>();
            manifests.Add(new Models.Manifest.Manifest { propertyName = "manifest.version", value = "1.0" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "oneroster.version", value = "1.2" });

            if (c.academicSessions > 0)
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.academicSessions", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.academicSessions", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.categories", value = "absent" });

            if (c.classes > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.classes", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.classes", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.classResources", value = "absent" });

            if (c.courses > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.courses", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.courses", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.courseResources", value = "absent" });

            if (c.demographics > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.demographics", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.demographics", value = "absent" });
            }

            if (c.enrollments > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.enrollments", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.enrollments", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.lineItemLearningObjectiveIds", value = "absent" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.lineItems", value = "absent" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.lineItemScoreScales", value = "absent" });

            if (c.orgs > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.orgs", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.orgs", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.resources", value = "absent" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.resultLearningObjectiveIds", value = "absent" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.results", value = "absent" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.resultScoreScales", value = "absent" });

            if (c.roles > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.roles", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.roles", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.scoreScales", value = "absent" });

            if (c.userProfile > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.userProfiles", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.userProfiles", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "file.userResources", value = "absent" });

            if (c.users > 0)
            {
                // 想定値
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.users", value = "bulk" });
            }
            else
            {
                manifests.Add(new Models.Manifest.Manifest { propertyName = "file.users", value = "absent" });
            }

            manifests.Add(new Models.Manifest.Manifest { propertyName = "source.systemName", value = "dummySystemName" });
            manifests.Add(new Models.Manifest.Manifest { propertyName = "source.systemCode", value = "dummySystemCode" });


            // mongodbに格納
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);

            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Manifest.Manifest>("csv_manifest").DeleteMany("{}");

            // コレクションのデータを再設定
            foreach (var item in manifests)
            {
                var document = BsonSerializer.Deserialize<BsonDocument>(item.ToJson());
                var collection = database.GetCollection<BsonDocument>("csv_manifest");
                collection.InsertOne(document);
            }


            // csv出力
            csvExport("manifest", "csv_manifest", "propertyName,value");
        }

        #endregion

        #region academicSessions.csv出力

        /// <summary>
        /// OneRosterCSVのacademicSessionsを出力
        /// </summary>
        private int createAcademicSessions()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.AcademicSession.Academicsession>("csv_academicSessions").DeleteMany("{}");


            // csv-rest変更なし
            PipelineDefinition<OneRosterCSV.Models.AcademicSession.Academicsession, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "title", "$title" },
                                    { "type", "$type" },
                                    { "startDate", "$startDate" },
                                    { "endDate", "$endDate" },
                                    { "schoolYear", "$schoolYear" }
                                }),
                            new BsonDocument("$out", "csv_academicSessions"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.AcademicSession.Academicsession>("rest_academicSessions").Aggregate(pipeline);

            // csv出力
            csvExport("academicSessions", "csv_academicSessions", "sourcedId,status,dateLastModified,title,type,startDate,endDate,parentSourcedId,schoolYear");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region classes.csv出力

        /// <summary>
        /// OneRosterCSVのclassesを出力
        /// </summary>
        private int createClasses()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Class.Class1>("csv_classes").DeleteMany("{}");

            var gradeArrayJoin = new BsonDocument("$reduce",
                new BsonDocument {
                    { "input", "$grades" },
                    { "initialValue", "" },
                    { "in", new BsonDocument("$concat",
                    new BsonArray
                    {
                        "$$value",
                        new BsonDocument("$cond",
                        new BsonArray
                        {
                            new BsonDocument("$eq",
                            new BsonArray
                            {
                                "$$value",
                                ""
                            }),
                            "",
                            ","
                        }),
                        "$$this"
                    })
                    }
                });

            var termArrayJoin = new BsonDocument("$reduce",
                new BsonDocument {
                    { "input", "$terms.sourcedId" },
                    { "initialValue", "" },
                    { "in", new BsonDocument("$concat",
                    new BsonArray
                    {
                        "$$value",
                        new BsonDocument("$cond",
                        new BsonArray
                        {
                            new BsonDocument("$eq",
                            new BsonArray
                            {
                                "$$value",
                                ""
                            }),
                            "",
                            ","
                        }),
                        "$$this"
                    })
                    }
                });

            // course.sourcedId -> courseSourcedId
            // school.sourcedId -> schoolSourcedId
            // terms[].sourcedId -> termSourcedId
            PipelineDefinition<OneRosterCSV.Models.Class.Class1, BsonDocument> pipeline = new BsonDocument[]
            {
                new BsonDocument("$project",
                    new BsonDocument
                    {
                        { "_id", "$_id" },
                        { "sourcedId", "$sourcedId" },
                        { "title", "$title" },
                        { "grades", gradeArrayJoin },
                        { "courseSourcedId", "$course.sourcedId" },
                        { "classType", "$classType" },
                        { "schoolSourcedId", "$school.sourcedId" },
                        { "metadataJpSpecialNeeds", "$metadata.jp.specialNeeds" },
                        { "termSourcedIds", termArrayJoin }
                    }),
                new BsonDocument("$out", "csv_classes"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.Class.Class1>("rest_classes").Aggregate(pipeline);

            // csv出力
            csvExport("classes", "csv_classes", "sourcedId,status,dateLastModified,title,grades,courseSourcedId,classCode,classType,location,schoolSourcedId,termSourcedIds,subjects,subjectCodes,periods,metadata.jp.specialNeeds");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region courses.csv出力

        /// <summary>
        /// OneRosterCSVのcoursesを出力
        /// </summary>
        private int createCourses()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Course.Cours>("csv_courses").DeleteMany("{}");

            var gradeArrayJoin = new BsonDocument("$reduce",
                new BsonDocument {
                    { "input", "$grades" },
                    { "initialValue", "" },
                    { "in", new BsonDocument("$concat",
                    new BsonArray
                    {
                        "$$value",
                        new BsonDocument("$cond",
                        new BsonArray
                        {
                            new BsonDocument("$eq",
                            new BsonArray
                            {
                                "$$value",
                                ""
                            }),
                            "",
                            ","
                        }),
                        "$$this"
                    })
                }
            });

            // org.sourcedId -> orgSourcedId
            PipelineDefinition<OneRosterCSV.Models.Course.Cours, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "title", "$title" },
                                    { "grades", gradeArrayJoin },
                                    { "orgSourcedId", "$org.sourcedId" }
                                }),
                            new BsonDocument("$out", "csv_courses"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.Course.Cours>("rest_courses").Aggregate(pipeline);

            // csv出力
            csvExport("courses", "csv_courses", "sourcedId,status,dateLastModified,schoolYearSourcedId,title,courseCode,grades,orgSourcedId,subjects,subjectCodes");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region demographics.csv出力

        /// <summary>
        /// OneRosterCSVのdemographicsを出力
        /// </summary>
        private int createDemographics()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Demographic.Demographic>("csv_demographics").DeleteMany("{}");


            // csv-rest変更なし
            PipelineDefinition<OneRosterCSV.Models.Demographic.Demographic, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "birthDate", "$birthDate" },
                                    { "sex", "$sex" }
                                }),
                            new BsonDocument("$out", "csv_demographics"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.Demographic.Demographic>("rest_demographics").Aggregate(pipeline);

            // csv出力
            csvExport("demographics", "csv_demographics", "sourcedId,status,dateLastModified,birthDate,sex,americanIndianOrAlaskaNative,asian,blackOrAfricanAmerican,nativeHawaiianOrOtherPacificIslander,white,demographicRaceTwoOrMoreRaces,hispanicOrLatinoEthnicity,countryOfBirthCode,stateOfBirthAbbreviation,cityOfBirth,publicSchoolResidenceStatus");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region enrollments.csv出力

        /// <summary>
        /// OneRosterCSVのenrollmentsを出力
        /// </summary>
        private int createEnrollments()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Enrollment.Enrollment>("csv_enrollments").DeleteMany("{}");


            // class.sourcedId-> classSourcedId,
            // school.sourcedId -> schoolSourcedId
            // user.sourcedId -> userSourcedId
            PipelineDefinition<OneRosterCSV.Models.Enrollment.Enrollment, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "classSourcedId", "$class.sourcedId" },
                                    { "schoolSourcedId", "$school.sourcedId" },
                                    { "userSourcedId", "$user.sourcedId" },
                                    { "role", "$role" },
                                    { "primary", "$primary" },
                                    { "metadata.jp.ShussekiNo", "$metadata.jp.ShussekiNo" },
                                    { "metadata.jp.PublicFlg", "$metadata.jp.PublicFlg" }
                                }),
                            new BsonDocument("$out", "csv_enrollments"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.Enrollment.Enrollment>("rest_enrollments").Aggregate(pipeline);

            // csv出力
            csvExport("enrollments", "csv_enrollments", "sourcedId,status,dateLastModified,classSourcedId,schoolSourcedId,userSourcedId,role,primary,beginDate,endDate,metadata.jp.ShussekiNo,metadata.jp.PublicFlg");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region orgs.csv出力

        /// <summary>
        /// OneRosterCSVのorgsを出力
        /// </summary>
        private int createOrgs()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.Org.Org>("csv_orgs").DeleteMany("{}");


            // csv-rest変更なし
            PipelineDefinition<OneRosterCSV.Models.Org.Org, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "name", "$name" },
                                    { "type", "$type" },
                                    { "parentSourcedId", "$parent.sourcedId" }
                                }),
                            new BsonDocument("$out", "csv_orgs"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.Org.Org>("rest_orgs").Aggregate(pipeline);

            // csv出力
            csvExport("orgs", "csv_orgs", "sourcedId,status,dateLastModified,name,type,identifier,parentSourcedId");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region users.csv出力

        /// <summary>
        /// OneRosterCSVのusersを出力
        /// </summary>
        private int createUsers()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.User.User>("csv_users").DeleteMany("{}");


            // primaryOrg.sourcedId -> primaryOrgSourcedId
            // preferredFirstName -> preferredGivenName
            // preferredLastName -> preferredFamilyName
            PipelineDefinition<OneRosterCSV.Models.User.User, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "_id", "$_id" },
                                    { "sourcedId", "$sourcedId" },
                                    { "enabledUser", "$enabledUser" },
                                    { "username", "$username" },
                                    { "givenName", "$givenName" },
                                    { "familyName", "$familyName" },
                                    { "userMasterIdentifier", "$userMasterIdentifier" },
                                    { "preferredGivenName", "$preferredFirstName" },
                                    { "preferredFamilyName", "$preferredLastName" },
                                    { "primaryOrgSourcedId", "$primaryOrg.sourcedId" },
                                    { "metadata.jp.kanaGivenName", "$metadata.jp.kanaGivenName" },
                                    { "metadata.jp.kanaFamilyName", "$metadata.jp.kanaFamilyName" },
                                    { "metadata.jp.kanaMiddleName", "$metadata.jp.kanaMiddleName" },
                                    { "metadata.jp.homeClass", "$metadata.jp.homeClass" }
                                }),
                            new BsonDocument("$out", "csv_users"),
            };

            var result = database.GetCollection<OneRosterCSV.Models.User.User>("rest_users").Aggregate(pipeline);

            // csv出力
            csvExport("users", "csv_users", "sourcedId,status,dateLastModified,enabledUser,username,userIds,givenName,familyName,middleName,identifier,email,sms,phone,agentSourcedIds,grades,password,userMasterIdentifier,resourceSourcedIds,preferredGivenName,preferredMiddleName,preferredFamilyName,primaryOrgSourcedId,pronouns,metadata.jp.kanaGivenName,metadata.jp.kanaFamilyName,metadata.jp.kanaMiddleName,metadata.jp.homeClass");

            // 件数を返す
            return result.ToList().Count;
        }

        #endregion

        #region roles.csv出力

        /// <summary>
        /// OneRosterCSVのrolesを出力
        /// </summary>
        private int createRoles()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.User.User>("csv_roles").DeleteMany("{}");


            // users から作成
            PipelineDefinition<OneRosterCSV.Models.User.User, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$unwind", "$roles"),
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "sourcedId", "dummyguid" },
                                    { "userSourcedId", "$sourcedId" },
                                    { "roleType", "$roles.roleType" },
                                    { "role", "$roles.role" },
                                    { "orgSourcedId", "$roles.org.sourcedId" }
                                }),
                            new BsonDocument("$out", "csv_roles"),
            };

            var listId = database.GetCollection<OneRosterCSV.Models.User.User>("rest_users").Aggregate(pipeline).ToList();


            // GUIDを生成
            var csvCollection = database.GetCollection<dynamic>("csv_roles");

            foreach (BsonDocument i in listId)
            {
                csvCollection.UpdateOne(new BsonDocument("_id", i.GetValue("_id").AsObjectId),
                    new BsonDocument("$set",
                        new BsonDocument
                        {
                            { "sourcedId", Guid.NewGuid().ToString() }
                        }
                    )
                );
            }


            // csv出力
            csvExport("roles", "csv_roles", "sourcedId,status,dateLastModified,userSourcedId,roleType,role,beginDate,endDate,orgSourcedId,userProfileSourcedId");

            // 件数を返す
            return listId.Count;
        }

        #endregion

        #region userProfiles.csv出力

        /// <summary>
        /// OneRosterCSVのuserProfileを出力
        /// </summary>
        private int createUserProfiles()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);


            // コレクションのデータを削除
            database.GetCollection<OneRosterCSV.Models.User.User>("csv_userProfile").DeleteMany("{}");


            // users から作成
            PipelineDefinition<OneRosterCSV.Models.User.User, BsonDocument> pipeline = new BsonDocument[]
            {
                            new BsonDocument("$unwind", "$userProfiles"),
                            new BsonDocument("$unwind", "$userProfiles.credentials"),
                            new BsonDocument("$project",
                                new BsonDocument
                                {
                                    { "sourcedId", Guid.NewGuid().ToString() },
                                    { "userSourcedId", "$sourcedId" },
                                    { "profileType", "$userProfiles.profileType" },
                                    { "vendorId", "$userProfiles.vendorId" },
                                    { "credentialType", "$userProfiles.credentials.type" },
                                    { "username", "$userProfiles.credentials.username" }
                                }),
                            new BsonDocument("$out", "csv_userProfiles"),
            };

            var listId = database.GetCollection<OneRosterCSV.Models.User.User>("rest_users").Aggregate(pipeline).ToList();


            // GUIDを生成
            var csvCollection = database.GetCollection<dynamic>("csv_userProfiles");

            foreach (BsonDocument i in listId)
            {
                csvCollection.UpdateOne(new BsonDocument("_id", i.GetValue("_id").AsObjectId),
                    new BsonDocument("$set",
                        new BsonDocument
                        {
                            { "sourcedId", Guid.NewGuid().ToString() }
                        }
                    )
                );
            }

            // csv出力
            csvExport("userProfiles", "csv_userProfiles", "sourcedId,status,dateLastModified,userSourcedId,profileType,vendorId,applicationId,description,credentialType,username,password");

            // 件数を返す
            return listId.Count;
        }

        #endregion

        #region zipに圧縮しダウンロード

        /// <summary>
        /// OneRosterCSVを圧縮したZIPファイルをダウンロード
        /// </summary>
        private void downloadOneRosterCSV(OneRosterDataCount c)
        {
            // 出力するZIPファイルのファイル名は、以下のルールに従って命名する。

            //・RO_YYYYMMDD_[学校コード または 学校設置者コード].zip
            //　※RO：名簿情報(Roster)であることを示す文字列
            //　※YYYYMMDD：名簿情報がいつの時点での状態なのかを表す日付
            //　※私立学校にて、学校設置者コードの代わりに法人コードを使用することは許容しない

            //　※例：
            //　2023年4月4日時点の北海道の全データを出力
            //　→　RO_20230404_01.zip

            //　2023年4月4日時点の秋田市の全データを出力
            //　→　RO_20230404_052019.zip

            //　2023年4月4日時点の東京都江戸川区の全データを出力
            //　→　RO_20230404_131237.zip

            //　2023年4月4日時点の大阪市立滝川小学校の全データを出力
            //　→　RO_20230404_B127210000018.zip

            //学校コード：
            // https://edu-data.jp/
            //教育委員会コード：
            // https://edu-data.jp/eb

            ProprietaryConverter p = new ProprietaryConverter();
            string filename = p.GetJapanZipFilename();
            string zipped = Global.csvPath + filename;
            System.IO.File.Delete(zipped);

            using (var z = ZipFile.Open(zipped, ZipArchiveMode.Create))
            {
                z.CreateEntryFromFile(Global.csvPath + @"manifest.csv", "manifest.csv", CompressionLevel.Optimal);

                if (c.academicSessions > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"academicSessions.csv", "academicSessions.csv", CompressionLevel.Optimal);
                }

                if (c.classes > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"classes.csv", "classes.csv", CompressionLevel.Optimal);
                }

                if (c.courses > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"courses.csv", "courses.csv", CompressionLevel.Optimal);
                }

                if (c.demographics > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"demographics.csv", "demographics.csv", CompressionLevel.Optimal);
                }

                if (c.enrollments > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"enrollments.csv", "enrollments.csv", CompressionLevel.Optimal);
                }

                if (c.orgs > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"orgs.csv", "orgs.csv", CompressionLevel.Optimal);
                }

                if (c.roles > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"roles.csv", "roles.csv", CompressionLevel.Optimal);
                }

                if (c.userProfile > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"userProfiles.csv", "userProfiles.csv", CompressionLevel.Optimal);
                }

                if (c.users > 0)
                {
                    z.CreateEntryFromFile(Global.csvPath + @"users.csv", "users.csv", CompressionLevel.Optimal);
                }
            }

            // ダウンロード
            Response.Clear();
            Response.ContentType = "application/octet-stream";
            Response.Charset = string.Empty;
            Response.AddHeader("Cache-Control", "public");
            Response.AddHeader("Pragma", "public");
            Response.AddHeader("Content-Disposition", "attachment; filename*=UTF-8''" + Server.UrlEncode(filename));
            FileInfo fileInfo = new FileInfo(zipped);
            Response.AddHeader("Content-Length", fileInfo.Length.ToString());
            Response.Flush();
            Response.TransmitFile(zipped);
            Response.End();
        }

        #endregion

        #region mongodbからcsv出力

        /// <summary>
        /// mongodbからcsv出力
        /// </summary>
        /// <param name="filename"></param>
        /// <param name="collection"></param>
        /// <param name="fields"></param>
        private void csvExport(string filename, string collection, string fields)
        {
            string mongoOutpath = Global.csvPath + filename + @".csv.mongo";
            string japanOutpath = Global.csvPath + filename + @".csv";

            //BOM無しのUTF8
            System.Text.Encoding csvEncoding = new System.Text.UTF8Encoding(false);

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = Global.mongoexport;
            startInfo.Arguments = "--host=\"" + Global.mongodbHost + "\" --collection=" + collection + " --db=" + Global.mongodbDatabase + " --type=\"csv\" --out=\"" + mongoOutpath + "\" --fields=\"" + fields + "\"";
            startInfo.UseShellExecute = false;

            Process exportProcess = new Process();
            exportProcess.StartInfo = startInfo;

            exportProcess.Start();
            exportProcess.WaitForExit();


            // 学習eポータル標準モデル
            // ・sourcedIdの英字は小文字である必要がある。
            // ・すべての要素をダブルクオーテーションで囲む必要がある。
            // ・改行コードはCR-LFとなる必要がある。

            // mongoexport で対応できない処理を実施。ここではダブルクオーテーションで囲むことを処理。
            using (TextFieldParser parser = new TextFieldParser(mongoOutpath, csvEncoding))
            {
                parser.TextFieldType = FieldType.Delimited;
                parser.SetDelimiters(","); // 区切り文字はコンマ

                parser.HasFieldsEnclosedInQuotes = true;
                parser.TrimWhiteSpace = false;

                int rowNo = 0;

                // 書き込むファイル
                using (System.IO.StreamWriter sr = new System.IO.StreamWriter(japanOutpath, false, csvEncoding))
                {
                    while (!parser.EndOfData)
                    {
                        string[] row = parser.ReadFields(); // 1行読み込み

                        // ヘッダはスキップ
                        rowNo++;
                        if (rowNo == 1)
                        {
                            for (int i = 0; i <= row.Length - 1; i++)
                            {
                                sr.Write(row[i]);

                                if (i < row.Length - 1)
                                {
                                    sr.Write(",");
                                }
                            }
                            sr.Write("\n");
                            continue;
                        }

                        // データをすべてダブルクオーテーションで囲む
                        for (int i = 0; i <= row.Length - 1; i++)
                        {
                            string field = row[i];

                            if (field.IndexOf('"') > -1)
                            {
                                //"を""とする
                                field = field.Replace("\"", "\"\"");
                            }

                            sr.Write("\"" + field + "\"");

                            if (i < row.Length - 1)
                            {
                                sr.Write(",");
                            }
                        }
                        sr.Write("\n");
                    }
                }
            }
        }

        #endregion

    }
}