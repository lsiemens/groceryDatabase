#!/usr/bin/env python3

#
# comandline interface for groceryDatabase.py
#

import cmd
import sys
import groceryDatabase

class gdatabaseShell(cmd.Cmd):
    intro = "Welcome to the gdatabase shell"
    prompt = ">>> "

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self.database = groceryDatabase.groceryDatabase()
    
    def do_list(self, arg):
        """ 
        List contents of database.
        """
        print(self.database)
    
    def do_add(self, arg):
        """ 
        Add entry to database.
        
        Examples: 
            add name: tag,...,tag; trait,value,unit ...
    
            add name; trait,value trait,value,unit ...
        
            add name: tag,...,tag
        
            add name

            add
        """

        name = None
        tags = None
        attributes = None

        if len(arg.strip()) != 0:
            arg = arg.split(";")
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

            name_tags = name_tags.split(":")
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

    def do_EOF(self, arg):
        """ 
        Exit gdatabase comand line.
        """
        
        print("\n")
        return self._exit_cmd()
        
    def do_exit(self, arg):
        """ 
        Exit gdatabase comand line.
        """
        
        return self._exit_cmd()
        
    def emptyline(self):
        """ 
        This method is called if an empty line is given
        in responce to the command prompt.
        """
        
        return
    
    def default(self, line):
        print("*** ERROR: \"" + line + "\" command not found")
    
    def _exit_cmd(self):
        """ 
        cleanly close cmd.
        """
        
        self.database.update()
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        terminal = gdatabaseShell()
        terminal.onecmd(" ".join(sys.argv[1:]))
    else:
        terminal = gdatabaseShell()
        terminal.cmdloop()
