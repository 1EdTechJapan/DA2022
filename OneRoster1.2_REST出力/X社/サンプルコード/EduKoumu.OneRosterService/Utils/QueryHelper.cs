using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Exceptions;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data.Entity;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Utils
{
    public class QueryHelper
    {
        public static async Task<List<T>> Query<T>(
            IQueryable<T> query, int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter
        )
            where T : class
        {

            if (!string.IsNullOrWhiteSpace(filter))
            {
                var filterExpression = GetFilterExpression<T>(filter);
                query = query.Where(filterExpression);
            }

            if (!string.IsNullOrWhiteSpace(sort))
            {
                query = SortBy(query, sort, orderBy);
            }

            if (offset.HasValue && offset.Value > 0)
            {
                query = query.Skip(offset.Value);
            }

            if (limit.HasValue && limit.Value > 0)
            {
                query = query.Take(limit.Value);
            }

            return await query.ToListAsync();
        }

        public static async Task<T> GetBySourcedId<T>(IQueryable<T> query, string sourcedId)
            where T : class
        {
            Guid sourcedGuid;

            try
            {
                sourcedGuid = new Guid(sourcedId);
            }
            catch (Exception ex)
            {
                throw new InvalidFilterFieldException($"SourcedId {sourcedId} is not a Guid: {ex.Message}");
            }

            //parameter expression of x=> condition
            var parameterExpression = Expression.Parameter(typeof(T));

            //Expression for accessing sourcedId property
            Expression eSourcedId = Expression.Property(parameterExpression, "SourcedId");

            //the sourcedId to match 
            Expression cSourcedGuid = Expression.Constant(sourcedGuid);

            //the equal expression: ClaimantLastName = ?
            var equalExpression = Expression.Equal(eSourcedId, cSourcedGuid);

            var whereClause = Expression.Lambda<Func<T, Boolean>>(equalExpression, new ParameterExpression[] { parameterExpression });

            var entity = await query.Where(whereClause).SingleOrDefaultAsync();

            if (entity == null)
            {
                throw new UnknownObjectException($"{typeof(T).Name} {sourcedId} not found!");
            }

            return entity;
        }


        private static Expression<Func<T, Boolean>> GetFilterExpression<T>(string filter)
        {
            var conditionExp = @"(?'field'(\w+)(\.\w+)*)\s*(?'predicate'=|(!=)|>|(>=)|<|(<=)|~)\s*'(?'value'.+?)'\s*";
            var filterExp = $"^({conditionExp})(\\s+(?'logical'AND|OR)\\s+({conditionExp}))?$";

            var match = Regex.Match(filter, filterExp, RegexOptions.IgnoreCase);
            if (!match.Success)
            {
                throw new InvalidFilterFieldException("Invalid filter string!");
            }

            var field1 = match.Groups["field"].Captures[0].Value;
            var predicate1 = match.Groups["predicate"].Captures[0].Value;
            var value1 = match.Groups["value"].Captures[0].Value;


            //parameter expression of x=> condition
            var parameterExpression = Expression.Parameter(typeof(T));

            var filterExpression1 = GetPredicateExpression<T>(parameterExpression, field1, predicate1, value1);

            if (match.Groups["logical"].Success)
            {
                var field2 = match.Groups["field"].Captures[1]?.Value;
                var predicate2 = match.Groups["predicate"].Captures[1]?.Value;
                var value2 = match.Groups["value"].Captures[1]?.Value;

                var filterExpression2 = GetPredicateExpression<T>(parameterExpression, field2, predicate2, value2);

                var logical = match.Groups["logical"].Value.ToLower();

                switch (logical)
                {
                    case "and":
                        filterExpression1 = Expression.And(filterExpression1, filterExpression2);
                        break;
                    case "or":
                        filterExpression1 = Expression.Or(filterExpression1, filterExpression2);
                        break;
                    default:
                        throw new Exception($"Unkonow logical '{logical}' in query expression!");
                }
            }

            //create and return the predicate
            return Expression.Lambda<Func<T, Boolean>>(filterExpression1, new ParameterExpression[] { parameterExpression });
        }

        private static Expression GetPredicateExpression<T>(Expression parameterExpression, string field, string predicate, string value)
        {
            //if(field.Contains('.'))
            //{
            //    return Expression.Constant(true);
            //}

            //Expression for accessing field property
            Expression eField = Expression.Property(parameterExpression, field);

            //the value to check
            Expression cValue = Expression.Constant(value);

            switch (predicate)
            {
                case "=":
                    return Expression.Equal(eField, cValue);
                case "!=":
                    return Expression.NotEqual(eField, cValue);
                case ">":
                    return Expression.GreaterThan(eField, cValue);
                case ">=":
                    return Expression.GreaterThanOrEqual(eField, cValue);
                case "<":
                    return Expression.LessThan(eField, cValue);
                case "<=":
                    return Expression.LessThanOrEqual(eField, cValue);
                case "~":
                    return Expression.Call(eField, "Contains", null, cValue);
                default:
                    throw new Exception($"Unkonow predicate '{predicate}' in query expression!");
            }
        }

        private static IQueryable<T> SortBy<T>(IQueryable<T> source, string sort, OrderByEnum? sortDirection)
        {
            var sortPropertyInfo = typeof(T).GetProperty(sort, BindingFlags.IgnoreCase | BindingFlags.Public | BindingFlags.Instance);
            if (sortPropertyInfo == null)
            {
                throw new InvalidFilterFieldException($"Sort field {sort} not found in type {typeof(T).Name}");
            }
            var sortPropertyType = sortPropertyInfo.PropertyType;
            var methodName = sortDirection == OrderByEnum.desc ? "OrderByDescending" : "OrderBy";

            var arg = Expression.Parameter(typeof(T));
            Expression mExpr = Expression.Property(arg, sortPropertyInfo);

            // For guid column, sort them in order of Guid.ToString()
            if(sortPropertyType == typeof(Guid))
            {
                var toStringMethod = typeof(Guid).GetMethods()
                  .Single(m => m.Name == nameof(Guid.ToString) && m.GetParameters().Length == 0);

                mExpr = Expression.Call(mExpr, toStringMethod);

                sortPropertyType = typeof(string);
            }

            var delegateType = typeof(Func<,>).MakeGenericType(typeof(T), sortPropertyType);
            var lambda = Expression.Lambda(delegateType, mExpr, arg);

            var orderedSource = typeof(Queryable).GetMethods().Single(
                method => method.Name == methodName
                        && method.IsGenericMethodDefinition
                        && method.GetGenericArguments().Length == 2
                        && method.GetParameters().Length == 2)
                .MakeGenericMethod(typeof(T), sortPropertyType)
                .Invoke(null, new object[] { source, lambda });

            return (IQueryable<T>)orderedSource;
        }
    }
}