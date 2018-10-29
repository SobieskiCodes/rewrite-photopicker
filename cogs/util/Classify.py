import requests


def add_class(name, methods, classes=''):
    methods = '\n'.join(methods)
    classes = '\n'.join(classes)
    x = f'''{classes}\nclass {name}:\n\tdef __init__(self,items):\n\t\tif items:\n\t\t\tself.items=items\n\t\telse:\n\t\t\tself.items=dict()\n\t{methods}'''
    return x


def new_method(name, output, desc):
    x = f"""\n\t@property\n\tdef {name}(self):\n\t\t'''{desc}. If no data is available, an empty dict or None is returned'''\n\t\treturn {output}\n"""
    return x


def clean(string):
    if not string:
        string = '_'
    if string[0].isdigit():
        string = f"_{string}"
    return string.replace(' ', '_')


class Classify_API:

    def __init__(self, class_name, api_json, names=None):
        initial_list = False
        if names:
            self.class_names = names
        else:
            self.class_names = []
        self.name = clean(class_name)
        while self.name in self.class_names:
            self.name = f'_{self.name}'
        self.class_names.append(self.name)
        self.classes = []
        self.methods = []
        if isinstance(api_json, list):
            if all(isinstance(item, dict) for item in api_json):
                api_json = {'list': api_json}
                initial_list = True
            else:
                output = '''self.items'''
                desc = f'''will return {type(api_json)}'''
                self.methods.append(f'''{new_method('list',output,desc)}''')

        if isinstance(api_json, dict):
            for k, v in api_json.items():
                if v and isinstance(v, dict):
                    self.__is_dict(k, v)
                elif v and isinstance(v, list) and all(isinstance(item, dict) for item in v):
                    self.__is_list(k, v, initial_list=initial_list)
                else:
                    output = f'''self.items.get('{k}',dict())'''
                    desc = f'''Will return {type(v)}'''
                    self.methods.append(f'''{new_method(clean(k),output,desc)}''')

    def __is_dict(self, k, v):
        new_class = clean(k).title()
        while new_class in self.class_names:
            new_class = f'_{new_class}'
        output = f"{new_class}(self.items.get('{k}',dict()))"
        desc = f'Will return class {new_class}()'
        self.methods.append(f'''{new_method(clean(k),output,desc)}''')
        new_class = Classify_API(new_class, v, names=self.class_names)
        self.classes.append(new_class.txt)
        self.class_names = new_class.get_names

    def __is_list(self, k, v, initial_list=False):
        new_class = clean(k).title()
        while new_class in self.class_names:
            new_class = f'_{new_class}'
        desc = f'''Will return a generator with instances of class {new_class}()'''
        if not initial_list:
            output = f'''({new_class}(item) for item in self.items.get('{k}',dict()) if item)'''
        else:
            output = f'''({new_class}(item) for item in self.items if item)'''
        self.methods.append(f'''{new_method(clean(k),output,desc)}''')
        new_class = Classify_API(new_class, v[0], names=self.class_names)
        self.classes.append(new_class.txt)
        self.class_names = new_class.get_names

    @property
    def txt(self):
        return add_class(self.name.title(), self.methods, self.classes)

    @property
    def get_names(self):
        return self.class_names

    @classmethod
    def fromURL(cls, class_name, url, headers: dict = None):
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            _json = r.json()
            return cls(class_name, _json)
        else:
            print(f'Failed to retrieve JSON: Status {r.status_code}')

    @property
    def create(self):
        with open(f'{self.name.lower()}.py', 'w+') as f:
            f.write(add_class(self.name.title(), self.methods, self.classes))
            f.close()
        print(f'{self.name.lower()}.py has been created!')