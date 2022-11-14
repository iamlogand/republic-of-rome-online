set pythonVirtualEnvActivationScriptPath=".\backend\env\Scripts\activate"
start cmd /k %pythonVirtualEnvActivationScriptPath%" & py .\backend\manage.py runserver"
start cmd /k "cd .\frontend & npm run start"