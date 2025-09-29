import re
from typing import List, Dict, Tuple, Set

class NaturalLanguageTranslator:
    
    def __init__(self):
        self.symbols = ['M', 'N', 'O', 'P', 'Q', 'R', 'S', 'U', 'V', 'X', 'Y', 'Z']
        self.symbol_index = 0
        self.atomic_propositions = {}
        self.reverse_mapping = {}
        
        self.connective_patterns = {
            'negation': [
                r'\bnão\b', r'\bnao\b', r'\bnem\b', r'\bnunca\b', 
                r'\bfalso que\b', r'\bé falso que\b', r'\bnão é verdade que\b'
            ],
            'conjunction': [
                r'\be\b', r'\bmas\b', r'\bporém\b', r'\btodavia\b', 
                r'\bentretanto\b', r'\bcontudo\b', r'\bem conjunto com\b',
                r'\balém disso\b', r'\btambém\b', r'\bao mesmo tempo\b'
            ],
            'disjunction': [
                r'\bou\b', r'\bou então\b', r'\balternativamente\b',
                r'\bcaso contrário\b', r'\bou bem\b'
            ],
            'implication': [
                r'\bse\b.*\bentão\b', r'\bse\b.*\b,\b', r'\bcaso\b.*\bentão\b',
                r'\bquando\b.*\bentão\b', r'\bimplica que\b', r'\bimplica\b',
                r'\blogo\b', r'\bportanto\b', r'\bassim\b', r'\bconcluímos que\b'
            ],
            'biconditional': [
                r'\bse e somente se\b', r'\bse e só se\b', r'\bequivale a\b',
                r'\bé equivalente a\b', r'\bse e apenas se\b'
            ]
        }
        
        self.proposition_markers = [
            r'\bé verdade que\b', r'\bé o caso que\b', r'\bocorre que\b',
            r'\bacontece que\b', r'\bsabemos que\b', r'\bé fato que\b'
        ]
    
    def clean_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[.,;:!?]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def identify_connectives(self, sentence: str) -> List[Tuple[str, str, int]]:
        connectives_found = []
        
        for conn_type, patterns in self.connective_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    connectives_found.append((conn_type, match.group(), match.start()))
        
        connectives_found.sort(key=lambda x: x[2])
        return connectives_found
    
    def extract_atomic_propositions(self, sentence: str) -> List[str]:
        cleaned = self.clean_text(sentence)
        
        for conn_type, patterns in self.connective_patterns.items():
            for pattern in patterns:
                cleaned = re.sub(pattern, ' CONECTIVO ', cleaned, flags=re.IGNORECASE)
        
        for marker in self.proposition_markers:
            cleaned = re.sub(marker, '', cleaned, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'\bCONECTIVO\b', '|', cleaned)
        
        parts = [part.strip() for part in cleaned.split('|') if part.strip()]
        
        atomic_props = []
        for part in parts:
            if len(part) > 3 and not part.isspace():
                atomic_props.append(part.strip())
        
        return atomic_props
    
    def assign_symbols(self, propositions: List[str]) -> Dict[str, str]:
        mapping = {}
        
        for prop in propositions:
            if prop not in self.atomic_propositions:
                if self.symbol_index < len(self.symbols):
                    symbol = self.symbols[self.symbol_index]
                    self.atomic_propositions[prop] = symbol
                    self.reverse_mapping[symbol] = prop
                    self.symbol_index += 1
                    mapping[prop] = symbol
                else:
                    mapping[prop] = f"P{self.symbol_index}"
                    self.symbol_index += 1
            else:
                mapping[prop] = self.atomic_propositions[prop]
        
        return mapping
    
    def translate_sentence(self, sentence: str) -> Tuple[str, Dict[str, str]]:
        original_sentence = sentence
        cleaned = self.clean_text(sentence)
        
        connectives = self.identify_connectives(cleaned)
        atomic_props = self.extract_atomic_propositions(sentence)
        symbol_mapping = self.assign_symbols(atomic_props)
        
        if not connectives and len(atomic_props) == 1:
            return symbol_mapping[atomic_props[0]], symbol_mapping
        
        formula = cleaned
        
        for prop, symbol in symbol_mapping.items():
            formula = formula.replace(prop.lower(), f" {symbol} ")
        
        for conn_type, patterns in self.connective_patterns.items():
            for pattern in patterns:
                if conn_type == 'negation':
                    formula = re.sub(pattern, ' ~ ', formula, flags=re.IGNORECASE)
                elif conn_type == 'conjunction':
                    formula = re.sub(pattern, ' & ', formula, flags=re.IGNORECASE)
                elif conn_type == 'disjunction':
                    formula = re.sub(pattern, ' | ', formula, flags=re.IGNORECASE)
                elif conn_type == 'implication':
                    formula = re.sub(pattern, ' > ', formula, flags=re.IGNORECASE)
                elif conn_type == 'biconditional':
                    formula = re.sub(pattern, ' = ', formula, flags=re.IGNORECASE)
        
        formula = re.sub(r'\s+', ' ', formula).strip()
        
        tokens = formula.split()
        logical_formula = ""
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token in self.symbols or token in ['~', '&', '|', '>', '=']:
                if token == '~' and i + 1 < len(tokens):
                    logical_formula += f"~{tokens[i+1]} "
                    i += 1
                else:
                    logical_formula += f"{token} "
            i += 1
        
        logical_formula = logical_formula.strip()
        
        if ' ' in logical_formula and not any(op in logical_formula for op in ['&', '|', '>', '=']):
            parts = logical_formula.split()
            if len(parts) == 2:
                logical_formula = f"({parts[0]} & {parts[1]})"
        
        return logical_formula, symbol_mapping
    
    def translate_argument(self, premises: List[str], conclusion: str) -> Dict:
        self.symbol_index = 0
        self.atomic_propositions = {}
        self.reverse_mapping = {}
        
        translated_premises = []
        all_mappings = {}
        
        print(f"🔄 TRADUZINDO ARGUMENTO")
        print(f"{'='*60}")
        
        print(f"\n📋 PREMISSAS:")
        for i, premise in enumerate(premises, 1):
            print(f"P{i}: {premise}")
            formula, mapping = self.translate_sentence(premise)
            translated_premises.append(formula)
            all_mappings.update(mapping)
            print(f"     → {formula}")
        
        print(f"\n🎯 CONCLUSÃO:")
        print(f"C: {conclusion}")
        conclusion_formula, conclusion_mapping = self.translate_sentence(conclusion)
        all_mappings.update(conclusion_mapping)
        print(f"   → {conclusion_formula}")
        
        print(f"\n🔤 MAPEAMENTO DE SÍMBOLOS:")
        print(f"{'='*40}")
        for symbol, prop in self.reverse_mapping.items():
            print(f"{symbol}: {prop}")
        
        print(f"\n⚡ FÓRMULA LÓGICA COMPLETA:")
        print(f"{'='*40}")
        premises_str = " & ".join([f"({p})" for p in translated_premises])
        full_formula = f"({premises_str}) > {conclusion_formula}"
        print(f"({premises_str})")
        print(f"∴ {conclusion_formula}")
        print(f"\nForma de inferência: {full_formula}")
        
        return {
            'premises': translated_premises,
            'conclusion': conclusion_formula,
            'mapping': all_mappings,
            'full_formula': full_formula,
            'reverse_mapping': self.reverse_mapping
        }
    
    def interactive_translation(self):
        print(f"\n🎮 MODO INTERATIVO DE TRADUÇÃO")
        print(f"{'='*50}")
        print("Digite um argumento em linguagem natural para traduzir.")
        print("Formato: Premissa 1, Premissa 2, ..., Conclusão")
        print("Para sair, digite 'quit'")
        print(f"{'='*50}")
        
        while True:
            try:
                print(f"\n📝 Digite o argumento:")
                print("(Separe premissas por ponto-e-vírgula ';' e termine com a conclusão)")
                
                input_text = input("➤ ").strip()
                
                if input_text.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not input_text:
                    print("⚠️  Por favor, digite um argumento válido.")
                    continue
                
                if ';' in input_text:
                    parts = input_text.split(';')
                    premises = [p.strip() for p in parts[:-1]]
                    conclusion = parts[-1].strip()
                else:
                    print("📌 Formato sugerido: 'premissa1; premissa2; conclusão'")
                    print("Assumindo entrada única como premissa simples...")
                    premises = [input_text]
                    conclusion = input("Digite a conclusão: ").strip()
                
                if not conclusion:
                    conclusion = "Verdadeiro"
                
                result = self.translate_argument(premises, conclusion)
                
                print(f"\n{'='*60}")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Programa interrompido!")
                break
            except Exception as e:
                print(f"❌ Erro na tradução: {e}")

