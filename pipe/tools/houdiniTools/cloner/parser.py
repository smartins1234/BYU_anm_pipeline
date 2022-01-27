'''
This was my attempt at creating a usda file parser.
I ended up not using it.
:')
'''

#from pxr import Usd
import os

class Parser:
    def __init__(self):
        #print("starting parser...")
        pass
    
    def parse(self, path=None):
        stage = Stage()

        file = open(path, "r")
        for line in file:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "def":
                    
                    type = next(wordIter)

                    if type in PrimTypes.ALL:
                        prim = PrimTypes.PRIM[type]()
                        prim.parse(file, wordIter, line.strip())
                        stage.addPrim(prim)

                    else:
                        prim = Def()
                        prim.parse(file, type, line)
                        stage.addPrim(prim)
                    
                #current = next(myiter)

        #now we have to select the one variant that's actually supposed to be loaded into the scene

        for p in stage.prims:
            if p.varDict is not {}:
                #get attribute that is variantset
                for att in p.attributes:
                    if isinstance(att, VariantSet):
                        setName = att.getName()
                        varName = p.varDict[setName]
                        if varName:
                            var = att.dict[varName]
                            var.isLoaded = True

        #stage.printAll()
        #print("finished")
        return stage

class Stage:
    def __init__(self):
        self.prims = []

    def addPrim(self, prim):
        self.prims.append(prim)

    def printAll(self):
        tabs = ""
        for prim in self.prims:
            if prim.isLoaded:
                self.printPrim(prim, tabs)

    def printPrim(self, prim, tabs):
        if not prim.isLoaded:
            return
        print(tabs + prim.getName() + " " + prim.getPrimPath() + " " + prim.getTypeName())
        for prop in prim.properties:
            print(tabs + "\t" + prop.getName() + " = " + prop.getValue())
        for att in prim.attributes:
            if isinstance(att, VariantSet):
                tabs += "\t"
                for v in att.value:
                    self.printPrim(v, tabs)
                tabs = tabs[:-1]
            else:
                print(tabs + "\t" + att.getName() + " = " + str(att.getValue()))

        tabs += "\t"
        for p in prim.prims:
            self.printPrim(p, tabs)

    def printStructure(self):
        tabs = ""
        for prim in self.prims:
            if prim.isLoaded:
                self.printPrimShort(prim, tabs)

    def printPrimShort(self, prim, tabs):
        if not prim.isLoaded:
            return
        print(tabs + prim.getName() + " " + prim.getPrimPath() + " " + prim.getTypeName())
        for att in prim.attributes:
            if isinstance(att, VariantSet):
                tabs += "\t"
                for v in att.value:
                    self.printPrimShort(v, tabs)
                tabs = tabs[:-1]
        tabs += "\t"
        for p in prim.prims:
            self.printPrimShort(p, tabs)


class Prim(object):
    def __init__(self, parent=None):
        self.typeName = ""
        self.name = ""
        self.attributes = []
        self.prims = []
        self.primPath = ""
        self.parent = parent
        self.properties = []
        self.varDict = {}
        self.isLoaded = True

        if parent:
            self.primPath += parent.getPrimPath()

    def getName(self):
        return self.name

    def getTypeName(self):
        return self.typeName

    def hasParent(self):
        if self.parent is not None:
            return True
        else:
             return False

    def getParent(self):
        return self.parent

    def getPrimPath(self):
        return self.primPath

    def parse(self, lineIter, wordIter, line):
        self.name = next(wordIter)[1:-1]
        self.primPath = self.primPath + "/" + self.name
        #print(self.typeName)
        #print(self.primPath)
        if line[-1] == "(":
            self.getMetadata(lineIter)
        count = 0
        for line in lineIter:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "{":
                    count += 1
                elif word == "}":
                    count -=1
                    if count == 0:
                        return
                    elif count < 0:
                        print("BIG WHOOPSIE TIME, GO FIX")
                        quit()
                elif word == "def":
                    type = next(wordIter).strip()
                    #name = next(wordIter)[1:-1]
                    #print(type)
                    if type in PrimTypes.ALL:
                        prim = PrimTypes.PRIM[type](parent=self)
                        prim.parse(lineIter, wordIter, line)
                        self.prims.append(prim)
                    else:
                        prim = Def(self)
                        prim.parse(lineIter, type, line)
                        self.prims.append(prim)
                    
                elif word != "def" and not word in Symbols.ALL:
                    type = word.strip()
                    if type in AttributeTypes.ALL:
                        #print("attr of type ", type)
                        att = AttributeTypes.ATTRIBUTE[type]()
                        if isinstance(att, VariantSet):
                            att.setParent(self)
                        att.loadValue(lineIter, wordIter)
                        self.attributes.append(att)
                    else:
                        for word in wordIter:
                            pass

        print("\n")

    def getMetadata(self, lineIter):
        count = 1
        for line in lineIter:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "(":
                    count += 1
                elif word == ")":
                    count -= 1
                    if count == 0:
                        return
                    elif count < 0:
                        print("This is so sad, Alexa play despacito")
                        quit()
                elif word == "prepend":
                    word = next(wordIter)
                    if word == "references":
                        name = "reference"
                        next(wordIter) #skipping equals
                        value = next(wordIter)
                        atCount = 0
                        finalVal = ""
                        for char in value:
                            if char == "@":
                                atCount += 1
                                if atCount == 2:
                                    break
                            else:
                                finalVal += char

                        self.properties.append(Property(name, finalVal))
                        layer = Parser().parse(finalVal)
                        
                        for prim in layer.prims:
                            #print("from ref: "+prim.getName())
                            prim.parent = self
                            if prim.getName != self.name:
                                self.prims.append(prim)
                            '''for subPrim in prim.prims:
                                print(subPrim.getName())
                                self.prims.append(subPrim)'''
                elif word == "variants":
                    line = next(lineIter).split()
                    setName = line[1]
                    varName = line[3][1:-1]
                    self.varDict[setName] = varName
                else:
                    pass
                    



