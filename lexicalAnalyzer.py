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
    end = 8

class tokenType(Enum):
    # Order Matters. Case sensitive for keywords.
    KEYWORD_IF = r"if"
    KEYWORD_OUTPUT = r"output"
    KEYWORD_INT = r"integer"
    KEYWORD_DOUBLE = r"double"
    IDENTIFIER = r"[a-zA-Z_][a-zA-Z0-9_]*"
    LITERAL_DOUBLE = r"[0-9]*\.[0-9]*" # Literals are same as constants.
    LITERAL_INTEGER = r"[0-9]*"
    LITERAL_STRING = r'''(['"])(.*?)\1''' # This could also be the alternative source of the error. 
    OP_ASSIGNMENT = r":="
    OP_COLON = r":" # For the type declaration
    OP_EQUAL = r"=" # For the start of an operation.
    OP_LEFTSHIFT = r"<<"
    ENDLINE = r";"
    OP_ARITHMETIC_PLUS = r"\+"
    OP_ARITHMETIC_MINUS = r"-"
    OP_ARITHMETIC_MULTIPLY = r"\*"
    OP_ARITHMETIC_DIVIDE = r"/"
    OP_RELATIONAL_ISEQUAL = r"=="
    OP_RELATIONAL_NOTEQUAL = r"!="
    OP_RELATIONAL_LESSTHAN = r"<"
    OP_RELATIONAL_LESSTHANOREQUAL = r"<="
    OP_RELATIONAL_GREATERTHAN = r">"
    OP_RELATIONAL_GREATERTHANOREQUAL = r">="
    DELIMITER_LEFT_P = r"\("
    DELIMITER_RIGHT_P = r"\)"

class LexicalAnalyzer:
    def __init__(self, fileToTokenize) -> None:
        self.fileName = fileToTokenize

        with open(fileToTokenize, "r") as file:
            self.file = file.read()

        self.atoms = [] # A nested list containing the atoms of each line.
        self.tokens = [] # A list containing the tokens of the file in the form of a tuple (token, type).
        self.symbol_table = {} # Considered as environment
        self.isFirstError = True # Indicates if it is the first error, useful for the error log.

        # The following functions will be called in the constructor.
        self.initDir()
        self.atomizer()
        self.tokenizer()
    
    def initDir(self) -> None:
        """ This function will create a directory for the logs."""
        if not os.path.exists(default_directory):
            os.makedirs(default_directory)

    def checkAtomType(self, char) -> atomType:
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
                isToken = False
                for ttype in tokenType:
                    if re.fullmatch(ttype.value, token):
                        self.tokens.append((token, ttype.name))
                        isToken = True
                        break
                if not isToken:
                    self.reportError(token, lineCount, "Invalid Token Type.", "Lexical Error")
                    self.tokens.append((token, 'err'))
            lineCount += 1
        
        # Debugging
        # print("\nTokenize:")
        # for tup in self.tokens:
        #     print(f"Type: {tup[1]:.32} | Token: {tup[0]}") # 32 is the longest name length of token type. Could've used a more dynamic way to get the length. QOL

        self.writeTokens()

    def writeTokens(self, mode = 'w') -> None:
        """ This function will write the tokens into a file."""
        with open(f'{default_directory}/RES_SYM.txt', mode) as file:
            for tup in self.tokens:
                file.write(f"{tup[1]:.32} token: {tup[0]} \n")

    def reportError(self, targetToken, targetLine, errorMessage = None, errorType = None, mode = 'a') -> None:
        """ This function will report the error of the token with its location."""
        mode = 'w' if self.isFirstError else 'a'
        self.isFirstError = False
        with open(f'{default_directory}/error.txt', mode) as log:
            for count, line in enumerate(self.file.split("\n")):
                if targetLine == count:
                    targetColumn = line.find(targetToken) + 1  # Adding 1 to make it 1-indexed
                    # Has issue since it continues to append instead of overwriting 
                    log.write(f"\nIn {self.fileName}, line {targetLine+1}: {line}, column {targetColumn}.\n\t< {targetToken} >: {errorType} - {errorMessage}")
                    print(f"\nIn {self.fileName}, line {targetLine+1}: {line}, column {targetColumn}.\n\t< {targetToken} >: {errorType} - {errorMessage}")
                    break
    # Once the entire file has been tokenized, then we analyze and report errors. 
    