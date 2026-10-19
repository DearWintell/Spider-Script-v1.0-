import time
import tkinter as tk
from core.vars import SpiderVars
from core.parser import SpiderParser
from core.errors import SpiderError

class SpiderExecutor:
    def __init__(self):
        self.vars = SpiderVars()
        self.parser = SpiderParser()
        self.root = None
        self.canvas = None
        self.elements = {}
        self.textv_bindings = {}
        self.window_created = False

    def execute_line(self, line, line_num):
        line = line.strip()
        if not line or self.parser.is_comment(line):
            return

        cmd = self.parser.extract_command(line)
        if not cmd:
            return
            
        params_str = self.parser.extract_params_string(line)
        params = self.parser.parse_params(params_str)

        if cmd == 'var':
            self.cmd_var(params, line_num)
        elif cmd == 'print':
            self.cmd_print(params, line_num)
        elif cmd == 'title':
            self.cmd_title(params, line_num)
        elif cmd == 'button':
            self.cmd_button(params, line_num)
        elif cmd == 'wait':
            self.cmd_wait(params, line_num)
        elif cmd == 'check':
            self.cmd_check(params, line_num)
        elif cmd == 'bind':
            self.cmd_bind(params, line_num)
        elif cmd == 'window':
            self.cmd_window(params, line_num)
        elif cmd == 'text':
            self.cmd_text(params, line_num)
        elif cmd == 'textv':
            self.cmd_textv(params, line_num)
        elif cmd == 'shape':
            self.cmd_shape(params, line_num)
        elif cmd == 'move':
            self.cmd_move(params, line_num)
        elif cmd == 'clear':
            self.cmd_clear(params, line_num)

    def cmd_window(self, params, line_num):
        if self.window_created:
            return
        
        title = params.get('title', 'Spider Script')
        width = params.get('width', 800)
        height = params.get('height', 600)
        bg = params.get('bg', 'white')
        
        try:
            width = int(width)
            height = int(height)
        except:
            width = 800
            height = 600
        
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg)
        self.canvas.pack()
        
        self.window_created = True
        print(f"[SPIDER] Window created: {width}x{height}")

    def cmd_text(self, params, line_num):
        if not self.canvas:
            return
        
        text = params.get('text', '')
        x = params.get('x', 10)
        y = params.get('y', 10)
        color = params.get('color', 'black')
        size = params.get('size', 12)
        
        try:
            x = int(x)
            y = int(y)
            size = int(size)
        except:
            x, y, size = 10, 10, 12
        
        self.canvas.create_text(x, y, text=text, fill=color, 
                                font=('Arial', size), anchor='nw')

    def cmd_textv(self, params, line_num):
        if not self.canvas:
            return
        
        var_name = params.get('var', '')
        value = self.vars.get(var_name)
        if value is None:
            value = '0'
        
        x = params.get('x', 10)
        y = params.get('y', 10)
        color = params.get('color', 'black')
        size = params.get('size', 12)
        
        try:
            x = int(x)
            y = int(y)
            size = int(size)
        except:
            x, y, size = 10, 10, 12
        
        text_id = self.canvas.create_text(x, y, text=str(value), fill=color,
                                          font=('Arial', size), anchor='nw')
        
        if var_name not in self.textv_bindings:
            self.textv_bindings[var_name] = []
        self.textv_bindings[var_name].append({
            'id': text_id,
            'x': x,
            'y': y,
            'color': color,
            'size': size
        })

    def update_textv(self, var_name):
        if var_name not in self.textv_bindings:
            return
        
        value = self.vars.get(var_name)
        if value is None:
            value = '0'
            
        for item in self.textv_bindings[var_name]:
            self.canvas.delete(item['id'])
            new_id = self.canvas.create_text(
                item['x'], item['y'], 
                text=str(value), 
                fill=item['color'],
                font=('Arial', item['size']), 
                anchor='nw'
            )
            item['id'] = new_id

    def cmd_shape(self, params, line_num):
        if not self.canvas:
            return
        
        shape_type = params.get('type', 'square')
        x = params.get('x', 100)
        y = params.get('y', 100)
        color = params.get('color', 'red')
        size = params.get('size', 50)
        elem_id = params.get('id', '')
        
        try:
            x = int(x)
            y = int(y)
            size = int(size)
        except:
            x, y, size = 100, 100, 50
        
        if shape_type == 'circle':
            shape_id = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')
        else:
            shape_id = self.canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline='')
            
        if elem_id:
            self.elements[elem_id] = {
                'id': shape_id,
                'x': x,
                'y': y,
                'size': size
            }
            print(f"[SPIDER] Shape '{elem_id}' created at ({x}, {y}) [ID: {shape_id}]")

    def cmd_move(self, params, line_num):
        if not self.canvas:
            print("[SPIDER] ERROR: No canvas")
            return
        
        elem_id = params.get('id', '')
        print(f"[SPIDER] Move command: id='{elem_id}', params={params}")
        print(f"[SPIDER] Available elements: {list(self.elements.keys())}")
        
        if not elem_id or elem_id not in self.elements:
            print(f"[SPIDER] ERROR: Element '{elem_id}' not found")
            return
        
        element = self.elements[elem_id]
        shape_id = element['id']
        
        dx = 0
        dy = 0
        
        for key, value in params.items():
            if key == 'id':
                continue
                
            if key == 'x':
                val = str(value)
                if val.startswith('+'):
                    dx = int(val[1:]) if len(val) > 1 else 0
                elif val.startswith('-'):
                    dx = -int(val[1:]) if len(val) > 1 else 0
                else:
                    try:
                        new_x = int(val)
                        coords = self.canvas.coords(shape_id)
                        dx = new_x - coords[0]
                    except:
                        pass
                        
            elif key == 'y':
                val = str(value)
                if val.startswith('+'):
                    dy = int(val[1:]) if len(val) > 1 else 0
                elif val.startswith('-'):
                    dy = -int(val[1:]) if len(val) > 1 else 0
                else:
                    try:
                        new_y = int(val)
                        coords = self.canvas.coords(shape_id)
                        dy = new_y - coords[1]
                    except:
                        pass
        
        print(f"[SPIDER] Moving by dx={dx}, dy={dy}")
        
        if dx != 0 or dy != 0:
            self.canvas.move(shape_id, dx, dy)
            self.canvas.update()
            
            coords = self.canvas.coords(shape_id)
            element['x'] = coords[0]
            element['y'] = coords[1]
            
            print(f"[SPIDER] Moved '{elem_id}' to ({coords[0]}, {coords[1]})")
        else:
            print(f"[SPIDER] No movement (dx=0, dy=0)")

    def cmd_clear(self, params, line_num):
        if self.canvas:
            self.canvas.delete('all')
            self.elements.clear()
            self.textv_bindings.clear()
            print("[SPIDER] Canvas cleared")

    def cmd_button(self, params, line_num):
        text = params.get('text', 'Button')
        action = params.get('action', '')
        
        if self.root:
            x = params.get('x', 10)
            y = params.get('y', 10)
            width = params.get('width', 100)
            height = params.get('height', 30)
            bg = params.get('bg', '#238636')
            fg = params.get('color', 'white')
            
            try:
                x = int(x)
                y = int(y)
                width = int(width)
                height = int(height)
            except:
                x, y, width, height = 10, 10, 100, 30
            
            btn = tk.Button(self.root, text=text, bg=bg, fg=fg,
                           command=lambda a=action: self.execute_action(a, line_num))
            btn.place(x=x, y=y, width=width, height=height)
            print(f"[SPIDER] Button '{text}' created")

    def cmd_var(self, params, line_num):
        name = params.get('name', '')
        value = params.get('value', '')
        if not name:
            SpiderError.show('MISSING_PARAM', line_num, '', 'var requires name')
        self.vars.set(name, value)
        print(f"[SPIDER] var '{name}' = {self.vars.get(name)}")

    def cmd_print(self, params, line_num):
        text = params.get('text', '')
        print(f"[SPIDER] {text}")

    def cmd_title(self, params, line_num):
        text = params.get('text', '')
        print(f"\n{'='*50}\n  {text}\n{'='*50}\n")

    def cmd_wait(self, params, line_num):
        t = params.get('time', 1)
        try:
            seconds = float(t)
            if self.root:
                self.root.after(int(seconds * 1000))
            else:
                time.sleep(seconds)
        except:
            pass

    def cmd_check(self, params, line_num):
        cond = params.get('what', '')
        yes = params.get('yes', '')
        no = params.get('no', '')
        if self.check_condition(cond):
            if yes:
                self.execute_action(yes, line_num)
        else:
            if no:
                self.execute_action(no, line_num)

    def cmd_bind(self, params, line_num):
        key = params.get('key', '')
        action = params.get('action', '')
        if self.root:
            def callback(event, act=action):
                self.execute_action(act, line_num)
            
            self.root.bind(f'<KeyPress-{key}>', callback)
            self.root.bind(f'<KeyPress-{key.upper()}>', callback)
            print(f"[SPIDER] Bind '{key}' -> {action}")

    def execute_action(self, action_str, line_num):
        if not action_str:
            return
        
        print(f"[SPIDER] Executing action: {action_str}")
        
        if action_str.startswith('move('):
            params_str = action_str[5:-1]
            params = self.parser.parse_params(params_str)
            self.cmd_move(params, line_num)
        else:
            actions = self.parser.parse_action(action_str)
            for act_type, var1, var2 in actions:
                if act_type == 'assign':
                    val = self.parse_value(var2)
                    self.vars.set(var1, val)
                    self.update_textv(var1)
                elif act_type == 'add':
                    v1 = self.vars.get(var1)
                    if v1 is None:
                        v1 = 0
                    v2 = self.parse_value(var2)
                    result = v1 + v2
                    self.vars.set(var1, result)
                    self.update_textv(var1)
                elif act_type == 'sub':
                    v1 = self.vars.get(var1)
                    if v1 is None:
                        v1 = 0
                    v2 = self.parse_value(var2)
                    result = v1 - v2
                    self.vars.set(var1, result)
                    self.update_textv(var1)

    def parse_value(self, val_str):
        val_str = str(val_str).strip()
        try:
            if '.' in val_str:
                return float(val_str)
            return int(val_str)
        except:
            return val_str

    def check_condition(self, cond):
        for name in self.vars.vars:
            if name in cond:
                cond = cond.replace(name, str(self.vars.get(name)))
        try:
            return eval(cond)
        except:
            return False

    def run_loop(self):
        if self.root:
            self.root.mainloop()