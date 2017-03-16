#!/usr/bin/env python3

#
# comandline interface for groceryDatabase.py
#

import os
import sys
import textwrap
import groceryDatabase
import terminal

_commands = {}

def command(function):
    _commands[function.__name__] = function.__doc__
    return function

class gdatabaseUtility:
    def __init__(self, command, arg=""):
        """ 
        Initalize gdatabasUtility
        
        Parameters
        ----------
        command : string
            The subcommand to run.
        arg : string
            Arguments for the command.
        """
        self.database = groceryDatabase.groceryDatabase()
        
        function = None

        try:
            if command not in _commands:
                raise AttributeError
            
            function = getattr(self, command)
        except AttributeError:
            print("ERROR: \"" + command + "\" is not a valid subcommand. See 'gdata help'")
 
        try:
            function(arg)
        except KeyboardInterrupt:
            #close program silently
            print("\n")
            
    @command
    def list(self, arg):
        """ 
        List the contents of the database.
        """
        print(self.database)

    @command
    def add(self, arg):
        """ 
        Add an entry to database.
        
        Examples: 
            add name, tag,...,tag: trait,value,unit ...
            add name: trait,value trait,value,unit ...
            add name, tag,...,tag
            add name
            add
        """

        name = None
        tags = None
        attributes = None

        if len(arg.strip()) != 0:
            arg = arg.split(":")
            if len(arg) == 1:
                name_tags, attributes = arg[0], None
            elif len(arg) == 2:
                arg[1] = arg[1].strip()
                if len(arg[1].split()) == 0:
                    arg[1] = None
                name_tags, attributes = arg[0], arg[1]
            else:
                print("Malformed command 1")
                return

            name_tags = name_tags.split(",", 1)
            if len(name_tags) == 1:
                name = name_tags[0]
                tags = None
            else:
                name = name_tags[0]
                tags = [tag.strip() for tag in name_tags[1].split(",") if len(tag.strip()) != 0]
                if len(tags) == 0:
                    tags = None
            
            if attributes is not None:
                attributes = attributes.split(" ")
                for i, attribute in enumerate(attributes):
                    attribute = [trait.strip() for trait in attribute.split(",") if len(trait.strip()) != 0]
                    if len(attribute) == 2:
                        attributes[i] = (attribute[0], self._float_eval(attribute[1]), None)
                    elif len(attribute) == 3:
                        if len(attribute[2].strip()) == 0:
                            attribute[2] = None
                        attributes[i] = (attribute[0], self._float_eval(attribute[1]), attribute[2])
                    else:
                        print("Malformed command 3")
                        return

        with terminal.terminal() as term:
            while name is None:
                name = str(term.input("Enter entry name: ", self._tabcomplete_name())).strip()
                if len(name) == 0:
                    name = None
            
            if tags is None:
                tags = str(term.input("Enter tags(comma separated): ", self._tabcomplete_tag(name))).strip()
                tags = [tag.strip() for tag in tags.split(",") if len(tag.strip()) != 0]
            
            if attributes is None:
                attributes = []
                while True:
                    attribute = str(term.input("Enter attribute, leave blank if finished. format 'Name,value,[unit]'\nattribute: "))
                    attribute = [trait.strip() for trait in attribute.split(",") if len(trait.strip()) != 0]
    
                    if len(attribute) == 0:
                        break
                    elif len(attribute) == 2:
                        attributes.append((attribute[0], self._float_eval(attribute[1]), None))
                    elif len(attribute) == 3:
                        if len(attribute[2].strip()) == 0:
                            attribute[2] = None
                        attributes.append((attribute[0], self._float_eval(attribute[1]), attribute[2]))
                    else:
                        term.print("Malformed command 4")
                        return
        
        new_entry = groceryDatabase.entry(name, tags)
        for name, value, unit in attributes:
            new_attribute = groceryDatabase.attribute(name, value, unit)
            new_entry.add_attribute(new_attribute)
        
        self.database.add_entry(new_entry)
        self.database.update()
    
    @command
    def add_food(self, arg):
        """ 
        Add a food entry to database.
        
        Examples: 
            add name, tag,...,tag
            add name
            add
        """

        name = None
        tags = None
        attributes = []

        if len(arg.strip()) != 0:
            arg = arg.split(",", 1)
            if len(arg) == 1:
                name = arg[0]
                tags = None
            else:
                name = arg[0]
                tags = [tag.strip() for tag in arg[1].split(",") if len(tag.strip()) != 0]
                if len(tags) == 0:
                    tags = None
            
        with terminal.terminal() as term:
            while name is None:
                name = str(term.input("Enter entry name: ", self._tabcomplete_name())).strip()
                if len(name) == 0:
                    name = None
            
            if tags is None:
                tags = str(term.input("Enter tags(comma separated): ", self._tabcomplete_tag(name))).strip()
                tags = [tag.strip() for tag in tags.split(",") if len(tag.strip()) != 0]
            
            
            attributes.append(("price", self._float_eval(term.input("Enter price: ")), "dollars"))
            
            while True:
                reply = str(term.input("Did you buy more than one[y/n]: ")).lower()
                if reply.startswith("y"):
                    attributes.append(("quantity", self._float_eval(term.input("Enter quantity: ")), None))
                    break
                elif reply.startswith("n"):
                    break
    
            while True:
                reply = str(term.input("Mesure by mass or volume[m/v]: ")).lower()
                if reply.startswith("m"):
                    attributes.append(("mass", self._float_eval(term.input("Enter mass in grams: ")), "g"))
                    break
                elif reply.startswith("v"):
                    attributes.append(("volume", self._float_eval(term.input("Enter volume in milliliters: ")), "ml"))
                    break
            
            attributes.append(("calories", self._float_eval(term.input("Enter calories in calories per 100 grams: ")), "calories/100g"))
            attributes.append(("fat", self._float_eval(term.input("Enter fat in grams per 100 grams: ")), "g/100g"))
            attributes.append(("carbohydrates", self._float_eval(term.input("Enter carbohydrates in grams per 100 grams: ")), "g/100g"))
            attributes.append(("protein", self._float_eval(term.input("Enter protein in grams per 100 grams: ")), "g/100g"))
        
        new_entry = groceryDatabase.entry(name, tags)
        for name, value, unit in attributes:
            new_attribute = groceryDatabase.attribute(name, value, unit)
            new_entry.add_attribute(new_attribute)
        
        self.database.add_entry(new_entry)
        self.database.update()
    
    @command
    def help(self, arg):
        """ 
        Display helpfull information about the avaliable subcommands.
        """
        if arg.strip() == "":
            print("Help: all subcommands\n" + " ".join(list(_commands.keys())) + "\n\n'gdata help' lists available subcommands. See 'gdata help <command>' to get documentation for a specific subcommand.")
        else:
            if arg.strip() in _commands:
                if _commands[arg.strip()] is not None:
                    print(textwrap.dedent(_commands[arg.strip()]))
                else:
                    print("No documentation exists for the subcommand \"" + arg.strip() + "\".")
            else:
                print("\"" + arg.strip() + "\" is not a valid subcommand.")
    
    def _tabcomplete_name(self):
        """ 
        returns callback function for tab completion 
        """
        def tabcomplete(string):
            names = []
            for entry in self.database._database:
                if entry.name.startswith(string):
                    names.append(entry.name)
            names = list(set(names))
    
            prefix = os.path.commonprefix(names)
            
            text = ""
            if len(prefix) != 0:
                text = prefix[len(string):]
            
            tips = ""
            if len(names) > 1:
                for i, name in enumerate(names[:-1]):
                    tips = tips + name
                    if (i + 1)%3 == 0:
                        tips = tips + "\n"
                    else:
                        tips = tips + ", "
    
                tips = tips + names[-1]
            return text, tips
        return tabcomplete
    

    def _tabcomplete_tag(self, name):
        """ 
        returns callback function for tab completion 
        """
        def tabcomplete(string):
            if "," in string:
                string = string.split(",")[-1].strip()
            
            tags = []
            for entry in self.database._database:
                if entry.name == name:
                    for tag in entry.tags:
                        if tag.startswith(string):
                            tags.append(tag)            
            tags = list(set(tags))
    
            prefix = os.path.commonprefix(tags)
            
            text = ""
            if len(prefix) != 0:
                text = prefix[len(string):]
            
            tips = ""
            if len(tags) > 1:
                for i, tag in enumerate(tags[:-1]):
                    tips = tips + tag
                    if (i + 1)%3 == 0:
                        tips = tips + "\n"
                    else:
                        tips = tips + ", "
    
                tips = tips + tags[-1]
            return text, tips
        return tabcomplete
    
    def _float_eval(self, string):
        """ 
        evaluate a string as a float.
        
        Note this code uses eval
        """
        string = "".join([char for char in string if char in '0123456789.*/( )'])
        return float(eval(string, {"__builtins__": None}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process = gdatabaseUtility(sys.argv[1], " ".join(sys.argv[2:]))
    else:
        process = gdatabaseUtility("help")
