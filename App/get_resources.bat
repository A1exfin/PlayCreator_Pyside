set "root_dir=%~dp0..\"
%root_dir%venv\Scripts\pyside6-rcc.exe %~dp0Interface\Interface.qrc -o %~dp0Interface_rc.py