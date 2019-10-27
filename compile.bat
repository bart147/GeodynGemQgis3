@echo off
call "C:\PROGRA~1\QGIS3~1.4\bin\o4w_env.bat"
call "C:\PROGRA~1\QGIS3~1.4\bin\qt5_env.bat"
call "C:\PROGRA~1\QGIS3~1.4\bin\py3_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc
pause

