from dataclasses import dataclass

from app.entities.user import User


@dataclass
class Api_search_date(User):
    """
    Ldapで時間指定で検索するためのエンティティ。LDAP情報はUserエンティティ側に記載
    """
    export_type: str = None
    export_term: int = None
    hours_ago: int = None
    start_time: str = None
    end_time: str = None
    offset: int = None
    oneroster_api_host: str = None

