@echo off

SET Instance=localhost
SET DbName=oneroster
SET Passwd=***
SET Opt=-b -s, -W -h -1 -o

rem manifest
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\manifest.sql %Opt% output\manifest.csv

rem academicSessions
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\academicSessions.sql %Opt% output\academicSessions.csv

rem classes
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\classes.sql %Opt% output\classes.csv

rem courses
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\courses.sql %Opt% output\courses.csv

rem enrollments
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\enrollments.sql %Opt% output\enrollments.csv

rem orgs
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\orgs.sql %Opt% output\orgs.csv

rem roles
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\roles.sql %Opt% output\roles.csv

rem users
sqlcmd -S %Instance% -d %DbName% -U sa -P %Passwd% -i query\users.sql %Opt% output\users.csv

rem UTF-8へのコンバートは別ツールで実行

pause