class Xform(Prim):
    def __init__(self, parent=None):
        super(Xform, self).__init__(parent)
        self.typeName = "Xform"

class Scope(Prim):
    def __init__(self, parent=None):
        super(Scope, self).__init__(parent)
        self.typeName = "Scope"

class Material(Prim):
    def __init__(self, parent=None):
        super(Material, self).__init__(parent)
        self.typeName = "Material"

class Shader(Prim):
    def __init__(self, parent=None):
        super(Shader, self).__init__(parent)
        self.typeName = "Shader"

class Mesh(Prim):
    def __init__(self, parent=None):
        super(Mesh, self).__init__(parent)
        self.typeName = "Mesh"

    def parse(self, lineIter, word, line):
        pass


class Def(Prim):
    def __init__(self, parent=None):
        super(Def, self).__init__(parent)
        self.typeName = "def"

    def parse(self, lineIter, word, line):
        self.name = word[1:-1]
        self.primPath = self.primPath + "/" + self.name
        #print(self.typeName)
        #print(self.primPath)
        if line.strip()[-1] == "(":
            self.getMetadata(lineIter)
        count = 0
        for line in lineIter:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "{":
                    count += 1
                elif word == "}":
                    count -= 1
                    if count == 0:
                        return
                    elif count < 0:
                        print("UH OH STINKY, MUST FIX")
                        quit()
                elif word not in Symbols.ALL:
                    type = word.strip()
                    #print("attr of type ", type)
                    if type in AttributeTypes.ALL:
                        att = AttributeTypes.ATTRIBUTE[type]()
                        if isinstance(att, VariantSet):
                            att.setParent(self)
                        att.loadValue(lineIter, wordIter)
                        self.attributes.append(att)
                    else:
                        for word in wordIter:
                            pass

        
class Attribute(object):
    def __init__(self):
        self.type = None
        self.name = None
        self.value = None

    @staticmethod
    def printHi():
        print("hi")

    def getType(self):
        return self.type

    def getName(self):
        return self.name

    def getValue(self):
        return self.value
    
    def loadValue(self, lineIter, wordIter):
        return self

class Matrix4d(Attribute):
    def __init__(self):
        super(Matrix4d, self).__init__()
        self.type = "matrix4d"
        self.value = []

    def loadValue(self, lineIter, wordIter):
        self.name = next(wordIter)
        next(wordIter) #skipping the equals sign
        #add the rest of the line into a string
        valString = ""
        for word in wordIter:
            valString += word
        self.parseValue(valString)
        #print(self.value)
        return self

    def parseValue(self, valString):
        temp = []
        num = ""
        for char in valString:
            if char == ")":
                if num != "":
                    temp.append(float(num))
                    self.value.append(temp)
                    num = ""
                    temp = []
            elif char != "(":
                if char == ",":
                    if num != "":
                        temp.append(float(num))
                        num = ""
                else:
                    num += char

class Relationship(Attribute):
    def __init__(self):
        super(Relationship, self).__init__()
        self.type = "rel"
        self.value = ""

    def loadValue(self, lineIter, wordIter):
        self.name = next(wordIter)
        next(wordIter) #skipping the equals sign
        self.value = next(wordIter)[1:-1]

