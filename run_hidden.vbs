Set WshShell = CreateObject("WScript.Shell")
currentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDirectory

' Tenta encontrar o Python no sistema
pythonPath = "python"
On Error Resume Next
WshShell.Run "where python", 0, True
If Err.Number <> 0 Then
    ' Se não encontrar python no PATH, tenta caminhos comuns
    If WshShell.FileExists("C:\Python39\python.exe") Then
        pythonPath = """C:\Python39\python.exe"""
    ElseIf WshShell.FileExists("C:\Python310\python.exe") Then
        pythonPath = """C:\Python310\python.exe"""
    End If
End If
On Error Goto 0

scriptPath = """" & currentDirectory & "\iniciar.py"""
WshShell.Run "cmd /c " & pythonPath & " " & scriptPath, 0, False
