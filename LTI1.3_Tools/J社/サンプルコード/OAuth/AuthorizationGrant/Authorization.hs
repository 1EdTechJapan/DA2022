module OAuth.AuthorizationGrant.Authorization where

import qualified OAuth.AuthorizationGrant.AuthorizationCode.Authorization as AuthorizationCode
import qualified OAuth.AuthorizationGrant.Implicit.Authorization as Implicit

data AuthorizationRequest
  = AuthorizationCode.Request
  | Implicit.Request
