class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = 0

    def advance(self):
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1

    def error(self, message):
        raise Exception(f"Syntax Error: {message}")

    def match(self, expected_type):
        if self.current_token and self.current_token[0] == expected_type:
            self.advance()
        else:
            self.error(f"Expected {expected_type}, found {self.current_token[0]}")

    def program(self):
        ast = {"Program": []}
        ast["Program"].append(self.declarations())
        ast["Program"].append(self.statements())
        return ast

    def declarations(self):
        ast = {"Declarations": []}
        while self.current_token and self.current_token[0] in ['IDENTIFIER']:
            ast["Declarations"].append(self.declaration())
        return ast

    def declaration(self):
        ast = {"Declaration": []}
        self.match('IDENTIFIER')
        self.match(':')
        ast["Declaration"].append(self.current_token)
        self.match('KEYWORD_INT')
        self.match('ENDLINE')
        return ast

    def statements(self):
        ast = {"Statements": []}
        while self.current_token:
            ast["Statements"].append(self.statement())
        return ast

    def statement(self):
        ast = {"Statement": []}
        if self.current_token[0] == 'IDENTIFIER':
            ast["Statement"].append(self.assignment_statement())
        elif self.current_token[0] == 'KEYWORD_OUTPUT':
            ast["Statement"].append(self.output_statement())
        elif self.current_token[0] == 'KEYWORD_IF':
            ast["Statement"].append(self.if_statement())
        return ast

    def assignment_statement(self):
        ast = {"AssignmentStatement": []}
        self.match('IDENTIFIER')
        self.match(':=')
        ast["AssignmentStatement"].append(self.expression())
        self.match(';')
        return ast

    def output_statement(self):
        ast = {"OutputStatement": []}
        self.match('KEYWORD_OUTPUT')
        self.match('<<')
        ast["OutputStatement"].append(self.output_params())
        self.match(';')
        return ast

    def output_params(self):
        ast = {"OutputParams": []}
        if self.current_token[0] == 'LITERAL_STRING':
            ast["OutputParams"].append(self.current_token)
            self.match('LITERAL_STRING')
        else:
            ast["OutputParams"].append(self.expression())
        return ast

    def if_statement(self):
        ast = {"IfStatement": []}
        self.match('KEYWORD_IF')
        self.match('(')
        ast["IfStatement"].append(self.expression())
        self.match(')')
        ast["IfStatement"].append(self.statement())
        return ast


    ##  EXPRESSION / TERM / FACTOR   ##

    def expression(self):
        return self.simple_expression()

    def simple_expression(self):
        return self.term()

    def term(self):
        return self.factor()

    def factor(self):
        ast = {"Factor": []}
        if self.current_token[0] == 'IDENTIFIER':
            ast["Factor"].append(self.current_token)
            self.match('IDENTIFIER')
        elif self.current_token[0] in ['LITERAL_INTEGER', 'LITERAL_DOUBLE']:
            ast["Factor"].append(self.current_token)
            self.match(self.current_token[0])
        elif self.current_token[0] == '(':
            self.match('(')
            ast["Factor"].append(self.expression())
            self.match(')')
        return ast