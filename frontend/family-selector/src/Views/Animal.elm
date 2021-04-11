module Views.Animal exposing (view)

import Data.Animal exposing (Animal)
import Data.Core exposing (Msg(..))
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)


view : List Animal -> List Animal -> Html Msg
view animals selectedAnimals =
    div []
        [ p []
            [ label []
                [ text "Animaux :" ]
            ]
        , List.map (viewAnimal selectedAnimals) animals
            |> ul [ id "id_animaux" ]
        ]


viewAnimal : List Animal -> Animal -> Html Msg
viewAnimal selectedAnimals animal =
    let
        html_id =
            "id_animaux_" ++ String.fromInt animal.id

        is_checked =
            List.member animal selectedAnimals
    in
    li []
        [ label [ for html_id ]
            [ input
                [ id html_id
                , name "animaux"
                , type_ "checkbox"
                , value <| String.fromInt animal.id
                , onInput <| ToggleAnimal animal
                , checked is_checked
                ]
                []
            , text <| " " ++ animal.label
            ]
        ]
