module Request.FamilyCandidates exposing (fetchFamilies)

import Data.Animal exposing (Animal)
import Data.Family as Family exposing (Family)
import Date exposing (Date)
import Http
import HttpBuilder
import Json.Decode as Decode exposing (Decoder)
import Json.Encode as Encode


fetchFamilies : String -> Date -> List Animal -> (Result Http.Error (List Family) -> msg) -> Cmd msg
fetchFamilies url date_debut animals toMsg =
    HttpBuilder.post url
        |> HttpBuilder.withCredentials
        |> HttpBuilder.withJsonBody (encodeData date_debut animals)
        |> HttpBuilder.withExpect (Http.expectJson toMsg decodeData)
        |> HttpBuilder.request


decodeData : Decoder (List Family)
decodeData =
    Decode.at [ "familles_candidates" ] (Decode.list Family.decode)


encodeData : Date -> List Animal -> Encode.Value
encodeData date_debut animals =
    Encode.object
        [ ( "date_debut", Encode.string <| Date.format "yyyy-MM-dd" date_debut )
        , ( "animaux", Encode.list Encode.int <| List.map .id animals )
        ]
