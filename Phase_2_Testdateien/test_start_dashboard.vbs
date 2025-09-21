' test_start_dashboard.vbs
Set sh = CreateObject("Wscript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
sh.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)
' Eigener Port 8511, um Konflikte zu vermeiden
sh.Run "cmd /c start """" ""http://localhost:8511"" & python -m streamlit run test_dashboard.py --server.headless true --server.address=localhost --server.port=8511", 0, False