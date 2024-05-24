from typing import Optional, Union, List, Any
from warnings import warn
from urllib import parse
from datetime import timedelta, datetime, timezone
from language_tags import tags

# IRI type
class IRI:
    def __init__(self, iri: str) -> None:
        if self.validate_iri(iri):
            self.__iri = iri
        else:
            raise ValueError(f"{iri} is not valid IRI")

    def validate_iri(self, iri: str) -> bool:
        parsed_iri = parse.urlparse(iri)
        if not parsed_iri.scheme or not parsed_iri.netloc:
            return False
        return True

    def __str__(self) -> str:
        return self.__iri
    
    def __repr__(self) -> str:
        return self.__iri
    
    def __call__(self) -> str:
        return self.__iri

# Timestamp type
class Timestamp:
    def __init__(self, timestamp: datetime, tzone: Optional[timezone] = None) -> None:
        if timestamp.tzinfo is None:
            if tzone is None:
                warn(f"No timezone infomation")
                self.__timestamp = timestamp.isoformat()[:-3]
                return
            
            timestamp = timestamp.astimezone(tzone)

        timestamp = timestamp.isoformat()
        self.__timestamp = timestamp[:23] + timestamp[26:]
    
    def __str__(self) -> str:
        return self.__timestamp

    def __repr__(self) -> str:
        return self.__timestamp
    
    def __call__(self) -> dict:
        return self.__timestamp
    
    @classmethod
    def now(cls):
        return cls(datetime.now(timezone.utc))

# Version type
class Version:
    def __init__(
            self,
            version: Optional[str] = None,
            major_version: Optional[int] = None,
            minor_version: Optional[int] = None,
            patch_version: Optional[int] = None
        ) -> None:
        if version is not None:
            if self.validate_version(version):
                self.__version = self.add_patch_version(version)
                return
            else:
                raise ValueError(f"Argument version is not valid.")

        if major_version is None:
            raise ValueError(f"Argument major_version should not be None if argument version is None.")
        
        if minor_version is None:
            raise ValueError(f"Argument minor_version should not be None if argument version is None.")

        if patch_version is None:
            patch_version = 0

        self.__version = f"{major_version}.{minor_version}.{patch_version}"

    def validate_version(self, version: str) -> bool:
        parsed_version = version.split(".")
        
        if len(parsed_version) == 2 or len(parsed_version) == 3:
            for v in parsed_version:
                if not v.isdecimal():
                    return False
                
            return True
        
        return False

    def add_patch_version(self, version: str) -> str:
        parsed_version = version.split(".")

        if len(parsed_version) == 2:
            return version + ".0"
        if len(parsed_version) == 3:
            if parsed_version[2] == "":
                return version + "0"
            return version
        
        raise ValueError(f"Argument version has less than 2 or more than 3 numbers")
            
    def __str__(self) -> str:
        return self.__version
    
    def __repr__(self) -> str:
        return self.__version
    
    def __call__(self) -> str:
        return self.__version

# Language code type
class Language:
    def __init__(self, tag: str) -> None:
        if tags.check(tag):
            self.__language = tag
            return
        
        raise ValueError(f"{tag} does not match RFC 5646")
    
    def __str__(self) -> str:
        return self.__language
    
    def __repr__(self) -> str:
        return self.__language

    def __call__(self) -> Any:
        return self.__language

# Language map type
class LanguageMap:
    def __init__(
            self,
            languages: Union[str, Language, List[str], List[Language]],
            definitions: Union[str, List[str]]
        ) -> None:
        
        if isinstance(languages, str) & isinstance(definitions, str):
            languages = Language(languages)
            self.__language_maps = {languages(): definitions}
            return

        if len(languages) != len(definitions):
            raise ValueError(f"Number of keys and values do not match")
        
        self.__language_maps = {}
        for key, val in zip(languages, definitions):
            if isinstance(key, str):
                key = Language(key)

            self.__language_maps[key()] = val
    
    def __call__(self) -> dict:
        return self.__language_maps
    
# Extensions type
class Extensions:
    def __init__(
            self,
            keys: Union[IRI, List[IRI]],
            values: Any
        ) -> None:
        if isinstance(keys, IRI):
            extensions = {keys(): values}
        else:
            extensions = {}
            for key, val in zip(keys, values):
                extensions[key()] = val
        
        self.__extensions = extensions

    def __call__(self) -> dict:
        return self.__extensions

# Duration type
class Duration:
    def __init__(
            self,
            duration: Optional[timedelta] = None,
            year: Optional[int] = None,
            month: Optional[int] = None,
            day: Optional[int] = None,
            hour: Optional[int] = None,
            minute: Optional[int] = None,
            second: Optional[float] = None
        ) -> None:
        if duration is not None:
            self.__iso8601_duration = self.timedelta_2_iso8601(duration)
            return
        
        period = ""
        if year is not None:
            period += f"{year}Y"
        if month is not None:
            period += f"{month}M"
        if day is not None:
            period += f"{day}D"
        
        time = ""
        if hour is not None:
            time += f"{hour}H"
        if minute is not None:
            time += f"{minute}M"
        if second is not None:
            time += f"{second}S"

        iso8601_duration = "P"
        if period != "":
            iso8601_duration += f"{period}"
        if time != "":
            iso8601_duration += f"T{time}"
        
        self.__iso8601_duration = iso8601_duration

    def timedelta_2_iso8601(self, duration: timedelta):
        """
        Because timedelta object does not store month or year information,
        this method assumes that 1 year = 365 days and 1 month = 31 days.
        """

        is08601_duration = "P"

        if duration.days > 0:
            day = duration.days
            if day >= 365:
                year = day // 365
                day -= year * 365
                
                is08601_duration += f"{year}Y"
            if day >= 31:
                month = day // 31
                day -= month * 31
                
                is08601_duration += f"{month}M"
            is08601_duration += f"{day}D"
        
        if duration.seconds > 0:
            is08601_duration += "T"

            sec = duration.seconds
            if sec >= 3600:
                hour = sec // 3600
                sec -= hour * 3600

                is08601_duration += f"{hour}H"
            if sec >= 60:
                minute = sec // 60
                sec -= minute * 60

                is08601_duration += f"{minute}M"
            is08601_duration += f"{sec}S"

        return is08601_duration

    def __str__(self) -> str:
        return self.__iso8601_duration
    
    def __call__(self) -> str:
        return self.__iso8601_duration
        
# Attachment type
class Attachment:
    def __init__(
            self,
            usage_type: IRI,
            display: LanguageMap,
            content_type: str,
            length: int,
            sha2: str,
            description: Optional[LanguageMap] = None,
            file_url: Optional[IRI] = None
        ) -> None:
        attachment = {
            "usageType": usage_type,
            "display": display(),
            "contentType": content_type,
            "length": length,
            "sha2": sha2,
        }

        if description is not None:
            attachment["description"] = description
        if file_url is not None:
            attachment["fileUrl"] = file_url

        self.__attachment = attachment
    
    def __call__(self) -> dict:
        return self.__attachment