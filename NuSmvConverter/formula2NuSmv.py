from pylogics.parsers import parse_pltl
from pylogics.syntax.pltl import Atomic, Since
from pylogics.syntax.base import And, Or, Implies
from random import sample, seed

class PLTL2NuSmv():

    _operand_classes = [Since, Or, And, Implies]

    def __init__(self, formula_str: str, fname: str):
        self._formula = parse_pltl(formula_str)
        self.formula_str = formula_str
        self._fname = f"{fname}.smv"
        self._names = self._extract_names()
        self._controllable = self._get_random_controllable()

    def _extract_names(self):
        queue = [self._formula]
        names = set()
        while len(queue) != 0:
            curr_node = queue.pop(0)
            curr_node_type = type(curr_node)
            if curr_node_type == Atomic:
                names.add(curr_node.name)
            elif curr_node_type in self._operand_classes:
                for op in curr_node.operands:
                    queue.append(op)
            else:
                # Not, Historically, Once case
                queue.append(curr_node.argument)
        return names
    
    def _get_random_controllable(self):
        return sample(list(self._names), k= int(len(self._names) // 2))

    def write_nusmv(self, tableaux_filename:str):
        with open(tableaux_filename, "r") as file:
            lines = file.readlines()
        with open(self._fname, "w") as file:
            file.write("MODULE main\n")
            # Boolean variables
            file.write("VAR\n")
            for name in self._extract_names():
                file.write(f"\t{name} : boolean;\n")
            index_st = lines.index("VAR\n")
            for i in range(index_st+1, len(lines)):
                file.write(f"{lines[i]}")

            file.write("CONTROLLABLES\n")
            file.write("\t")
            for var in self._controllable:
                file.write(f"{var} ")
            file.write("\n")

            
            
def main():
    seed(23)
    formula = "p S q"
    #formula = "!p S (q S (O a))"
    #formula = "O(on_b6_b5 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b8_b7 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b10_b9 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b1_b2 & Y(O(on_b2_b3 & Y(O(on_b3_b4 & Y(O(on_b4_b5 & Y(O(on_b5_b6 & Y(O(on_b6_b7 & Y(O(on_b7_b8 & Y(O(on_b8_b9 & Y(O(on_b9_b10)))))))))))))))))"
    #formula = "p S q & (O(q))"
    #formula = "p -> q"
    fsmv = PLTL2NuSmv(formula_str=formula, fname="pSq")
    fsmv.write_nusmv(tableaux_filename="./examples/pSq/pSq.txt")

if __name__ == "__main__":
    main()