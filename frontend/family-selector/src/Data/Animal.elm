module Data.Animal exposing (Animal, decode)

import Json.Decode as Decode exposing (Decoder)
import Json.Decode.Pipeline exposing (required)


type alias Animal =
    { id : Int
    , label : String
    }


decode : Decoder Animal
decode =
    Decode.succeed Animal
        |> required "id" Decode.int
        |> required "label" Decode.string
