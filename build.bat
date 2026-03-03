@echo off
echo === Skizzenwelt Build ===
echo.
echo Installiere Abhaengigkeiten...
pip install pygame-ce pyinstaller
echo.
echo Erstelle .exe...
pyinstaller --onedir --windowed --name Skizzenwelt main.py
echo.
echo Fertig! Die .exe befindet sich in: dist\Skizzenwelt\
echo Diesen Ordner kannst du als ZIP teilen.
pause
