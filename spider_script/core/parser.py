import re

class SpiderParser:
    @staticmethod
    def parse_params(param_str):
        params = {}
        if not param_str:
            return params
        
        pattern = r"(\w+)=('[^']*'|\"[^\"]*\"|\S+)"
        matches = re.findall(pattern, param_str)
        
        for key, value in matches:
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            else:
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except:
                    pass
            params[key] = value
            
        return params

    @staticmethod
    def parse_action(action_str):
        actions = []
        if not action_str:
            return actions
            
        if action_str.startswith('move('):
            return [('move', action_str, '')]
            
        for act in action_str.split(';'):
            act = act.strip()
            if not act:
                continue
            if '=' in act:
                var, val = act.split('=')
                var = var.strip()
                val = val.strip()
                actions.append(('assign', var, val))
            elif '+' in act:
                parts = act.split('+')
                var1 = parts[0].strip()
                var2 = parts[1].strip()
                actions.append(('add', var1, var2))
            elif '-' in act:
                parts = act.split('-')
                var1 = parts[0].strip()
                var2 = parts[1].strip()
                actions.append(('sub', var1, var2))
        return actions

    @staticmethod
    def is_comment(line):
        line = line.strip()
        return line.startswith('/') or line.startswith('#')

    @staticmethod
    def extract_command(line):
        line = line.strip()
        if '(' in line:
            return line[:line.index('(')]
        return None

    @staticmethod
    def extract_params_string(line):
        line = line.strip()
        start = line.find('(')
        end = line.rfind(')')
        if start != -1 and end != -1:
            return line[start+1:end]
        return ''