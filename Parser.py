class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = 0
        self.parse_tree = []

    def consume(self):
        self.current_token = self.tokens[self.token_index]
        self.token_index += 1

    def match(self, expected_type):
        if self.current_token[0] == expected_type:
            self.parse_tree.append(self.current_token)
            self.consume()
        else:
            raise SyntaxError(f"Expected {expected_type} but got {self.current_token[0]}")

    def program(self):
        self.declarations()
        self.statements()
        
        if self.current_token[0] != 'ENDLINE':
            raise SyntaxError(f"Expected ENDLINE at the end, but got {self.current_token[0]}")

    def declarations(self):
        while self.current_token[0] == 'IDENTIFIER':
            self.declaration_assignment()
            if self.current_token[0] != 'ENDLINE':
                raise SyntaxError(f"Expected ENDLINE after declaration, but got {self.current_token[0]}")

    def declaration_assignment(self):
        self.match('IDENTIFIER')
        if self.current_token[0] != 'OP_ASSIGNMENT':
            # Variable Declaration
            self.match('OP_COLON')
            self.type()
        else:
            # Assignment as Declaration
            self.match('OP_ASSIGNMENT')
            self.expression()
            print(self.parse_tree)
            print(".. Assignment Statement")

    def assignment_statement(self):
        self.match(':=')
        self.expression()
        print(self.parse_tree)

    def type(self):
        if self.current_token[0] in ['KEYWORD_INT', 'KEYWORD_DOUBLE', 'IDENTIFIER']:
            self.match(self.current_token[0])
            print(self.parse_tree)
            print(".. Declaration")
        else:
            raise SyntaxError(f"Invalid type: {self.current_token[0]}")
        

    def statements(self):
        while self.current_token[0] in ['IDENTIFIER', 'KEYWORD_OUTPUT', 'KEYWORD_IF']:
            self.statement()

    def statement(self):
        if self.current_token[0] == 'IDENTIFIER':
            self.assignment_statement()
        elif self.current_token[0] == 'KEYWORD_OUTPUT':
            self.output_statement()
        elif self.current_token[0] == 'KEYWORD_IF':
            self.if_statement()

    def output_statement(self):
        self.match('KEYWORD_OUTPUT')
        self.match('OP_LEFTSHIFT')
        self.output_params()

    def output_params(self):
        if self.current_token[0] == 'LITERAL_STRING':
            self.match('LITERAL_STRING')
            print(self.parse_tree)
            print(".. Output Literal String")
        else:
            self.expression()
            print(self.parse_tree)
            print(".. Output Expression")
            

    def if_statement(self):
        self.match('KEYWORD_IF')
        self.match('DELIMITER_LEFT_P')
        self.condition()
        self.match('DELIMITER_RIGHT_P')
        self.statement()
        print(self.parse_tree)
        print(".. If Statement")

    def expression(self):
        self.simple_expression()

    def simple_expression(self):
        self.term()
        while self.current_token[0] in ['OP_ARITHMETIC_PLUS', 'OP_ARITHMETIC_MINUS']:
            self.match(self.current_token[0])
            self.term()

    def term(self):
        self.factor()
        while self.current_token[0] in ['OP_ARITHMETIC_MULTIPLY', 'OP_ARITHMETIC_DIVide']:
            self.match(self.current_token[0])
            self.factor()

    def factor(self):
        if self.current_token[0] == 'IDENTIFIER':
            self.match('IDENTIFIER')
        elif self.current_token[0] in ['LITERAL_INTEGER', 'LITERAL_DOUBLE']:
            self.match(self.current_token[0])
        elif self.current_token[0] == '(':
            self.match('(')
            self.expression()
            self.match(')')\

    def parse(self):
        while(True):
            self.consume()  # Start parsing from the first token
            self.program()  # Start with the program rule
            self.parse_tree = []

            # Check if we've reached the end of the input
            if self.token_index == len(self.tokens):
                return

    def condition(self):
        self.expression()
        self.relational_expression()

    def relational_expression(self):
        # Based on RES_SYM.txt
        if self.current_token[0] == 'OP_RELATIONAL_GREATERTHANOREQUAL':
            self.match('OP_RELATIONAL_GREATERTHANOREQUAL')
        self.expression()

# Sample usage (continued)
#tokens = [('IDENTIFIER', 'x'),('OP_COLON', ':'),('KEYWORD_INT', 'integer'),('ENDLINE', ';'),
#          ('IDENTIFIER', 'y'),('OP_COLON', ':'),('KEYWORD_DOUBLE', 'double'),('ENDLINE', ';'),
#          ('IDENTIFIER', 'x'), ('OP_ASSIGNMENT', ':='), ('IDENTIFIER', '-5'),('ENDLINE', ';'),
#          ('IDENTIFIER', 'x'), ('OP_ASSIGNMENT', ':='), ('IDENTIFIER', 'x'),('OP_ARITHMETIC_PLUS','+'),('IDENTIFIER', 'y'),('ENDLINE', ';'),
#          ('KEYWORD_OUTPUT', 'output'),('OP_LEFTSHIFT', '<<'), ('LITERAL_STRING', '"Hello World!"'),('ENDLINE', ';'),
#          ('KEYWORD_OUTPUT', 'output'),('OP_LEFTSHIFT', '<<'), ('IDENTIFIER', '-5'), ('ENDLINE', ';'),
#          ('KEYWORD_IF', 'if'),('DELIMITER_LEFT_P', '('), ('IDENTIFIER','x'), ('OP_RELATIONAL_GREATERTHANOREQUAL', '>='), ('IDENTIFIER', '-5'), ('DELIMITER_RIGHT_P', ')'),('KEYWORD_OUTPUT', 'output'),('OP_LEFTSHIFT', '<<'), ('IDENTIFIER', '-5'), ('ENDLINE', ';')
#          ]

#parser = Parser(tokens)
#try:
#    parser.parse()
#    print("Grammar is correct.")
#except SyntaxError as e:
#    print(f"Syntax error: {e}")

