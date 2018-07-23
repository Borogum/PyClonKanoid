@ECHO OFF

SET IRONPYTHON_COMPILER=C:\IronPython2.7\ipyc.exe
SET SOURCE_PATH=%~dp0
SET OUT_PATH=%~dp0bin\


copy /Y %SOURCE_PATH%pyclonkanoid.xaml %OUT_PATH%pyclonkanoid.xaml
copy /Y %SOURCE_PATH%config.cfg %OUT_PATH%config.cfg
copy /Y %SOURCE_PATH%icon.ico %OUT_PATH%icon.ico


%IRONPYTHON_COMPILER% ^
%SOURCE_PATH%pyclonkanoid.py ^
/out:%OUT_PATH%pyclonkanoid ^
/main:%SOURCE_PATH%pyclonkanoid.py ^
/target:winexe ^
/win32icon:%SOURCE_PATH%icon.ico ^
/embed
