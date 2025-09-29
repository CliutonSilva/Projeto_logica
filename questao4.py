import itertools
from typing import List, Dict, Tuple, Optional

class verificando_SAT:
    def __init__(self):
        self.precedence = {
            '~': 4,
            '&': 3, 
            '|': 2, 
            '>': 1,
            '=': 1   
        }
        
        self.right_associative = {'~'}
    
    def tokenize(self, expression: str) -> List[str]:
        tokens = []
        i = 0
        
        while i < len(expression):
            char = expression[i]
            
            if char.isspace():
                i += 1
            elif char in '()&|>=~':
                tokens.append(char)
                i += 1
            elif char.isalpha():
                var = ''
                while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                    var += expression[i]
                    i += 1
                tokens.append(var)
            else:
                i += 1
                
        return tokens
    
    def is_operator(self, token: str) -> bool:
        return token in self.precedence
    
    def is_variable(self, token: str) -> bool:
        return token.isalnum() and not self.is_operator(token)
    
    def infix_to_postfix(self, infix_tokens: List[str]) -> List[str]:
        output = []
        operator_stack = []
        
        for token in infix_tokens:
            if self.is_variable(token):
                output.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
            elif self.is_operator(token):
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       self.is_operator(operator_stack[-1]) and
                       (self.precedence[operator_stack[-1]] > self.precedence[token] or
                        (self.precedence[operator_stack[-1]] == self.precedence[token] and 
                         token not in self.right_associative))):
                    output.append(operator_stack.pop())
                operator_stack.append(token)

        while operator_stack:
            output.append(operator_stack.pop())
        
        return output
    
    def infix_to_prefix(self, infix_tokens: List[str]) -> List[str]:
        reversed_tokens = []
        for token in reversed(infix_tokens):
            if token == '(':
                reversed_tokens.append(')')
            elif token == ')':
                reversed_tokens.append('(')
            else:
                reversed_tokens.append(token)

        postfix = self.infix_to_postfix(reversed_tokens)
        return list(reversed(postfix))
    
    def evaluate_postfix(self, postfix: List[str], assignment: Dict[str, bool]) -> bool:
        stack = []
        
        for token in postfix:
            if self.is_variable(token):
                stack.append(assignment.get(token, False))
            elif token == '~': 
                if stack:
                    operand = stack.pop()
                    stack.append(not operand)
            elif token == '&': 
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(left and right)
            elif token == '|': 
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(left or right)
            elif token == '>':
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(not left or right)
            elif token == '=': 
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(left == right)
        
        return stack[0] if stack else False
    
    def extract_variables(self, tokens: List[str]) -> List[str]:
        variables = set()
        for token in tokens:
            if self.is_variable(token):
                variables.add(token)
        return sorted(list(variables))
    
    def is_satisfiable(self, expression: str) -> Tuple[bool, Optional[Dict[str, bool]], Dict]:
        try:
            infix_tokens = self.tokenize(expression)
            postfix_tokens = self.infix_to_postfix(infix_tokens)
            prefix_tokens = self.infix_to_prefix(infix_tokens)

            variables = self.extract_variables(infix_tokens)
            
            if not variables:
                result = self.evaluate_postfix(postfix_tokens, {})
                return result, {}, {
                    'infix': expression,
                    'postfix': ' '.join(postfix_tokens),
                    'prefix': ' '.join(prefix_tokens),
                    'variables': [],
                    'type': 'tautology' if result else 'contradiction',
                    'satisfying_assignments': [{}] if result else []
                }

            satisfying_assignments = []
            total_assignments = 2 ** len(variables)
            
            for values in itertools.product([False, True], repeat=len(variables)):
                assignment = dict(zip(variables, values))
                if self.evaluate_postfix(postfix_tokens, assignment):
                    satisfying_assignments.append(assignment.copy())
            
            is_sat = len(satisfying_assignments) > 0
            first_satisfying = satisfying_assignments[0] if satisfying_assignments else None

            formula_type = 'satisfiable'
            if len(satisfying_assignments) == total_assignments:
                formula_type = 'tautology'
            elif len(satisfying_assignments) == 0:
                formula_type = 'contradiction'
            
            return is_sat, first_satisfying, {
                'infix': expression,
                'postfix': ' '.join(postfix_tokens),
                'prefix': ' '.join(prefix_tokens),
                'variables': variables,
                'type': formula_type,
                'satisfying_assignments': satisfying_assignments,
                'total_assignments': total_assignments
            }
            
        except Exception as e:
            return False, None, {'error': str(e)}

def main():
    checker = verificando_SAT()
    
    print("🔍 VERIFICADOR DE SATISFATIBILIDADE - LÓGICA PROPOSICIONAL")
    print("=" * 60)
    print("Operadores: ~ (NOT), & (AND), | (OR), > (IMPLIES), = (BICONDITIONAL)")
    print("Variáveis: letras ou palavras (ex: A, B, P1, var)")
    print("Parênteses: ( ) para agrupamento")
    print("=" * 60)
    
    while True:
        print("\n📝 Digite uma sentença lógica (ou 'sair' para encerrar):")
        print("Exemplos: 'A & B', '(P > Q) & P & ~Q', '~(A | B) = (~A & ~B)'")
        
        sentence = input("➤ ").strip()
        
        if sentence.lower() in ['sair', 'exit', 'quit', 'q', 's', 'fim', ]:
            print("👋 Programa encerrado!")
            break
        
        if not sentence:
            print("⚠️  Por favor, digite uma sentença válida.")
            continue
        
        print(f"\n🔎 Analisando: {sentence}")
        print("-" * 40)
        
        is_sat, satisfying_assignment, info = checker.is_satisfiable(sentence)
        
        if 'error' in info:
            print(f"❌ Erro na análise: {info['error']}")
            continue

        if is_sat:
            print(f"\n✅ RESULTADO: SATISFATÍVEL")
            print(f"🎯 Exemplo de atribuição que satisfaz:")
            if satisfying_assignment:
                for var, value in satisfying_assignment.items():
                    print(f"   {var} = {value}")
        else:
            print(f"\n❌ RESULTADO: INSATISFATÍVEL")
            print("🚫 Não existe atribuição que torna a sentença verdadeira")

        if info['type'] == 'tautology':
            print("🌟 Esta é uma TAUTOLOGIA (sempre verdadeira)")
        elif info['type'] == 'contradiction':
            print("⛔ Esta é uma CONTRADIÇÃO (sempre falsa)")

        if 'satisfying_assignments' in info:
            total = info['total_assignments']
            satisfying = len(info['satisfying_assignments'])
            print(f"📊 Estatísticas: {satisfying}/{total} atribuições satisfazem a fórmula")

if __name__ == "__main__":
    main()