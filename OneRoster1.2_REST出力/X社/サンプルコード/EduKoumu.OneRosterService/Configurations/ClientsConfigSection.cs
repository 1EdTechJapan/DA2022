using System.Configuration;

namespace EduKoumu.OneRosterService.Configurations
{
    public class ClientsConfigSection : ConfigurationSection
    {
        [ConfigurationProperty("clients")]
        [ConfigurationCollection(typeof(ClientSettings))]
        public ClientSettings ClientSettings
        {
            get
            {
                // Get the collection and parse it
                return (ClientSettings)this["clients"];
            }
        }
    }
}