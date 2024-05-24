using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;

namespace EduKoumu.OneRosterService.Utils
{
    public class DateTimeISO8601Converter : DateTimeConverterBase
    {
        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
        {
            return (DateTime?)reader.Value;
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
        {
            if (value == null)
            {
                writer.WriteNull();
            }
            else
            {
                writer.WriteValue(((DateTime)value).ToString("yyyy-MM-ddThh:mm:ss.fffZ"));
            }
        }
    }
}