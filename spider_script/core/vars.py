class SpiderVars:
    def __init__(self):
        self.vars = {}
        self.vars['true'] = True
        self.vars['false'] = False
        self.vars['yes'] = True
        self.vars['no'] = False

    def set(self, name, value):
        if value is None:
            value = 0
        try:
            if '.' in str(value):
                value = float(value)
            else:
                value = int(value)
        except:
            value = str(value).strip("'\"")
        self.vars[name] = value

    def get(self, name):
        return self.vars.get(name, None)

    def exists(self, name):
        return name in self.vars