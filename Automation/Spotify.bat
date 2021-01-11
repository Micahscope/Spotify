@echo off
setlocal enabledelayedexpansion

rem Runs the Daily_Checkup.py program. After
rem completion, it checks the log file to
rem determine what has happened. If nothing
rem happened, we close the cmd window. Otherwise,
rem we call PAUSE and write to terminal what happened.

rem Set a %today% variable to hold the formatting of
rem the date also used in the log file.
rem Stored as MM/DD/YY.

set today=%date:~4,5%/%date:~12,2%

rem Define %isToday% as a boolean variable to
rem hold when we found the most recent (today's)
rem entry to the log file. Then, we know based on
rem the log file formatting, the next line holds
rem the relevant information as to what process
rem occurred.

set isToday=0

rem Store %default% as the string we search for.
rem If our log file says "No requests completed at this time",
rem we want our cmd window to close. Otherwise, we should
rem print what occurred.

set default=No requests completed at this time.

rem Set the cmd window title to depict its purpose.

title Spotify

rem Move working directory to Spotify files.
rem This allows us to use our local credientials files,
rem and to access our log file later.

pushd "C:\Users\micah\PycharmProjects\Spotify"

rem Execute the program.
rem In doing so, our log file will be
rem written to.

python Daily_Checkup.py

rem If we did nothing, close the program.
rem Otherwise, leave the cmd window open
rem and show what happened during execution.

rem Loop through the lines of the log file.
rem When we find a line showing the date and time
rem of the log entry that matches the current date,
rem mark that isToday is true. Then, on the next loop
rem cycle, we will read the data entry. If nothing
rem happened, we exit the program. If something
rem did happen, we write it to the cmd window and
rem keep it persistent until the user closes it.

for /f "tokens=*" %%a in (Local_Files\Log.txt) do (

  if !isToday!==1 (
    echo %%a|find "%default%" >nul
    if errorlevel 1 (echo %%a
    start "" /wait notepad.exe Local_Files\Log.txt
    goto :Halt
    )
  )

  echo %%a|find "%today%" >nul
  if not errorlevel 1 set isToday=1

)

goto :Halt

:Wait

pause

:Halt
