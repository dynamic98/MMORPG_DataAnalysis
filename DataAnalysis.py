import os
import json

class ParticipantData:
    def __init__(self, participant:str):
        self.participant = participant
        self.log_list = {}
    
    def add_log(self, session, log):
        if session not in self.log_list:
            self.log_list[session] = []
        self.log_list[session].append(log)


class Log:
    def __init__(self, session:int, cycles:dict, game_result:str):
        self.session = session
        self.cycles = cycles
        self.log_stack = {'Mage':self.get_log_stack_dict(), 'Priest':self.get_log_stack_dict(), 
                          'MeleeDealer':self.get_log_stack_dict(), 'Tanker':self.get_log_stack_dict()}
        self.log = {'Mage':self.get_log_dict(), 'Priest':self.get_log_dict(), 
                    'MeleeDealer':self.get_log_dict(), 'Tanker':self.get_log_dict()}
        self.result = game_result

        self.processing()
        
    def get_log(self):
        return self.log
    
    def make_log(self):
        log_stack = self.get_log_stack()
        for agent in log_stack:
            speed = self.get_speed(log_stack[agent]['position'])
            distance = self.get_distance(self.cycles, agent)
            health = self.get_health(log_stack[agent]['health'])
            skillCount = self.get_skillCount(log_stack[agent]['skillInfo'])
            dps = self.get_dps(log_stack[agent]['skillInfo'])
            bosskill = self.get_bosskill(log_stack[agent]['skillInfo'])
            death = self.get_death(log_stack[agent]['state'])
            
            
            
    
    
    def get_log_stack_dict(self):
        log_stack_dict = {'health':[], 'shield':[], 'skillInfo':[], 'position':[], 'state':[]}
        return log_stack_dict
    
    def get_log_dict(self):
        log_dict = {'speed':None, 'distance':None, 'health':None, 'skillCount':None, 'dps':None, 'bosskill':None, 'death':None, 'distanceWhenSkill':None,
            'totalPath':None, 'takeShield':None, 'skillFrequency':None, 'distanceBTNagent':None, 'attackCount':None, 'attackLowHealth':None}
        return log_dict
    
    def get_log_stack(self):
        return self.log_stack
    
    def processing(self):
        for cycle in self.cycles:
            self.processing_cycle(cycle)
    
    def processing_cycle(self, cycle:dict):
        for agent in cycle:
            if agent != 'PatchwerkAgent':
                self.processing_agent(cycle[agent], agent)
    
    def processing_agent(self, agent_cycle:dict, agent_name:str):
        if agent_cycle['health'] != None:
            self.log_stack[agent_name]['health'].append(agent_cycle['health'])
        if agent_cycle['shield'] != None:
            self.log_stack[agent_name]['shield'].append(agent_cycle['shield'])
        if agent_cycle['skillInfo'] != None:
            self.log_stack[agent_name]['skillInfo'].append(agent_cycle['skillInfo'])
        if agent_cycle['position'] != None:
            self.log_stack[agent_name]['position'].append(agent_cycle['position'])
        if agent_cycle['state'] != None:
            self.log_stack[agent_name]['state'].append(agent_cycle['state'])
    


