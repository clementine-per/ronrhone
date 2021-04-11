module Views.Family exposing (view)

import Data.Core exposing (Msg(..))
import Data.Family exposing (Family)
import Html exposing (Html, input, pre, table, tbody, td, text, th, thead, tr)
import Html.Attributes exposing (checked, class, colspan, id, name, required, type_, value)


view : List Family -> Html Msg
view families =
    let
        firstId =
            case families of
                first :: _ ->
                    first.id

                _ ->
                    0
    in
    table [ class "display table table-sm table-bordered", id "famille" ]
        [ thead []
            [ tr []
                [ th [ class "no-sort" ]
                    []
                , th []
                    [ text "Places Disponibles" ]
                , th []
                    [ text "Personne" ]
                , th []
                    [ text "Disponibilité" ]
                , th []
                    [ text "Caractéristiques" ]
                , th []
                    [ text "Commentaire" ]
                ]
            ]
        , if List.length families == 0 then
            tbody [] [ tr [] [ td [ colspan 6, class "text-center" ] [ text "Aucune famille disponible" ] ] ]

          else
            List.map (viewFamily firstId) families |> tbody []
        ]


viewFamily : Int -> Family -> Html Msg
viewFamily firstId family =
    tr []
        [ td []
            [ input
                [ class "tableselectmultiple selectable-checkbox form-check-input"
                , id <| "id_famille_" ++ String.fromInt family.id
                , name "famille"
                , type_ "radio"
                , required True
                , checked <| firstId == family.id
                , value <| String.fromInt family.id
                ]
                []
            ]
        , td [] [ text family.places_disponible ]
        , td [] [ text family.personne ]
        , td [] [ text family.disponibilites ]
        , td [] [ pre [] [ text family.caracteristiques ] ]
        , td [] [ text family.commentaire ]
        ]
