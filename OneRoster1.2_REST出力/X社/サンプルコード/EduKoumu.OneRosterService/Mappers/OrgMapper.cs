using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Org;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web.UI.WebControls;

namespace EduKoumu.OneRosterService.Mappers
{
    public class OrgMapper
    {
        public static OrgDType Map(OR_Org entity, string fields)
        {
            var org = new OrgDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Name = entity.Name,
                Type = (OrgTypeEnum)Enum.Parse(typeof(OrgTypeEnum), entity.Type),
                Identifier = entity.Identifier,
                Parent = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, entity.Parent),
                Children = GUIDRefDTypeHelper.GetGUIDRefDTypeList(GUIDRefTypeEnum.org, entity.OR_Children.Select(x => x.SourcedId).ToArray()),
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(org, fields);
        }

        public static List<OrgDType> Map(List<OR_Org> entities, string fields) =>
            entities.Select(x => Map(x, fields)).ToList();
    }
}