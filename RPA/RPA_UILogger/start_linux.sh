#!/bin/sh
echo "Please provide your user ID:"

read userID

echo "Starting action logger with userID: $userID"

npm install --prefix Excel_Addin
npm install --prefix append_http

(npm start --prefix Excel_Addin & npm start $userID --prefix append_http)
