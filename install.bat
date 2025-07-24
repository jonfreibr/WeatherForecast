@echo off
echo Sourcing from: %~dp0
echo Installing Python 3.11.5
"%~dp0\python-3.11.5-amd64.exe" /passive
echo upgrading pip
%LocalAppData%\Programs\Python\Python311\python.exe -m pip install --upgrade pip
echo Adding package requirements
%LocalAppData%\Programs\Python\Python311\Scripts\pip.exe install -r "%~dp0\requirements.txt"
echo Copying files
if not exist %USERPROFILE%\WForecast md %USERPROFILE%\WForecast
copy /y "%~dp0\forecast.py" %USERPROFILE%\WForecast
copy /y "%~dp0\*.png" %USERPROFILE%\WForecast
copy /y "%~dp0\Weather Forecast.lnk" %USERPROFILE%\Desktop
if not exist %USERPROFILE%\WForecast\forecast.json copy /y %~dp0\forecast.json %USERPROFILE%\WForecast
echo Done with installation
start %USERPROFILE%"\Desktop\Weather Forecast.lnk"