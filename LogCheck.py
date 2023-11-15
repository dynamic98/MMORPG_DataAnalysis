import os
import shutil

def checkLog(textfile_path):
    with open(textfile_path, "r") as f:
        line = f.read()
        if "PlayerWin" in line:
            return True
        else:
            return False

fileName = 1
save_path = "C:/Users/scilab/MMORPG-UNITY/RaidEnv/Assets/Resources/PlayLog"
log_total_path = "C:/Users/scilab/Desktop/잡무/게임 과제/2차연도/게임플레이데이터수집/실험자데이터"
for participant in os.listdir(log_total_path):
    log_path = os.path.join(log_total_path, participant, "Log")
    for log in os.listdir(log_path):
        textfile_path = os.path.join(log_path, log)
        bool_result = checkLog(os.path.join(log_path, log))
        if bool_result:
            save_filepath = os.path.join(save_path, str(fileName)+".txt")
            shutil.copy(textfile_path, save_filepath)
            fileName += 1
    

