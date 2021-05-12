@ECHO OFF
ECHO.
ECHO ======================================
ECHO  vCO Storage artifact script
ECHO. 
ECHO  All Rights Reserved. Copyright (c) 2015, Hitachi Ltd.
ECHO. 
ECHO  Version 1.2.0
ECHO ======================================
ECHO.

SET ARTIFACTDIR=%CD%\Artifacts\vROSt-support.%RANDOM%

SET DATADIRFORVCO=%ProgramFiles%\Hitachi\vROStorageConnector\log
SET DATADIRFORVIAPI=%ProgramFiles%\Hitachi\vROStorageConnector\VIAPIService\log
SET HORCMDIR=\HORCM

SET ORCHESTRATORBASEDIR=%ProgramFiles%\VMware\Infrastructure\Orchestrator
SET VCOPLUGINCONFIG=%ORCHESTRATORBASEDIR%\app-server\conf\plugins
SET VCOTOMCATLOG=%ORCHESTRATORBASEDIR%\app-server\logs

SET VRO6BASEDIR=%ProgramFiles%\VMware\Orchestrator
SET VRO6PLUGINCONFIG=%VRO6BASEDIR%\app-server\conf\plugins
SET VRO6TOMCATLOG=%VRO6BASEDIR%\app-server\logs

mkdir "%ARTIFACTDIR%"
IF NOT EXIST "%ARTIFACTDIR%" (
	ECHO Error - unable to create artifact directory "%ARTIFACTDIR%".
	GOTO:EOF
)

ECHO Created "%ARTIFACTDIR%"



ECHO.
ECHO Collecting Hitachi vRO-Storage Information

REM =================
rem ECHO.
rem ECHO Copying HORCM log.
REM =================


IF EXIST %HORCMDIR% (
FOR /F "delims=|" %%F IN ('DIR /B %HORCMDIR%\log*.') DO xcopy /Q /S /I "%HORCMDIR%\%%F" "%ARTIFACTDIR%\HORCMLog\%%F" > NUL
)


IF EXIST %ORCHESTRATORBASEDIR% (
MKDIR "%ARTIFACTDIR%\VROCONFIG" > NUL
COPY /Y "%VCOPLUGINCONFIG%\*.*" "%ARTIFACTDIR%\VROCONFIG" > NUL
COPY /Y "%ORCHESTRATORBASEDIR%\apps\vso.log" "%ARTIFACTDIR%\VROCONFIG" > NUL
MKDIR "%ARTIFACTDIR%\APPSERVERLOG" > NUL
COPY /Y "%VCOTOMCATLOG%\*.*" "%ARTIFACTDIR%\APPSERVERLOG" > NUL
)


IF EXIST %VRO6BASEDIR% (
IF NOT EXIST "%ARTIFACTDIR%\VROCONFIG" (
   MKDIR "%ARTIFACTDIR%\VROCONFIG" > NUL
)
COPY /Y "%VRO6PLUGINCONFIG%\*.*" "%ARTIFACTDIR%\VROCONFIG" > NUL
COPY /Y "%VRO6BASEDIR%\apps\vso.log" "%ARTIFACTDIR%\VROCONFIG" > NUL
IF NOT EXIST "%ARTIFACTDIR%\APPSERVERLOG" (
   MKDIR "%ARTIFACTDIR%\APPSERVERLOG" > NUL
)
COPY /Y "%VRO6TOMCATLOG%\*.*" "%ARTIFACTDIR%\APPSERVERLOG" > NUL
)


REM =================
ECHO.
ECHO Copying logs.
REM =================

call:copyFiles "%DATADIRFORVCO%\*.*" "%ARTIFACTDIR%\Log"
call:copyFiles "%DATADIRFORVIAPI%\*.*" "%ARTIFACTDIR%\VIAPILog"

REM THE END

ECHO.
ECHO If you use vRO appliance please copy the vRO's logs manually to "%ARTIFACTDIR%" folder
ECHO.
ECHO Please compress and send the contents of folder "%ARTIFACTDIR%" in with your defect report.
ECHO.

PAUSE
GOTO:EOF

:copyFiles
IF NOT EXIST "%~2" mkdir "%~2" > NUL
copy /Y "%~1" "%~2" > NUL
IF ERRORLEVEL 1 (
	ECHO 	Could not copy "%~1" to "%~2".
)
GOTO:EOF