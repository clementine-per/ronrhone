module FamilySelector exposing (main)

import Browser
import Data.Animal exposing (Animal)
import Data.Core exposing (Flags, Model, Msg(..))
import Data.Family as Family exposing (Family)
import Date exposing (Date)
import DatePicker exposing (DateEvent(..), defaultSettings)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as Decode
import Request.FamilyCandidates as FamilyCandidates
import Views.Animal as AnimalView
import Views.DatePicker as DatePickerView exposing (datePickerSettings)
import Views.Family as FamilyView



-- MAIN


main : Program Flags Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


init : Flags -> ( Model, Cmd Msg )
init flags =
    let
        ( datePicker, datePickerCmd ) =
            DatePicker.init
    in
    ( { dateDebutPicker = datePicker
      , date_debut = Nothing
      , animals = flags.animals
      , selectedAnimals = []
      , families = []
      , url = flags.url
      }
    , Cmd.map SetDatePicker datePickerCmd
    )



-- UPDATE


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        refreshFamilies newModel =
            case ( newModel.date_debut, newModel.selectedAnimals ) of
                ( _, [] ) ->
                    ( newModel, Cmd.none )

                ( Nothing, _ ) ->
                    ( newModel, Cmd.none )

                ( Just date_debut, selectedAnimals ) ->
                    ( newModel, FamilyCandidates.fetchFamilies model.url date_debut selectedAnimals FamiliesFetched )
    in
    case msg of
        SetDatePicker subMsg ->
            let
                ( newDatePicker, dateEvent ) =
                    DatePicker.update datePickerSettings subMsg model.dateDebutPicker

                date =
                    case dateEvent of
                        Picked newDate ->
                            Just newDate

                        _ ->
                            model.date_debut

                newModel =
                    { model
                        | date_debut = date
                        , dateDebutPicker = newDatePicker
                    }
            in
            refreshFamilies newModel

        ToggleAnimal animal _ ->
            let
                newModel =
                    if List.member animal model.selectedAnimals then
                        { model | selectedAnimals = List.filter (\a -> a /= animal) model.selectedAnimals }

                    else
                        { model | selectedAnimals = animal :: model.selectedAnimals }
            in
            refreshFamilies newModel

        FamiliesFetched (Err err) ->
            ( { model | families = [] }, Cmd.none )

        FamiliesFetched (Ok families) ->
            ( { model | families = families }, Cmd.none )


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none



-- VIEW


view : Model -> Html Msg
view model =
    div [ class "p-2" ]
        [ DatePickerView.view model
        , AnimalView.view model.animals model.selectedAnimals
        , FamilyView.view model.families
        ]
