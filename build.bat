pyinstaller --noconfirm wswhud_app.spec
del /F *.pyc wswhud_app.exe
move dist\wswhud_app.exe .
rmdir /S /Q build dist
