using System.Configuration;

namespace EduKoumu.OneRosterService.Configurations
{
    public class ClientSettings : ConfigurationElementCollection
    {
        public new ClientSetting this[string key]
        {
            get
            {
                return (ClientSetting)BaseGet(key);
            }
        }

        protected override ConfigurationElement CreateNewElement()
        {
            return new ClientSetting();
        }

        protected override object GetElementKey(ConfigurationElement element)
        {
            return ((ClientSetting)element).Id;
        }
    }
}