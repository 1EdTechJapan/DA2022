using EduKoumu.OneRosterService.DataTypes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace EduKoumu.OneRosterService.Utils
{
    public class GUIDRefDTypeHelper
    {
        public static GUIDRefDType GetGUIDRefDType(GUIDRefTypeEnum type, Guid? sourcedId)
        {
            if (sourcedId == null)
            {
                return null;
            }

            return new GUIDRefDType
            {
                Href = new Uri(GetBaseUrl() + GetTypePluralNoun(type) + "/" + sourcedId.ToString()),
                SourcedId = sourcedId.ToString(),
                Type = type,
            };
        }

        public static List<GUIDRefDType> GetGUIDRefDTypeList(GUIDRefTypeEnum type, Guid[] sourcedIds)
        {
            return sourcedIds.Select(x => GetGUIDRefDType(type, x)).ToList();
        }

        // https://www.sensibledev.com/how-to-get-the-base-url-in-asp-net/
        public static string GetBaseUrl()
        {
            var request = HttpContext.Current.Request;
            var appRootFolder = request.ApplicationPath;

            if (!appRootFolder.EndsWith("/"))
            {
                appRootFolder += "/";
            }

            return string.Format(
                "{0}://{1}{2}{3}/",
                request.Url.Scheme,
                request.Url.Authority,
                appRootFolder,
                Consts.WEBAPI_ROUTE_PREFIX
            );
        }

        private static string GetTypePluralNoun(GUIDRefTypeEnum type)
        {
            switch (type)
            {
                case GUIDRefTypeEnum.academicSession:
                    return "academicSessions";
                case GUIDRefTypeEnum.@class:
                    return "classes";
                case GUIDRefTypeEnum.course:
                    return "courses";
                case GUIDRefTypeEnum.org:
                    return "orgs";
                case GUIDRefTypeEnum.resource:
                    return "resources";
                case GUIDRefTypeEnum.user:
                    return "users";
                default:
                    throw new NotImplementedException($"Unknow DType {type}");
            }
        }
    }
}