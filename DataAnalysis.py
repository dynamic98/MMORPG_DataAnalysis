import os

class ParticipantData:
    def __init__(self, participant):
        self.participant = participant
        self.log_list = {}
    
    def add_log(self, session, log):
        if session not in self.log_list:
            self.log_list[session] = []
        self.log_list[session].append(log)

class Log:
    def __init__(self, session, data):
        self.session = session
        self.data = data
        agent_dict = {'mage':0, 'priest':0, 'meleeDealer':0, 'tanker':0}
        self.log = {'speed':agent_dict, 'distance':agent_dict, 'health':agent_dict, 'skillCount':agent_dict,
                    'dps': agent_dict, 'bosskill': agent_dict, 'death': agent_dict, 'distanceWhenSkill': agent_dict,
                    'totalPath': agent_dict, 'takeShield': agent_dict, 'skillFrequency': agent_dict, 
                    'distanceBTNagent': agent_dict, 'attackCount': agent_dict, 'attackLowHealth': agent_dict}
    
    def get_data(self):
        return self.data








if __name__ == "__main__":
    dataPath = "C:/Users/scilab/Desktop/잡무/게임 과제/2차연도/게임플레이데이터수집/실험자데이터"

    for participant in os.listdir(dataPath):
        p_logPath = os.path.join(dataPath, participant, "log")
        for log in os.listdir(p_logPath):
            with open(os.path.join(p_logPath, log), "r") as f:
                contents = f.read()
                lines = contents.split("\n")
                