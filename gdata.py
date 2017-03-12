#!/usr/bin/env python3

#
# comandline interface for groceryDatabase.py
#

import sys
import textwrap
import groceryDatabase

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
        
        try:
            if command not in _commands:
                raise AttributeError
            
            function = getattr(self, command)
            function(arg)
        except AttributeError:
            print("ERROR: \"" + command + "\" is not a valid subcommand. See 'gdata help'")
            
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
                        attributes[i] = (attribute[0], float(attribute[1]), None)
                    elif len(attribute) == 3:
                        if len(attribute[2].strip()) == 0:
                            attribute[2] = None
                        attributes[i] = (attribute[0], float(attribute[1]), attribute[2])
                    else:
                        print("Malformed command 3")
                        return
        
        while name is None:
            name = str(input("Enter entry name: ")).strip()
            if len(name) == 0:
                name = None
        
        if tags is None:
            tags = str(input("Enter tags(comma separated): ")).strip()
            tags = [tag.strip() for tag in tags.split(",") if len(tag.strip()) != 0]
        
        if attributes is None:
            attributes = []
            while True:
                attribute = str(input("Enter attribute, leave blank if finished. format 'Name,value,[unit]'\nattribute: "))
                attribute = [trait.strip() for trait in attribute.split(",") if len(trait.strip()) != 0]

                if len(attribute) == 0:
                    break
                elif len(attribute) == 2:
                    attributes.append((attribute[0], float(attribute[1]), None))
                elif len(attribute) == 3:
                    if len(attribute[2].strip()) == 0:
                        attribute[2] = None
                    attributes.append((attribute[0], float(attribute[1]), attribute[2]))
                else:
                    print("Malformed command 4")
                    return
        
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process = gdatabaseUtility(sys.argv[1], " ".join(sys.argv[2:]))
    else:
        process = gdatabaseUtility("help")