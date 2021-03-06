module Views.DatePicker exposing (datePickerSettings, view)

import Data.Core exposing (Model, Msg(..))
import Date
import DatePicker exposing (defaultSettings)
import Html exposing (Html, label, p, text)
import Html.Attributes exposing (for)


datePickerSettings : DatePicker.Settings
datePickerSettings =
    { defaultSettings
        | inputId = Just "id_date_debut"
        , inputName = Just "date_debut"
        , placeholder = "Choisissez une date début…"
        , dateFormatter = Date.format "dd/MM/yyyy"
    }


view : Model -> Html Msg
view model =
    p []
        [ label [ for "id_date_debut" ] [ text "Date de début :" ]
        , DatePicker.view
            model.date_debut
            datePickerSettings
            model.dateDebutPicker
            |> Html.map SetDatePicker
        ]
