@echo off
: Shim to shell script from non-bash environment

sh "%~dp0\%~n0" %*
exit /b %errorlevel%
