@ECHO OFF

:: Runs the Daily_Checkup.py program.

:: Set the cmd window title.
TITLE Spotify

:: Move working directory to Spotify.
:: This allows us to use our local credientials files.
cd /d "C:\Users\micah\PycharmProjects\Spotify"

:: Execute the program.
:: Because we write errors and relevant changes
:: to a log file, we do not need to keep this window open.
python Daily_Checkup.py
