module LTI.Claim.ResourceLink where


import Data.Text (Text)
import Network.URI (URI)
import Data.Vector (Vector)

data ResourceLink = ResourceLink
  { id :: Text,
    description :: Text,
    title :: Text
  }
