@ECHO OFF
SET SvcName=mtsrv
for /f "skip=1" %%i in ('wmic os get localdatetime') do if not defined fulldate set fulldate=%%i
set year=%fulldate:~0,4%
set month=%fulldate:~4,2%
set day=%fulldate:~6,2%
set foldername=%year%%month%%day%

set "portCheck_status=false"
set "serviceCheck_status=false"
set hostName=%COMPUTERNAME%

set "EnvName=UAT"
set "emailName=gilbertyu@emperorgroup.com"
set "snmpServer=128.127.2.4"

ECHO Validate the MT4 server port status ...
netstat /o /a | find /i "listening" | find ":443" >nul 2>nul && (
   echo port 443 is open
   set "portCheck_status=true"
   EXIT /B 0
) || (
  echo port 443 is Not open
  set "portCheck_status=false"
  
  echo stop the "%SvcName%" service 
  NET STOP "%SvcName%" 
)


SC QUERYEX "%SvcName%" | FIND "STATE" | FIND /v "RUNNING" > NUL && (
    ECHO %SvcName% is not running 

	ECHO Backup the managers.ini before restart the service 
	if not exist D:\tmp\%foldername% md D:\tmp\%foldername%
	if not exist D:\tmp\%foldername%\managers.ini COPY D:\MetaTrader4Server\config\managers.ini D:\tmp\%foldername%\
	if not exist D:\tmp\%foldername%\managers.ini ECHO D:\tmp\%foldername%\managers.ini Cannot be backup && EXIT /B 1
	if exist D:\tmp\%foldername%\managers.ini ECHO D:\tmp\%foldername%\managers.ini has been backup

    ECHO START %SvcName%
	
    NET START "%SvcName%" > NUL || (
        ECHO "%SvcName%" wont start 
        REM EXIT /B 1
    )
    ECHO "%SvcName%" is started
    REM EXIT /B 0
) || (
    ECHO "%SvcName%" is running
    EXIT /B 0
)

ECHO Validate the MT4 server status after 30 secounds ...
ping -n 30 127.0.0.1
netstat /o /a | find /i "listening" | find ":443" >nul 2>nul && (
   echo port 443 is open
   set "portCheck_status=true"
) || (
  echo port 443 is Not open
  set "portCheck_status=false"
)

ECHO Check restarted MT4 managers.ini file size...
set file="D:\MetaTrader4Server\config\managers.ini"
set maxbytesize=100000

FOR /F "usebackq" %%A IN ('%file%') DO set size=%%~zA

if %size% LSS %maxbytesize% (
    echo.File [ERROR] '%file%' is ^< %maxbytesize% bytes
	ECHO Restore the managers.ini from backup...
	COPY D:\tmp\%foldername%\managers.ini D:\MetaTrader4Server\config\
) ELSE (
    echo.File [OK] '%file%' is ^>= %maxbytesize% bytes - file size check OK
)


SC QUERYEX "%SvcName%" | FIND "STATE" | FIND /v "RUNNING" > NUL && (set "serviceCheck_status=false") || (set "serviceCheck_status=true")



ECHO Send an e-mail to notice the status ...

if "%portCheck_status%" == "true" (
	if "%serviceCheck_status%" == "true" (
		powershell Send-MailMessage -To %emailName% -From %emailName%  -Subject '[Env: %EnvName%] %hostName% MT4 Server Service AUTO restarted : OK' -Body '[%EnvName%] %hostName% MT4 Server Service AUTO restarted : OK' -SmtpServer %snmpServer%
		EXIT /B 0
	)
) 


if "%portCheck_status%" == "false" (
	powershell Send-MailMessage -To %emailName% -From %emailName%  -Subject '[Env: %EnvName%] %hostName% MT4 Server Service AUTO restarted : NOK' -Body '[%EnvName%] %hostName% MT4 Server Service AUTO restarted : NOK, service status check: FAIL' -SmtpServer %snmpServer%
	EXIT /B 1
)

if "%portCheck_status%" == "false" (
	powershell Send-MailMessage -To %emailName% -From %emailName%  -Subject '[Env: %EnvName%] %hostName% MT4 Server Service AUTO restarted : NOK' -Body '[%EnvName%] %hostName% MT4 Server Service AUTO restarted: NOK, port check status: FAIL' -SmtpServer %snmpServer%
	EXIT /B 1
)


