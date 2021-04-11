module Data.Family exposing (Family, decode)

import Json.Decode as Decode exposing (Decoder)
import Json.Decode.Pipeline exposing (required)


type alias Family =
    { id : Int
    , places_disponible : String
    , personne : String
    , disponibilites : String
    , caracteristiques : String
    , commentaire : String
    }


decode : Decoder Family
decode =
    Decode.succeed Family
        |> required "id" Decode.int
        |> required "places_disponible" Decode.string
        |> required "personne" Decode.string
        |> required "disponibilites" Decode.string
        |> required "caracteristiques" Decode.string
        |> required "commentaire" Decode.string
