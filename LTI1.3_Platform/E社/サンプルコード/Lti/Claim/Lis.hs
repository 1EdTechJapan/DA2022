module LTI.Claim.Lis where

import Data.Text (Text)

data Lis = Lis
  { personSourcedid :: Text,
    courseOfferingSourcedid :: Text,
    courseSectionSourcedid :: Text
  }
