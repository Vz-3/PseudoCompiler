import re # For regex in token type. 
import os # For creating directory for logs.
from enum import Enum

# Line and Column count should always start at 0. But displayed as 1.

default_directory = "logs"
class atomType(Enum):
    alpha = 0
    numeric = 1
    special = 2
    # Still not a robust way to check for strings, but it works for now
    string_ap = 3
    string_qt = 4
    del_left = 5
    del_right = 6
    space = 7
    arithemetic = 8
    end = 9


# Basically these enums are like CFG rules.
# Base if doesn't contain enums.
# Extended if part of general.
# General if part of umbrella and contains other enums.
# Need the enum names to match the token type names in higher levels otherwise it wont work.

# BASE
class DELIMETER(Enum):
    DELIMITER_LEFT_P = r"\("
    DELIMITER_RIGHT_P = r"\)"

# EXTENDED
class RELATIONAL(Enum):
    OP_RELATIONAL_ISEQUAL = r"=="
    OP_RELATIONAL_NOTEQUAL = r"!="
    OP_RELATIONAL_LESSTHAN = r"<"
    OP_RELATIONAL_LESSTHANOREQUAL = r"<="
    OP_RELATIONAL_GREATERTHAN = r">"
    OP_RELATIONAL_GREATERTHANOREQUAL = r">="

# EXTENDED 
class ARITHMETIC(Enum):
    OP_ARITHMETIC_PLUS = r"\+"
    OP_ARITHMETIC_MINUS = r"-"
    OP_ARITHMETIC_MULTIPLY = r"\*"
    OP_ARITHMETIC_DIVIDE = r"/"

# GENERAL
class OPERATOR(Enum):
    OP_ASSIGNMENT = r":="
    OP_COLON = r":" # For the type declaration
    OP_EQUAL = r"=" # For the start of an operation.
    OP_LEFTSHIFT = r"<<" 
    ARITHMETIC = '|'.join([arithmeticOperator.value for arithmeticOperator in ARITHMETIC])
    RELATIONAL = '|'.join([relationalOperator.value for relationalOperator in RELATIONAL])

# BASE
class LITERAL(Enum):
    LITERAL_DOUBLE = r"-?[0-9]+\.[0-9]*" # Literals are same as constants.
    LITERAL_INTEGER = r"-?[0-9]+"
    LITERAL_STRING = r'''(['"])(.*?)\1''' # This could also be the alternative source of the error. 

# EXTENDED 
class DATA_TYPE(Enum):
    KEYWORD_INT = r"integer"
    KEYWORD_DOUBLE = r"double"

# GENERAL
class KEYWORD(Enum):
    DATA_TYPE = '|'.join([dt.value for dt in DATA_TYPE])
    KEYWORD_IF = r"if"
    KEYWORD_OUTPUT = r"output"

# UMBRELLA
class tokenType(Enum):
    # Order Matters. Case sensitive for keywords. Arranged in likelihood.
    KEYWORD = '|'.join([keyword.value for keyword in KEYWORD])

    IDENTIFIER = r"[a-zA-Z_][a-zA-Z_]*"

    LITERAL = '|'.join([literal.value for literal in LITERAL])

    ENDLINE = r";"

    OPERATOR = '|'.join([operator.value for operator in OPERATOR])

    DELIMITER = '|'.join([delimiter.value for delimiter in DELIMETER])

# Storing all higher levels. 
enumDictionary = {
    "KEYWORD": KEYWORD,
    "OPERATOR": OPERATOR,
    "DELIMITER": DELIMETER,
    "LITERAL": LITERAL,
    "DATA_TYPE": DATA_TYPE,
    "RELATIONAL": RELATIONAL,
    "ARITHMETIC": ARITHMETIC
}

