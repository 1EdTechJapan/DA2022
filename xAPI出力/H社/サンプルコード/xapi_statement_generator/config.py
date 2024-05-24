from pathlib import Path

class Config:
    def __init__(self) -> None:
        self._HOME_PAGE = "https://example.com" # home page of account
        self._LEARNING_RECORD_PROVIDER = "example" # LRP name
        self._STATEMENT_VERSION = "1.0.0" # statement version, must be start from 1.0.
        self._IRI_BASE = "http://example.com/xapi" # iri base
        self._SAVE_PATH = Path("statement_store") # statement save path
        self._RESOURCE_PATH = Path("xapi_statement_generator/resources")
    
    def __getitem__(self, key: str) -> str:
        return self.__dict__[f"_{key}"]

    @property
    def HOME_PAGE(self) -> str:
        return self._HOME_PAGE
    
    @property
    def LEARNING_RECORD_PROVIDER(self) -> str:
        return self._LEARNING_RECORD_PROVIDER
    
    @property
    def STATEMENT_VERSION(self) -> str:
        return self._STATEMENT_VERSION
    
    @property
    def IRI_BASE(self) -> str:
        return self._IRI_BASE
    
    @property
    def SAVE_PATH(self) -> Path:
        return self._SAVE_PATH
    
    @property
    def RESOURCE_PATH(self) -> Path:
        return self._RESOURCE_PATH