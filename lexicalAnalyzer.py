import re 
from enum import Enum


class type(Enum):
    alpha = 0
    numeric = 1
    special = 2
    # Still not a robust way to check for strings, but it works for now
    string_ap = 3
    string_qt = 4
    del_left = 5
    del_right = 6
    space = 7
    end = 8

class LexicalAnalyzer:
    def __init__(self, fileToTokenize) -> None:
        with open(fileToTokenize, "r") as file:
            self.file = file.read()

        self.tokens = [] # A nested list containing the tokens of each line.
        self.symbol_table = {} # Considered as environment

        self.streamLine()

    def checkType(self, char) -> type:
        # Rudimentary approach for type checking. Separate from the token type indentifier.
        if char == "'":
            return type.string_ap
        elif char == '"':
            return type.string_qt
        elif char.isalpha() or char == "_":
            return type.alpha
        elif char.isdigit() or char == ".":
            return type.numeric
        elif char == ";":
            return type.end
        elif char == "(":
            return type.del_left
        elif char == ")":
            return type.del_right
        elif char.isspace():
            return type.space
        else:
            return type.special

    def streamLine(self):
        first = True # Indicates if it is the first character of the line, useful for indentation.
        previousType = None # Indicates the previous type of character, for combining or separating tokens.
        isString = False # Indicates if the current character is a start of a string.
        isFirstString = True # Indicates if the current character is the first character of the string.
        stringType = None # Indicates the type of string, either single or double quotation mark.


        # Algorithm:
        # 1. Iterate through each line of the file.
        # 2. Iterate through each character of the line.
        # 3. Check the type of the character.
        # 4. If the character is a string, then combine the characters until it finds the same quotation mark.
        # 5. If the character is not a string, then combine the characters until it finds a different type of character.
        # 6. If the character is a space, then ignore it.
        # 7. Add to symbol table information about the token, such as the line number, column number, and type. We'll add the type on a different function.
        # 8. At the end of the line, append the list of tokens to the tokens list.

        for line in self.file.split("\n"):
            tempList = [] # Create a sub list for each line.
            for char in line:
                if first:
                    first = False
                    previousType = self.checkType(char)
                    if (previousType == type.string_ap or previousType == type.string_qt) and not isString:
                        isString = True
                    # on the case of string, it only stops when it finds the same quotation mark. 
                    tempList.append(char) # if previousType != type.space else None
                else:   
                    currentType = self.checkType(char)

                    if (currentType == type.string_ap or currentType == type.string_qt) and not isString:
                        isString = True
                        stringType = currentType

                    if isString:
                        combineString = tempList.pop() if not isFirstString else ""
                        tempList.append(combineString + char)
                        if currentType == stringType and isFirstString == False:
                            isString = False
                        isFirstString = False
                    else:
                        if currentType == previousType:
                            combineWith = tempList.pop()
                            tempList.append(combineWith + char) 
                        else:
                            tempList.append(char) if currentType != type.space else None
                            previousType = currentType

            first = True
            isFirstString = True

            # Ignore's all temp lists that are empty
            self.tokens.append(tempList) if tempList != [] else None

        print(f"Tokens:\n{self.tokens}")

    def tokenize(self):
        pass
    # Once the entire file has been tokenized, then we analyze and report errors. 
    