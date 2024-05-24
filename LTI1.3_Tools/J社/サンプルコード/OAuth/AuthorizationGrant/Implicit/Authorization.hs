{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.Implicit.Authorization where

import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data Request = Request
  { responseType :: Text,
    clientId :: Text,
    redirectUri :: URI,
    scope :: Maybe Text,
    state :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (FromHttpApiData, ToHttpApiData, ToParamSchema, ToSchema)
