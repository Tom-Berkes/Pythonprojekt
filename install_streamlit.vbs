' Installiert Streamlit per pip, zeigt Ergebnis in MessageBoxen an.
Option Explicit
Dim sh, rc
Set sh = CreateObject("Wscript.Shell")

' Prüfen, ob python gefunden wird
rc = sh.Run("cmd /c python --version", 0, True)
If rc <> 0 Then
    rc = sh.Run("cmd /c py --version", 0, True)
    If rc <> 0 Then
    MsgBox "Python wurde nicht gefunden. Bitte Python 3.11+ installieren und nochmals versuchen.", vbCritical, "Installation abgebrochen"
    WScript.Quit 1
    End If
End If

' Streamlit installieren (nutzt python -m pip; fällt zurück auf py -m pip)
rc = sh.Run("cmd /c python -m pip install --upgrade pip && python -m pip install streamlit", 1, True)
If rc <> 0 Then
    rc = sh.Run("cmd /c py -m pip install --upgrade pip && py -m pip install streamlit", 1, True)
End If

If rc = 0 Then
    MsgBox "Streamlit wurde erfolgreich installiert. Sie können das Dashboard mit:" & vbCrLf & _
        "Doppelklick auf start_dashboard.vbs starten.", vbInformation, "Installation abgeschlossen"
Else
    MsgBox "Installation fehlgeschlagen. Bitte Konsole prüfen und ggf. erneut versuchen.", vbCritical, "Fehler"
    WScript.Quit 1
End If