class Log_cycle:
    def __init__(self, data:list):
        self.data = data
        self.cycles = []
        self.dead_possibility = {'Mage':0, 'Priest':0, 'MeleeDealer':0, 'Tanker':0, 'PatchwerkAgent':0}
        self.agent_list = ['Mage', 'Priest', 'MeleeDealer', 'Tanker', 'PatchwerkAgent']
        self.dead_agent = []
        self.current_cycle = self.make_cycle()
        self.current_cycle_filled = set()
        self.current_cycle_num = 0
        self.dead_threshold = 10
        self.result = None
        self.read_data()
    
    def get_data(self):
        return self.data
    
    def get_cycle(self):
        return self.cycles

    def make_cycle(self):
        process = {'state': None, 'position': None, 'health': None, 'shield': None, 'skillInfo': None}
        cycle = {'Mage': self.get_process(), 'Priest': self.get_process(), 'MeleeDealer': self.get_process(), 'Tanker': self.get_process(), 'PatchwerkAgent': self.get_process()}
        return cycle

    def get_process(self):
        process = {'state': None, 'position': None, 'health': None, 'shield': None, 'skillInfo': None}
        return process

        

    def read_data(self):
        data = self.get_data()
        for line in data:
            line_type = self.check_line(line)
            if line_type == 'Movement':
                self.CheckAgentDead()
                if self.CycleIsFilled():
                    self.cycles.append(self.current_cycle)
                    self.current_cycle = self.make_cycle()
                    self.current_cycle_filled = set()
                    self.current_cycle_num += 1
                    
                agent_name, state, position, health, shield = self.Movement(line)
                self.current_cycle_filled.add(agent_name)
                self.UpdateDeadPossibility(agent_name)
                self.current_cycle[agent_name]['state'] = state
                self.current_cycle[agent_name]['position'] = position
                self.current_cycle[agent_name]['health'] = health
                self.current_cycle[agent_name]['shield'] = shield
                
            elif line_type == 'Skill':
                agent_name, this_agent, target_agent, skill_name, this_agent_position, target_agent_position = self.Skill(line)
                self.current_cycle[agent_name]['skillInfo'] = {"this_agent":this_agent, "target_agent":target_agent, "skill_name":skill_name, 
                                                              "this_position":this_agent_position, "target_position":target_agent_position}
            elif line_type == 'Game Result':
                self.result = self.GameResult(line)    
    
    def check_line(self, line:str):
        info = line.split(":")[3].strip()
        if info.startswith("Game Result"):
            return "Game Result"
        elif info.startswith("Skill"):
            return "Skill"
        else:
            return "Movement"
    
    def Movement(self, line:str):
        info = line.split(":")[3].strip().split("/")
        agent_name = info[0]
        state = info[1]
        position = self.getPosition(info[2])
        health = float(info[3])
        shield = float(info[4])
        return agent_name, state, position, health, shield
        
    def Skill(self, line:str):
        info = line.split(":")[3].strip().split("/")
        agent_name = info[0].split(" ")[2]
        this_agent = self.getAgentByID(info[1])
        target_agent = self.getAgentByID(info[2])
        skill_name = info[3]
        this_agent_position = self.getPosition(info[4])
        target_agent_position = self.getPosition(info[5])
        return agent_name, this_agent, target_agent, skill_name, this_agent_position, target_agent_position
    
    def GameResult(self, line:str):
        info = line.split(":")[4].strip()
        if info == 'EnemyWin':
            return 'EnemyWin'
        elif info == 'PlayerWin':
            return 'PlayerWin'
        else:
            return "Draw"

    def getAgentByID(self, agent_id:str):
        if agent_id == '0':
            return "Mage"
        elif agent_id == '1':
            return "Priest"
        elif agent_id == '2':
            return "MeleeDealer"
        elif agent_id == '3':
            return "Tanker"
        elif agent_id == '100':
            return "PatchwerkAgent"
        else:
            return None
    
    def get_game_result(self):
        return self.result
    
    def UpdateDeadPossibility(self, agent_name:str):
        for agent in self.dead_possibility:
            if agent != agent_name:
                self.dead_possibility[agent] += 1
            else:
                self.dead_possibility[agent_name] = 0
                
    def CheckAgentDead(self):
        for agent in self.dead_possibility:
            if self.dead_possibility[agent] >= self.dead_threshold:
                if agent in self.agent_list:
                    self.agent_list.remove(agent)
                    self.dead_agent.append(agent)
    
    def CycleIsFilled(self):
        alive_agent = sorted(self.agent_list.copy())
        filled_agent = sorted(list(self.current_cycle_filled).copy())
        if alive_agent == filled_agent:
            return True
        else:
            return False
        
    def getPosition(self, position_str:str):
        position_str = position_str.strip("()").split(",")
        position = [float(value) for value in position_str]
        return position

if __name__ == "__main__":
    dataPath = "Log"
    dataExample = "2023-11-11 17-47-39_gameLog.txt"
    with open(os.path.join(dataPath, dataExample), "r") as f:
        contents = f.read()
        lines = contents.split("\n")[:-1]
        new_log_cycle = Log_cycle(lines)
        log_cycle = new_log_cycle.get_cycle()
        game_result = new_log_cycle.get_game_result()
        new_log = Log(1, log_cycle, game_result)
        
        with open("test.json", "w") as p:
            json.dump(new_log_cycle.get_cycle(), p, indent=4)
            
        with open("test2.json", "w") as p:
            json.dump(new_log.log_stack, p, indent=4)
        
    # for participant in os.listdir(dataPath):
    #     p_logPath = os.path.join(dataPath, participant, "log")
    #     for log in os.listdir(p_logPath):
    #         with open(os.path.join(p_logPath, log), "r") as f:
    #             contents = f.read()
    #             lines = contents.split("\n")

                