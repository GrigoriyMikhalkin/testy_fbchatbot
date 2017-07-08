#!/bin/bash

# Setting up Started Button and Persistent Menu


# setting environment variables
source .env


# setting Started Button
curl -X POST -H "Content-Type: application/json" -d '{
  "get_started":{
    "payload":"GET_STARTED_PAYLOAD"
  },
  "greeting":[{
    "locale":"default",
    "text":"This chatbot was made for test"
  }, {
    "locale":"ru_RU",
    "text":"Этот бот был сделан для тестового задания"
  }]
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=$PAGE_ACCESS_TOKEN"


# setting Persistent Menu
curl -X POST -H "Content-Type: application/json" -d '{
  "persistent_menu":[
    {
      "locale":"default",
      "composer_input_disabled":false,
      "call_to_actions":[
        {
          "title":"Exchange rates",
          "type":"nested",
          "call_to_actions":[
            {
              "title":"USD/RUB",
              "type":"postback",
              "payload":"USDRUB_PAYLOAD"
            },
            {
              "title":"EUR/RUB",
              "type":"postback",
              "payload":"EURRUB_PAYLOAD"
            }
          ]
        },
        {
          "title":"Weather",
          "type":"postback",
          "payload":"WEATHER_PAYLOAD"
        },
      ]
    },
    {
      "locale":"ru_RU",
      "composer_input_disabled":false,
      "call_to_actions":[
        {
          "title":"Курсы валют",
          "type":"nested",
          "call_to_actions":[
            {
              "title":"USD/RUB",
              "type":"postback",
              "payload":"USDRUB_PAYLOAD"
            },
            {
              "title":"EUR/RUB",
              "type":"postback",
              "payload":"EURRUB_PAYLOAD"
            }
          ]
        },
        {
          "title":"Погода",
          "type":"postback",
          "payload":"WEATHER_PAYLOAD"
        },
      ]
    }
  ]
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=$PAGE_ACCESS_TOKEN"
