using System.Configuration;

namespace EduKoumu.OneRosterService.Configurations
{
    public class ClientSetting : ConfigurationElement
    {
        [ConfigurationProperty("Id", IsKey = true, IsRequired = true)]
        public string Id
        {
            get
            {
                return (string)this["Id"];
            }
            set
            {
                value = (string)this["Id"];
            }
        }

        [ConfigurationProperty("Secret", IsRequired = true)]
        public string Secret
        {
            get
            {
                return (string)this["Secret"];
            }
            set
            {
                value = (string)this["Secret"];
            }
        }

        [ConfigurationProperty("Scope", IsRequired = true)]
        public string Scope
        {
            get
            {
                return (string)this["Scope"];
            }
            set
            {
                value = (string)this["Scope"];
            }
        }

        [ConfigurationProperty("Memo")]
        public string Memo
        {
            get
            {
                return (string)this["Memo"];
            }
            set
            {
                value = (string)this["Memo"];
            }
        }
    }
}