class LexicalAnalyzer:
    def __init__(self, fileToTokenize) -> None:
        self.fileName = fileToTokenize

        with open(fileToTokenize, "r") as file:
            self.file = file.read()

        self.atoms = [] # A nested list containing the atoms of each line. Should not be modified after atomizer() (R)
        self.tokens = [] # A list containing the tokens of the file in the form of a tuple (token, type). Can only be changed after parsing, to sort out negative values. (R)
        self.symbol_table = {} # Considered as environment (RW)
        self.isFirstError = True # Indicates if it is the first error, useful for the error log.

        self.tokensCopy = [] # used for symbol table initialization and perhaps other uses. (RW)
        # The following functions will be called in the constructor.
        self.initDir()
        self.atomizer()
        self.tokenizer()
        self.analyzeTokens()
        self.cleanTable() # At this point, all the variables should have a data type and value. Otherwise, they are not an indentifier, or declared/assigned properly.

    def getEnumValue(self, enumScope:Enum, target:str, isName:bool = False) -> str:
        """ This function will return the value of the enum."""
        for scope in enumScope:
            # print("Scope: ", scope.value, "Target: ", target)
            if re.fullmatch(scope.value, target):
                return scope.value if not isName else scope.name
        return None

    def updateTokenCopy(self) -> None:
        """ This function will update the token copy. Useful for symbol table initialization and perhaps other uses."""
        self.tokensCopy = self.tokens.copy()

    def initDir(self) -> None:
        """ This function will create a directory for the logs."""
        if not os.path.exists(default_directory):
            os.makedirs(default_directory)

    def checkAtomType(self, char) -> atomType:
        """"""
        # Rudimentary approach for type checking. Separate from the token type indentifier.
        # Produces niche error for string literals. 
        if char == "\'": # Removing the \ doesn't produce a different effect. 
            return atomType.string_ap
        elif char == '"':
            return atomType.string_qt
        elif char.isalpha() or char == "_":
            return atomType.alpha
        elif char.isdigit() or char == ".":
            return atomType.numeric
        elif char == ";":
            return atomType.end
        elif char == "(":
            return atomType.del_left
        elif char == ")":
            return atomType.del_right
        elif char.isspace():
            return atomType.space
        elif char == "+" or char == "-" or char == "*" or char == "/":
            return atomType.arithemetic
        else:
            return atomType.special

    def atomizer(self) -> None:
        """ As the name implies, this function will break down the file into tokens, words or the atoms of the language."""

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
        # 7. At the end of the line, append the list of tokens to the tokens list.
        # 8. Write into NOSPACES.txt

        lineCount = 0
        for line in self.file.split("\n"):
            tempList = [] # Create a sub list for each line.
            for char in line:
                if first:
                    first = False
                    previousType = self.checkAtomType(char)
                    if (previousType == atomType.string_ap or previousType == atomType.string_qt) and not isString:
                        isString = True
                        stringType = previousType
                        isFirstString = False # This for the next iterations, to accept any character instead of separating it.
                    # on the case of string, it only stops when it finds the same quotation mark. 
                    tempList.append(char) if previousType != atomType.space else None
                else:   
                    currentType = self.checkAtomType(char)

                    if (currentType == atomType.string_ap or currentType == atomType.string_qt) and not isString:
                        isString = True
                        stringType = currentType

                    if isString:
                        combineString = tempList.pop() if not isFirstString else ""
                        tempList.append(combineString + char)
                        if currentType == stringType and isFirstString == False:
                            isString = False
                        isFirstString = False
                    else:
                        if currentType == previousType and currentType != atomType.space:
                            combineWith = tempList.pop()
                            tempList.append(combineWith + char) 
                        else:
                            tempList.append(char) if currentType != atomType.space else None
                            previousType = currentType

            first = True
            isFirstString = True
            stringType = None
            self.atoms.append(tempList) #if tempList != [] else None # Ignoring the list would result in line inconsistency.
            lineCount += 1

        # Debugging
        # print("\nAtoms:")
        # for line in self.atoms:
        #     print(line)

        self.writeAtoms()

    def writeAtoms(self, mode = "w") -> None:
        """ This function will write the atoms into a file."""
        with open(f'{default_directory}/NOSPACES.txt', mode) as file:
            for line in self.atoms:
                for atom in line:
                    file.write(atom)
        
        with open(f'{default_directory}/NOSPACES_LINE.txt', mode) as file:
            for line in self.atoms:
                if line != []:
                    for atom in line:
                        file.write(atom)
                    file.write("\n")
    
    # Must pass only a base or extended enum, otherwise it will not work as there's no recursion for general enums.
    def tokenize(self, typeScope: Enum, token: str, lineCount: int) -> str:
        """ Smaller version of tokenizer, used for individual token matching!"""
        result = self.getEnumValue(typeScope, token)
        if result != None: # Guard is better than if else.
            return result
        # self.reportError(token, lineCount, f"Invalid Token Type of type {typeScope.__name__}.", "Lexical Error")
        return False

    # For tokenizer only. 
    def checkTokenType(self, token, typeScope: Enum) -> (bool, str): 
        """ This function will check the type of the token, returns the specified type if it matches, else returns typeScope"""
        isToken = False
        #print("Typescope:", typeScope, "Token:", token, end = "\t\t")
        
        nextScope = None

        for ttype in typeScope:
            if re.fullmatch(ttype.value, token):
                isToken = True
                nextScope = ttype.name
                break
        if not isToken:
            # If it reaches this point, this means that there's a regex in the higher scope that matches the token but not the lower scope.
            # Managed to reach this with 'errors" or "below'
            return (False, 'err')
        # print("Found match:", nextScope, "with type ", type(nextScope), end = "\t\t")
        
        # Recurse if next scope is in the enum dictionary.
        for name, enum in enumDictionary.items():
            # If the next scope: e.g. OPERATOR matches the name of the enum, then we recurse.
            if nextScope == name:
                nextScope = enum
                # the nextScope would properly point to an enum now. 
                result = self.checkTokenType(token, nextScope)
                return result

        # Should always be a str data type at this point.
        # print("Returns with type:", nextScope, " of type ", type(nextScope), end="\n\n")
        return (True, nextScope)

    def tokenizer(self) -> None:
        """ This function will analyze the tokens and determine the type of each token."""
            
        # Algorithm:
        # 1. Iterate through each line of the file.
        # 2. Iterate through each token of the line.
        # 3. Check the type of the token.
        # 4. If error, print and write the error. Set the token type to 'err'.
        # 5. At the end of the line, append the list of tokens to the tokens list.
        # 6. Write into RES_SYM.txt

        lineCount = 0
        for line in self.atoms:
            for token in line:
                isToken, typeToken = self.checkTokenType(token, tokenType)
                if not isToken:
                    self.reportError(token, lineCount, "Invalid Token Type.", "Lexical Error")
                self.tokens.append((token, typeToken))
            lineCount += 1
        
        # Debugging
        # print("\nTokenize:")
        # for tup in self.tokens:
        #     print(f"Type: {tup[1]:<32} | Token: {tup[0]}") # 32 is the longest name length of token type. Could've used a more dynamic way to get the length. QOL

        self.writeTokens()

    def writeTokens(self, mode = 'w') -> None:
        """ This function will write the tokens into a file."""
        with open(f'{default_directory}/RES_SYM.txt', mode) as file:
            for tup in self.tokens:
                file.write(f"{tup[1]:<32} token: {tup[0]} \n")

    def analyzeTokens(self) -> None:
        """ This function initializes the symbol table and analyzes the tokens."""
        # Base from my light understanding, symbol table is a dictionary that contains the variables and their values.
        # Despite the fact that output is technically a function, it will not be included in the symbol table for the time being.
        # Identifier - Data Type - Value - First Line - Last Line
        
        # Implementation (In a way, we're rebuilding the self.atoms list.)
        # Initialize the symbol table with the identifiers and their default values.
        # Heuristic approach, select only the lines containing the identifiers in a list.
        # Recursively check the list for the data type and value, update accordingly.

        # Initialization
        for token in self.tokens:
            if token[1] == tokenType.IDENTIFIER.name:
                if token[0] not in self.symbol_table:
                    self.symbol_table[token[0]] = {'data_type': None, 'value': 'null', 'first_line': None, 'last_line': None}

        # print("\nSymbol Table:")
        # print(self.symbol_table, end="\n\n")
        # Then we proceed by looking up all the combined atoms and check if they have an identifier or not. 
        
        # Heuristic
        self.updateTokenCopy()
        analyzeList = []
        for lineCount, atom in enumerate(self.atoms):
            for key in self.symbol_table:
                # Limited to only assignment and declaration. Rest is up to syntax and evaluation. 
                if key in atom and (OPERATOR.OP_ASSIGNMENT.value in atom or OPERATOR.OP_COLON.value in atom):
                    parsedAtom = ''.join(atom)
                    isAssign = OPERATOR.OP_ASSIGNMENT.value in atom  # Cause it's guaranteeed that its a colon.
                    #print("Key:", key, "Parsed Atom:", parsedAtom, "Line:", lineCount, isAssign) 
                    # Remove what we know, ergo the identifier, assignment/colon, and the endline tokens, leaving only the likehood of data type or literal.
                    cleanedAtom = parsedAtom.replace(key, "").replace(OPERATOR.OP_ASSIGNMENT.value, "").replace(OPERATOR.OP_COLON.value, "").replace(tokenType.ENDLINE.value, "")
                    # That's why if the declaration or assignment is wrong syntactically, it will not be added to the symbol table and flag the error.
                    analyzeList.append((key, cleanedAtom, lineCount, isAssign)) # key, line, lineCount, mode tuple. lineCount still starts at 0 to confer to error reporting.
    
        # print("Analyze List:", analyzeList)
        # Recursion
        self.assignOrDeclare(analyzeList)

    def fixTokens(self, targetToken: any, targetLine: int) -> None:
        """ This function will fix the tokens by removing the target token and the token before it."""
        # print("Target Token:", targetToken, "Target Line:", targetLine)
        for ctr, val in enumerate(self.tokensCopy):
            if val[0] == targetToken and val[1] == tokenType.IDENTIFIER.name:
                # print("Replacing :", self.tokens[ctr], "AT LINE:", targetLine, "VAL:", val)
                self.tokens[ctr] = (self.tokens[ctr][0], 'err')

    def cleanTable(self) -> None:
        rejects = {k: v for k, v in self.symbol_table.items() if v['data_type'] is None}
        for key in rejects: 
            self.fixTokens(key, rejects[key]['first_line'])
            # self.reportError(key, rejects[key]['first_line']-1, f"Incorrect token: {key}.", "Lexical Error")
        self.symbol_table = {k: v for k, v in self.symbol_table.items() if v['data_type'] is not None}
        # print("\nNew Symbol Table:")
        # print(self.symbol_table, end="\n\n")
        print()

    def assignOrDeclare(self, l) -> None:
        token, tag, lineCount, mode = l.pop(0)

        val = self.symbol_table[token]['value']
        dt = self.symbol_table[token]['data_type']       
        if mode == False: # Declaration
            if dt == None:
                self.symbol_table[token]['data_type'] = self.tokenize(DATA_TYPE, tag, lineCount)
                self.symbol_table[token]['first_line'] = lineCount+1
                self.symbol_table[token]['last_line'] = lineCount+1 # +1 since we're displaying this in symbol table.
            else:
                self.reportError(token, lineCount, f"Redeclaration Error of {token} previously in line: {self.symbol_table[token]['first_line']}", "Lexical Error")
        else: # Assignment
            if dt == None:
                self.reportError(tag, lineCount, f"Undeclared Variable {token}.", "Lexical Error")
            
            if val == 'null':
                result = self.tokenize(LITERAL, tag, lineCount)
                if result != False:
                    self.symbol_table[token]['value'] = tag if dt == DATA_TYPE.KEYWORD_DOUBLE.value else re.sub(r'\..+', '',tag)
                    self.symbol_table[token]['first_line'] = lineCount+1 if self.symbol_table[token]['first_line'] == None else self.symbol_table[token]['first_line'] # Dont change if it exists.
                    self.symbol_table[token]['last_line'] = lineCount+1
            else:
                result = self.tokenize(LITERAL, tag, lineCount)
                if result != False:
                    self.symbol_table[token]['value'] = tag if dt == DATA_TYPE.KEYWORD_DOUBLE.value else re.sub(r'\..+', '',tag)
                    self.symbol_table[token]['last_line'] = lineCount+1

        self.assignOrDeclare(l) if l != [] else None   

    def reportError(self, targetToken: any, targetLine: int,  errorMessage = None, errorType = None, mode = 'a') -> None:
        """ This function will report the error of the token with its location."""
        mode = 'w' if self.isFirstError else 'a'
        self.isFirstError = False
        with open(f'{default_directory}/error.txt', mode) as log:
            for count, line in enumerate(self.file.split("\n")):
                if targetLine == count:
                    targetColumn = line.find(targetToken) + 1  # Adding 1 to make it 1-indexed
                    # Has issue since it continues to append instead of overwriting 
                    log.write(f"\nIn {self.fileName}, line {targetLine+1}: {line}, column {targetColumn}.\n|\t{targetToken} :: {errorType} :: {errorMessage}")
                    print(f"\nIn {self.fileName}, line {targetLine+1}: {line}, column {targetColumn}.\n|\t{targetToken} :: {errorType} :: {errorMessage}")
                    break
    # Once the entire file has been tokenized, then we analyze and report errors. 
    

    def getTokens(self) -> list:
        return self.tokens