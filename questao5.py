import itertools
from typing import List, Dict, Tuple, Set
import re

class LogicalEquivalenceChecker:
    
    def __init__(self):
      self.precedence = {
          '~': 4,
          '&': 3,
          '|': 2,
          '>': 1,
          '=': 1
        }
        
      self.equivalence_rules = {
          "Lei de De Morgan 1": ("~(P & Q)", "(~P | ~Q)"),
          "Lei de De Morgan 2": ("~(P | Q)", "(~P & ~Q)"),
          "Lei da Implicação": ("(P > Q)", "(~P | Q)"),
          "Negação da Implicação": ("~(P > Q)", "(P & ~Q)"),
          "Bicondicional 1": ("(P = Q)", "((P > Q) & (Q > P))"),
          "Bicondicional 2": ("(P = Q)", "((P & Q) | (~P & ~Q))"),
          "Dupla Negação": ("~~P", "P"),
          "Lei de Idempotência AND": ("(P & P)", "P"),
          "Lei de Idempotência OR": ("(P | P)", "P"),
          "Lei Comutativa AND": ("(P & Q)", "(Q & P)"),
          "Lei Comutativa OR": ("(P | Q)", "(Q | P)"),
          "Lei Distributiva 1": ("(P & (Q | R))", "((P & Q) | (P & R))"),
          "Lei Distributiva 2": ("(P | (Q & R))", "((P | Q) & (P | R))"),
          "Lei da Absorção 1": ("(P & (P | Q))", "P"),
          "Lei da Absorção 2": ("(P | (P & Q))", "P")
        }
    
    def print_equivalence_table(self):
        print("\n" + "="*60)
        print(" TABELA DE EQUIVALÊNCIAS LÓGICAS FUNDAMENTAIS")
        print("="*60)
        
        for rule_name, (left, right) in self.equivalence_rules.items():
            print(f"{rule_name:25}: {left:15} ≡ {right}")
        
        print("="*60 + "\n")
    
    def tokenize(self, expression: str) -> List[str]:
        expression = re.sub(r'\s+', '', expression)
        tokens = []
        i = 0
        
        while i < len(expression):
            char = expression[i]
            
            if char in '()&|>=~':
                tokens.append(char)
            elif char.isalpha():
                var = ''
                while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                    var += expression[i]
                    i += 1
                tokens.append(var)
                i -= 1
            
            i += 1
        
        return tokens
    
    def is_operator(self, token: str) -> bool:
        return token in self.precedence
    
    def is_variable(self, token: str) -> bool:
        return token.isalnum() and not self.is_operator(token)
    
    def infix_to_postfix(self, tokens: List[str]) -> List[str]:
        output = []
        operator_stack = []
        
        for token in tokens:
            if self.is_variable(token):
                output.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()
            elif self.is_operator(token):
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       self.is_operator(operator_stack[-1]) and
                       self.precedence[operator_stack[-1]] >= self.precedence[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
        
        while operator_stack:
            output.append(operator_stack.pop())
        
        return output
    
    def extract_variables(self, tokens: List[str]) -> Set[str]:
        return {token for token in tokens if self.is_variable(token)}
    
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
    
    def generate_truth_table(self, expr1: str, expr2: str) -> Tuple[bool, List[Dict]]:
        tokens1 = self.tokenize(expr1)
        tokens2 = self.tokenize(expr2)
        
        postfix1 = self.infix_to_postfix(tokens1)
        postfix2 = self.infix_to_postfix(tokens2)
        
        all_vars = self.extract_variables(tokens1 + tokens2)
        var_list = sorted(list(all_vars))
        
        truth_table = []
        is_equivalent = True
        
        for values in itertools.product([False, True], repeat=len(var_list)):
            assignment = dict(zip(var_list, values))
            
            result1 = self.evaluate_postfix(postfix1, assignment)
            result2 = self.evaluate_postfix(postfix2, assignment)
            
            row = {
                'assignment': assignment.copy(),
                'expr1_result': result1,
                'expr2_result': result2,
                'equivalent': result1 == result2
            }
            
            truth_table.append(row)
            
            if result1 != result2:
                is_equivalent = False
        
        return is_equivalent, truth_table, var_list
    
    def print_truth_table(self, expr1: str, expr2: str, truth_table: List[Dict], var_list: List[str]):
        print(f"\n{'='*70}")
        print(f" TABELA VERDADE - VERIFICAÇÃO DE EQUIVALÊNCIA")
        print(f"{'='*70}")
        print(f"Expressão 1: {expr1}")
        print(f"Expressão 2: {expr2}")
        print(f"{'='*70}")
        
        header = "| "
        for var in var_list:
            header += f"{var:^6} | "
        header += f"{'Expr1':^6} | {'Expr2':^6} | {'Equiv':^6} |"
        
        print(header)
        print("|" + "-"*8 * (len(var_list) + 3) + "|")
        
        for i, row in enumerate(truth_table):
            line = f"| "
            
            for var in var_list:
                value = "T" if row['assignment'][var] else "F"
                line += f"{value:^6} | "
            
            result1 = "T" if row['expr1_result'] else "F"
            result2 = "T" if row['expr2_result'] else "F"
            equiv = "✓" if row['equivalent'] else "✗"
            
            line += f"{result1:^6} | {result2:^6} | {equiv:^6} |"
            print(line)
        
        print(f"{'='*70}\n")
    
    def check_known_equivalences(self, expr1: str, expr2: str) -> List[str]:
        matching_rules = []
        
        expr1_norm = expr1.replace(" ", "")
        expr2_norm = expr2.replace(" ", "")
        
        for rule_name, (left, right) in self.equivalence_rules.items():
            left_norm = left.replace(" ", "")
            right_norm = right.replace(" ", "")
            
            if ((expr1_norm == left_norm and expr2_norm == right_norm) or
                (expr1_norm == right_norm and expr2_norm == left_norm)):
                matching_rules.append(rule_name)
        
        return matching_rules
    
    def verify_logical_equivalence(self, expr1: str, expr2: str) -> Dict:
        print(f"\n🔍 VERIFICANDO EQUIVALÊNCIA LÓGICA")
        print(f"{'='*50}")
        print(f"Expressão 1: {expr1}")
        print(f"Expressão 2: {expr2}")
        
        try:
            known_rules = self.check_known_equivalences(expr1, expr2)
            if known_rules:
                print(f"\n📚 EQUIVALÊNCIA CONHECIDA IDENTIFICADA:")
                for rule in known_rules:
                    print(f"   → {rule}")
            
            is_equivalent, truth_table, var_list = self.generate_truth_table(expr1, expr2)
            
            self.print_truth_table(expr1, expr2, truth_table, var_list)
            
            if is_equivalent:
                print(f"✅ RESULTADO: AS EXPRESSÕES SÃO LOGICAMENTE EQUIVALENTES")
                print(f"   Todas as {len(truth_table)} linhas da tabela verdade coincidem.")
            else:
                print(f"❌ RESULTADO: AS EXPRESSÕES NÃO SÃO LOGICAMENTE EQUIVALENTES")
                
                counterexamples = [row for row in truth_table if not row['equivalent']]
                print(f"   Encontrados {len(counterexamples)} contraexemplo(s):")
                
                for i, row in enumerate(counterexamples[:3], 1):
                    assignment_str = ", ".join([f"{var}={row['assignment'][var]}" 
                                              for var in var_list])
                    print(f"   {i}. {assignment_str} → Expr1: {row['expr1_result']}, Expr2: {row['expr2_result']}")
            
            return {
                'equivalent': is_equivalent,
                'truth_table': truth_table,
                'variables': var_list,
                'known_rules': known_rules
            }
            
        except Exception as e:
            print(f"❌ ERRO na análise: {str(e)}")
            return {'error': str(e)}

def run_test_examples():
    checker = LogicalEquivalenceChecker()
    
    print("🧪 EXECUTANDO EXEMPLOS DE TESTE")
    print("="*60)
    
    test_cases = [
        ("~(P & Q)", "(~P | ~Q)", "Lei de De Morgan - Negação da Conjunção"),
        ("(P > Q)", "(~P | Q)", "Lei da Implicação"),
        ("(P = Q)", "((P & Q) | (~P & ~Q))", "Definição do Bicondicional"),
        ("~~P", "P", "Lei da Dupla Negação"),
        ("(P & Q)", "(P | Q)", "Exemplo de NÃO equivalência")
    ]
    
    results = []
    
    for i, (expr1, expr2, description) in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📋 TESTE {i}: {description}")
        print(f"{'='*60}")
        
        result = checker.verify_logical_equivalence(expr1, expr2)
        results.append((description, result.get('equivalent', False)))
        
        print(f"{'='*60}")
    
    print(f"\n📊 RESUMO DOS TESTES:")
    print(f"{'='*40}")
    for i, (desc, equiv) in enumerate(results, 1):
        status = "✅ EQUIVALENTES" if equiv else "❌ NÃO EQUIVALENTES"
        print(f"Teste {i}: {status}")
        print(f"         {desc}")
    print(f"{'='*40}")
    
    return results

def interactive_mode():
    checker = LogicalEquivalenceChecker()
    
    print(f"\n🎮 MODO INTERATIVO")
    print(f"{'='*50}")
    print("Digite suas próprias expressões para verificar equivalência.")
    print("Para sair, digite 'quit' em qualquer expressão.")
    print(f"{'='*50}")
    
    while True:
        try:
            print(f"\n📝 Digite as expressões:")
            expr1 = input("Expressão 1: ").strip()
            
            if expr1.lower() in ['quit', 'exit', 'q']:
                break
                
            expr2 = input("Expressão 2: ").strip()
            
            if expr2.lower() in ['quit', 'exit', 'q']:
                break
            
            if not expr1 or not expr2:
                print("⚠️  Por favor, digite expressões válidas.")
                continue
            
            result = checker.verify_logical_equivalence(expr1, expr2)
            
            print(f"\n{'='*60}")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Programa interrompido pelo usuário!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    checker = LogicalEquivalenceChecker()
    
    print("🧮 VERIFICADOR DE EQUIVALÊNCIA LÓGICA")
    print("="*50)
    print("Programa para verificar equivalência entre sentenças da lógica proposicional")
    print("Utiliza análise por tabela verdade e conhecimento de equivalências fundamentais")
    print("="*50)
    
    checker.print_equivalence_table()
    
    print("🎯 RESOLVENDO A QUESTÃO 1 COM 5 EXEMPLOS:")
    test_results = run_test_examples()
    
    interactive_mode()
    
    print(f"\n✨ PROGRAMA FINALIZADO!")
    print("Obrigado por usar o Verificador de Equivalência Lógica!")

if __name__ == "__main__":
    main()