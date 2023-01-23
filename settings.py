import os
file = "settings.txt"

def readSettings(setting):
    with  open(file, mode='r', encoding='utf-8') as f:
        content = f.read()
    data = content.split(";")
    status = ""
    for i in data:
        if setting in i:
            status = i.split("=")[1]
    return status

def modifySettings(setting, value):
        

    with  open(file, mode='r', encoding='utf-8') as f:
        content = f.read()
    data = content.split(";") 
    newSettings = []
    for i in data:
        if setting in i:
            text = setting + "=" + value
            newSettings.append(text)
        else:
            newSettings.append(i)            
    with  open(file, mode='w', encoding='utf-8') as f:
        text = ""
        for i in newSettings:
            if i != "":
                text += i + ";"
        f.write(text)


