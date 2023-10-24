import lexicalAnalyzer as lex
from Parser import Parser

if __name__ == "__main__":
    lex = lex.LexicalAnalyzer("src.txt")
    #print(lex.getTokens())
    tokens = [t[::-1] for t in lex.getTokens()]
    parser = Parser(tokens)
    parser.parse()
    #print(parser)