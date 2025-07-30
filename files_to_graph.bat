@echo off
setlocal enabledelayedexpansion

REM Проверка аргумента
if "%~1"=="" (
    echo Usage: %~nx0 ^<path/to/directory^>
    exit /b 1
)

REM Обработка пути к директории
set "INPUT_DIR=%~f1"
if not exist "%INPUT_DIR%\" (
    echo Directory "%INPUT_DIR%" does not exist
    exit /b 1
)

REM Цикл по всем файлам в директории
for %%F in ("%INPUT_DIR%\*") do (
    set "INPUT_FILE=%%~fF"
    set "FILE_NAME=%%~nF"
    set "OUTPUT_DIR=%%~dpF"

    echo Processing %%~nxF...

    REM Команды Joern
    echo Parsing !INPUT_FILE!...
    cmd /c joern-parse "!INPUT_FILE!" -o "cpg\!FILE_NAME!.bin"
    if errorlevel 1 (
        echo Failed to parse !INPUT_FILE!
        goto :next_file
    )

    echo Exporting representations...
    if not exist "repr_all\" mkdir "repr_all"
    cmd /c joern-export "cpg\!FILE_NAME!.bin" --repr all --out "repr_all\!FILE_NAME!"
    if not exist "repr_pdg\" mkdir "repr_pdg"
    cmd /c joern-export "cpg\!FILE_NAME!.bin" --repr pdg --out "repr_pdg\!FILE_NAME!"

    REM Объединение графов
    echo Merging graphs...
    if not exist "graphs\" mkdir "graphs"
    python merge.py --pdg "repr_pdg\!FILE_NAME!\*-pdg.dot" --ref "repr_all\!FILE_NAME!\export.dot" -o "graphs\!FILE_NAME!.dot"

    echo Successfully processed %%~nxF
    echo ----------------------------------------
)

echo All files processed
endlocal