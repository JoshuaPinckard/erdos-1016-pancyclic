Dim sh: Set sh = CreateObject("WScript.Shell")
Dim cmd: cmd = "cmd.exe /c """"C:\Users\ToolsEnabled-Dev\Desktop\erdos1016\search\shapecsp\_probe\probe.cmd"""""
WScript.Quit sh.Run(cmd, 0, True)
