using EduKoumu.OneRosterService.Exceptions;
using System;
using System.Linq;
using System.Reflection;

namespace EduKoumu.OneRosterService.Utils
{
    public class SelectionFieldsHelper
    {
        public static T SetNotSelectedFieldsToNull<T>(T obj, string fields)
        {
            if(string.IsNullOrEmpty(fields))
            {
                return obj;
            }

            var selectionFields = fields?.Split(new[] { ',' }).ToList();

            // https://www.imsglobal.org/sites/default/files/spec/oneroster/v1p2/rostering-restbinding/OneRosterv1p2RosteringService_RESTBindv1p0.html#Main3p4
            // If the consumer requests that data be selected using a blank field the request will be treated as an invalid request. 
            if (selectionFields.Any(x => string.IsNullOrWhiteSpace(x)))
            {
                throw new InvalidSelectionFieldException($"Selection field must not be blank!");
            }

            // If the consumer requests that data be selected using non-existent field, ALL data for the record is returned.
            if (selectionFields.Any(x => !FieldExists<T>(x)))
            {
                return obj;
            }

            foreach(var property in typeof(T).GetProperties())
            {
                if (!selectionFields.Contains(property.Name, StringComparer.OrdinalIgnoreCase))
                {
                    if (!property.PropertyType.IsValueType)
                    {
                        property.SetValue(obj, null);
                    }

                    if (property.PropertyType.IsGenericType && property.PropertyType.GetGenericTypeDefinition() == typeof(Nullable<>))
                    {
                        property.SetValue(obj, null);
                    }
                }
            }

            return obj;
        }

        private static bool FieldExists<T>(string field)
        {
            var propertyInfo = typeof(T).GetProperty(field, BindingFlags.IgnoreCase | BindingFlags.Public | BindingFlags.Instance);

            if (propertyInfo == null)
            {
                // Caution: this breaks the following request described in standard:
                // If the consumer requests that data be selected using non-existent field, ALL data for the record is returned.
                throw new InvalidSelectionFieldException($"Field {field} not exists in type {typeof(T).Name}");
            }

            return propertyInfo != null;
        }
    }
}