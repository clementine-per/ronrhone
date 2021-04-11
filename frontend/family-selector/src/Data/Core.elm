module Data.Core exposing (Flags, Model, Msg(..))

import Data.Animal exposing (Animal)
import Data.Family exposing (Family)
import Date exposing (Date)
import DatePicker
import Http


type alias Flags =
    { animals : List Animal
    , url : String
    }


type alias Model =
    { dateDebutPicker : DatePicker.DatePicker
    , date_debut : Maybe Date
    , animals : List Animal
    , selectedAnimals : List Animal
    , families : List Family
    , url : String
    }


type Msg
    = SetDatePicker DatePicker.Msg
    | ToggleAnimal Animal String
    | FamiliesFetched (Result Http.Error (List Family))
