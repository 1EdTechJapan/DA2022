from typing import Optional, List

# Account propeties of inverse functional identifier
class Account:
    def __init__(
            self,
            home_page: str,
            name: str
        ) -> None:
        self.__acount = {
            "homePage": home_page,
            "name": name
        }

    def __call__(self) -> dict:
        return self.__acount

# Inverse functional identifier
class InverseFunctionalIdentifier:
    def __init__(
            self,
            mbox: Optional[str] = None,
            mbox_sha1sum: Optional[str] = None,
            openid: Optional[str] = None,
            account: Optional[Account] = None
        ) -> None:

        if self.mbox_isnot_none(mbox, mbox_sha1sum, openid, account):
            self.__ifi = {"mbox": mbox}
        elif self.mbox_sha1sum_isnot_none(mbox, mbox_sha1sum, openid, account):
            self.__ifi = {"mbox_sha1sum": mbox_sha1sum}
        elif self.openid_isnot_none(mbox, mbox_sha1sum, openid, account):
            self.__ifi = {"openid": openid}
        elif self.account_isnot_none(mbox, mbox_sha1sum, openid, account):
            self.__ifi = {"account": account()}
        else:
            raise ValueError(f"Must input one argument")

    def mbox_isnot_none(self, mbox, mbox_sha1sum, openid, account):
        return bool(mbox) & ~(bool(mbox_sha1sum)) & ~(bool(openid)) & ~(bool(account))
    
    def mbox_sha1sum_isnot_none(self, mbox, mbox_sha1sum, openid, account):
        return ~(bool(mbox)) & bool(mbox_sha1sum) & ~(bool(openid)) & ~(bool(account))
    
    def openid_isnot_none(self, mbox, mbox_sha1sum, openid, account):
        return ~(bool(mbox)) & ~(bool(mbox_sha1sum)) & bool(openid) & ~(bool(account))
    
    def account_isnot_none(self, mbox, mbox_sha1sum, openid, account):
        return ~(bool(mbox)) & ~(bool(mbox_sha1sum)) & ~(bool(openid)) & bool(account)

    def __call__(self) -> dict:
        return self.__ifi

# Agent actor template
class AgentActor:
    def __init__(
            self, 
            ifi: InverseFunctionalIdentifier,
            name: Optional[str] = None, 
        ) -> None:
        if name is not None:
            actor = {
                "name": name,
                "objectType": "Agent"
            }
        else:
            actor = {"objectType": "Agent"}
        
        actor = actor | ifi()

        self.__agent_actor = actor

    def __call__(self) -> dict:
        return self.__agent_actor

# Group actor template
class GroupActor:
    def __init__(
            self,
            member: List[AgentActor],
            name: Optional[str] = None,
            ifi: Optional[InverseFunctionalIdentifier] = None
        ) -> None:
        group = {"objectType": "Group"}

        if name is not None:
            group["name"] = name

        group["member"] = [actor() for actor in member]

        if ifi is not None:
            group = group | ifi
        
        self.__group_actor = group

    def __call__(self) -> dict:
        return self.__group_actor