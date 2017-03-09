#
#groceryDatabase.py: Data base for purchased grocerys
#

import time
import datetime

class attribute:
    """ 
    An attribute
    
    Parameters
    ----------
    name : string
        Attribute name. The names of attributes must be unique.
    value : float
        Value of the attribute.
    unit : string
        The units of measurement.
    
    """

    def __init__(self, name, value, unit=None):
        self.name = name
        self.value = value
        self.unit = unit
    
    def __str__(self):
        text = self.name + ": " + str(self.value)
        if self.unit is not None:
            text = text + " " + str(self.unit)
        return text + "\n"

    def __repr__(self):
        text = self.name + " = " + str(self.value)
        if self.unit is not None:
            text = text + " {" + str(self.unit) + "}"
        return text + "\n"

    def _update_from_text(self, line):
        self.name, line = line.split(" = ")
        if "{" in line:
            value, unit = line.split(" {")
            self.value = float(value)
            self.unit = unit[:-1]
        else:
            self.value = float(line)
            self.unit = None

class entry:
    """ 
    An object containing a 
    
    required entrys
        Name: produce name
        id  : entry identifier
        Date: entry date
        Tags: tags

    Parameters
    ----------
    name : string
        Name of database entry
    tags : list
        List of tags, the name is add as a tag automaticaly
    
    """
    
    _counter = 1

    def __init__(self, name, tags=[]):
        self.name = name
        self.id = self.__class__._counter
        self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        self.tags = tags
        self.attributes = []
        
        self.__class__._counter += 1
        
    def __str__(self):
        text = "[" + self.name + "]\nid: " + str(self.id) + "\ntimestamp: " + self.timestamp + "\n"
        if len(self.tags[1:]) != 0:
            text = text + "tags: " + ",".join(self.tags[1:]) + "\n"
        for attribute in self.attributes:
            text = text + str(attribute)
        return text
    
    def __repr__(self):
        text = "[" + self.name + "]\nid = " + str(self.id) + "\ntimestamp = " + self.timestamp + "\n"
        text = text + ",".join(self.tags) + "\n"
        for attribute in self.attributes:
            text = text + repr(attribute)
        return text + "[/" + self.name + "]\n"
    
    def add_attribute(self, trait):
        """ 
        Add attribute to entry. If the attribute already exists
        replace the old attribute.
        
        Parameters
        ----------
        trait : attribute
            The attribute to add to the current entry.
            
        """

        for i, existing_trait in enumerate(self.attributes):
            if trait.name == existing_trait.name:
                self.attributes[i] = trait
                return

        self.attributes = self.attributes + [trait]
    
    def _update_from_text(self, lines):
        """ 
        Update entry from text
        
        Parameters
        ----------
        lines : list
            list of lines from database
        """
        
        self.name = lines[0][1:-1]
        self.id = int(lines[1][5:])
        if self.id >= self.__class__._counter:
            self.__class__._counter = self.id + 1
        self.timestamp = lines[2][12:]
        self.tags = lines[3].split(",")[1:]
        if self.name != lines[-1][2:-1]:
            raise IOError("Mismatching opening and closing tags.")

        for line in lines[4:-1]:
            new_attribute = attribute(None, None, None)
            new_attribute._update_from_text(line)
            self.add_attribute(new_attribute)
    
    @property
    def tags(self):
        return [self.name] + self._tags
    
    @tags.setter
    def tags(self, tags):
        self._tags = tags

class groceryDatabase:
    """ 
    Object maintaining a list of entry instances.
    """

    def __init__(self, path, load=False):
        self.path = path
        self.database = []
        if load:
            self.load()
        
    def __str__(self):
        return "\n".join([str(entry) for entry in self.database])

    def __repr__(self):
        return "\n".join([repr(entry) for entry in self.database])
        
    def update(self):
        """ 
        Save database to file
        """
    
        with open(self.path, "w") as fout:
            fout.write(repr(self))
    
    def load(self):
        """ 
        Load database from file
        """
        
        self.database = []
        
        text = ""
        with open(self.path, "r") as fin:
            text = fin.read()
        
        lines = text.split("\n")
        start = 0
        end = 0
        while True:
            try:
                start, end = self._find_block(lines, end)
                new_entry = entry(name=None)
                new_entry._update_from_text(lines[start:end])
                self.add_entry(new_entry)
            except EOFError:
                break
    
    def add_entry(self, entry):
        """ 
        Add entry to database
        
        Parameters
        ----------
        entry : entry
            Add entry to data base
        """
        
        self.database = self.database + [entry]

    def _find_block(self, lines, offset=0):
        """ 
        Parameters
        ----------
        lines : list
            A list of the lines of text contained in the database.
        offset : integer
            Start from this line
        
        Returns
        -------
        start : integer
            Idex of block start.
        stop : integer
            Index of block end.
        
        Raises
        ------
        IOError :
            An exception is raised if no closing tag is found or if no block is found
        """

        start = None
        stop = None
        isblock = False
        for i, line in enumerate(lines[offset:]):
            if isblock:
                if line.startswith("[/"):
                    stop = i + 1 + offset
                    return start, stop
            else:
                if line.startswith("[") and (not line.startswith("[/")):
                    start = i + offset
                    isblock = True
        
        if isblock:
            raise IOError("No closing tag found for database entry.")
        else:
            raise EOFError("No database entry found.")
