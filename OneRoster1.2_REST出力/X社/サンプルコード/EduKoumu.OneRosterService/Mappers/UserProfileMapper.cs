using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;

namespace EduKoumu.OneRosterService.Mappers
{
    public class UserProfileMapper
    {
        public static UserProfileDType Map(OR_UserProfile entity) =>
            new UserProfileDType
            {
                ProfileId = new Uri(GUIDRefDTypeHelper.GetBaseUrl() + "userProfiles/" + entity.SourcedId.ToString()),
                ProfileType = entity.ProfileType,
                VendorId = entity.VenderId,
                ApplicationId = entity.ApplicationId,
                Description = entity.Description,
                Credentials = new List<CredentialDType>
                {
                    new CredentialDType
                    {
                        Type = entity.CredentialType,
                        Username = entity.Username,
                        Password = entity.Password, 
                    }
                }
            };
    }
}