def run_examples():
    translator = NaturalLanguageTranslator()
    
    print("🧪 EXEMPLOS DE TRADUÇÃO")
    print("="*60)
    
    examples = [
        {
            'name': 'Modus Ponens Simples',
            'premises': [
                'Se está chovendo então a rua está molhada',
                'Está chovendo'
            ],
            'conclusion': 'A rua está molhada'
        },
        {
            'name': 'Silogismo Disjuntivo',
            'premises': [
                'Ou João foi ao cinema ou João foi ao teatro',
                'João não foi ao cinema'
            ],
            'conclusion': 'João foi ao teatro'
        },
        {
            'name': 'Modus Tollens',
            'premises': [
                'Se Maria estudou então Maria passou na prova',
                'Maria não passou na prova'
            ],
            'conclusion': 'Maria não estudou'
        },
        {
            'name': 'Conjunção e Implicação',
            'premises': [
                'Pedro é inteligente e Pedro é estudioso',
                'Se Pedro é estudioso então Pedro terá sucesso'
            ],
            'conclusion': 'Pedro terá sucesso'
        },
        {
            'name': 'Bicondicional',
            'premises': [
                'Ana vai à festa se e somente se Carlos vai à festa',
                'Carlos vai à festa'
            ],
            'conclusion': 'Ana vai à festa'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"📚 EXEMPLO {i}: {example['name']}")
        print(f"{'='*70}")
        
        result = translator.translate_argument(
            example['premises'], 
            example['conclusion']
        )
        
        print(f"\n✅ Tradução concluída!")
        print(f"{'='*70}")

def main():
    print("🌐 TRADUTOR: LINGUAGEM NATURAL → LÓGICA PROPOSICIONAL")
    print("="*65)
    print("Converte argumentos em português para fórmulas lógicas")
    print("Símbolos disponíveis: M, N, O, P, Q, R, S, U, V, X, Y, Z")
    print("="*65)
    
    print("\n📖 CONECTIVOS RECONHECIDOS:")
    print("• Negação: não, nem, nunca, falso que")
    print("• Conjunção: e, mas, porém, também, ao mesmo tempo")  
    print("• Disjunção: ou, ou então, alternativamente")
    print("• Implicação: se...então, caso...então, implica, logo, portanto")
    print("• Bicondicional: se e somente se, se e só se, equivale a")
    
    run_examples()
    
    translator = NaturalLanguageTranslator()
    translator.interactive_translation()
    
    print(f"\n✨ TRADUTOR FINALIZADO!")
    print("Obrigado por usar o Tradutor de Linguagem Natural!")

if __name__ == "__main__":
    main()