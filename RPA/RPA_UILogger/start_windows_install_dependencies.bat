set /p @userID="Please provide your user ID: "

echo "Starting action logger with userID: %@userID%"

cd Excel_Addin
call npm install
cd ..
cd append_http
call npm install
cd ..

start npm start %@userID% --prefix append_http
call npm start --prefix Excel_Addin
