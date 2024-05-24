module LTI.Claim.Context where

import Data.Text (Text)
import Network.URI (URI)
import Data.Vector (Vector)

data Context = Context
  { id :: Text,
    label :: Text,
    title :: Text,
    type :: Vector URI
  }
