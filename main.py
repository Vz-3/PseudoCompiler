import lexicalAnalyzer as lex
<<<<<<< Updated upstream
from syntaxAnalyzer import SyntaxAnalyzer
=======
from Parser import Parser
>>>>>>> Stashed changes

if __name__ == "__main__":
    lex = lex.LexicalAnalyzer("src.txt")
    #parser = Parser.parse(lex.getTokens())
    #print(lex.getTokens())
    tokens = [t[::-1] for t in lex.getTokens()]
    parser = Parser(tokens)
    parser.parse()
    #print(reversed_tuples)
    #print(parser)