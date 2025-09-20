' Start-Script: setzt Arbeitsverzeichnis, öffnet Browser und startet Streamlit im Hintergrund.
Set sh = CreateObject("Wscript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Arbeitsverzeichnis = Ordner, in dem dieses Skript liegt (reproduzierbare Pfade).
sh.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)

' Erst Browser öffnen, dann Streamlit headless starten (Port 8501), ohne Konsolenfenster (0).
sh.Run "cmd /c start """" ""http://localhost:8501"" & python -m streamlit run dashboard.py --server.headless true --server.address=localhost --server.port=8501", 0, False