class Custom(Attribute):
    def __init__(self):
        super(Custom, self).__init__()
        self.type = "custom"
        
    def loadValue(self, lineIter, wordIter):
        valType = next(wordIter)
        if valType == "string":
            self.name = next(wordIter)
            next(wordIter) #skipping equals sign
            self.value = next(wordIter)[1:-1]
        else:
            for word in wordIter:
                pass

class VariantSet(Attribute):
    def __init__(self):
        super(VariantSet, self).__init__()
        self.type = "variantset"
        self.value = []
        self.parent = None
        self.dict = {}

    def setParent(self, parent):
        self.parent = parent

    def loadValue(self, lineIter, wordIter):
        self.name = next(wordIter)[1:-1]
        count = 1
        for line in lineIter:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "{":
                    count += 1
                elif word == "}":
                    count -= 1
                    if count == 0:
                        for var in self.value:
                            self.dict[var.name] = var
                        return
                    elif count < 0:
                        print("My dissapointment is immessurable and my day is ruined")
                        quit()
                elif word not in Symbols.ALL:
                    #print(word)
                    var = Variant(self.parent)
                    var.parse(lineIter, word, line)
                    self.value.append(var)
        



class Variant(Prim):
    def __init__(self, parent=None):
        super(Variant, self).__init__(parent)
        self.typeName = "Variant"
        self.isLoaded = False

    def parse(self, lineIter, word, line):
        self.name = word[1:-1]
        self.primPath = self.primPath + "/" + self.name
        #print(self.typeName)
        #print(self.primPath)
        if line.strip()[-1] == "(":
            self.getMetadata(lineIter)
        count = 1
        for line in lineIter:
            wordIter = iter(line.split())
            for word in wordIter:
                if word == "{":
                    count += 1
                elif word == "}":
                    count -= 1
                    if count == 0:
                        return
                    elif count < 0:
                        print("UH OH STINKY, MUST FIX")
                        quit()
                elif word == "def":
                    type = next(wordIter).strip()
                    #name = next(wordIter)[1:-1]
                    #print(type)
                    if type in PrimTypes.ALL:
                        prim = PrimTypes.PRIM[type](parent=self)
                        prim.parse(lineIter, wordIter, line)
                        self.prims.append(prim)
                    else:
                        prim = Def(self)
                        prim.parse(lineIter, type, line)
                        self.prims.append(prim)
                    
                elif word != "def" and not word in Symbols.ALL:
                    type = word.strip()
                    if type in AttributeTypes.ALL:
                        #print("attr of type ", type)
                        att = AttributeTypes.ATTRIBUTE[type]()
                        if isinstance(att, VariantSet):
                            att.setParent(self)
                        att.loadValue(lineIter, wordIter)
                        self.attributes.append(att)
                    else:
                        for word in wordIter:
                            pass

        print("\n")





class Symbols:
    OPEN = "("
    CLOSE = ")"
    OPEN_CURL = "{"
    CLOSE_CURL = "}"
    OPEN_SQUARE = "["
    CLOSE_SQUARE = "]"
    ALL = [OPEN, CLOSE, OPEN_CURL, CLOSE_CURL, OPEN_SQUARE, CLOSE_SQUARE]

class PrimTypes:
    XFORM = "Xform"
    SCOPE = "Scope"
    MATERIAL = "Material"
    SHADER = "Shader"
    MESH = "Mesh"
    ALL = [XFORM, SCOPE, MATERIAL, SHADER, MESH]
    PRIM = {
        XFORM: Xform,
        SCOPE: Scope,
        MATERIAL: Material,
        SHADER: Shader,
        MESH: Mesh
    }

class AttributeTypes:
    MATRIX4D = "matrix4d"
    RELATIONSHIP = "rel"
    CUSTOM = "custom"
    VARIANTSET = "variantSet"
    ALL = [MATRIX4D, RELATIONSHIP, CUSTOM, VARIANTSET]
    ATTRIBUTE = {
        MATRIX4D: Matrix4d,
        RELATIONSHIP: Relationship,
        CUSTOM: Custom,
        VARIANTSET: VariantSet
    }

class Property:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def getName(self):
        return self.name
    def getValue(self):
        return self.value
    
'''    
myParser = Parser()
myStage = myParser.parse("/groups/cenote/BYU_anm_pipeline/production/layouts/xochimilco/layout/xochimilco_ref.usda")
myStage.printAll()
print("finished")'''