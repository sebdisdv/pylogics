from pylogics.parsers import parse_pltl
from pylogics.syntax.pltl import Atomic, Since
from pylogics.syntax.base import And, Or



class PLTL2NuSmv():

    def __init__(self, formula_str: str, fname: str):
        self._formula = parse_pltl(formula_str)
        self.formula_str = formula_str
        self._fname = f"{fname}.smv"

    def _extract_names(self):
        queue = [self._formula]
        names = []
        while len(queue) != 0:
            curr_node = queue.pop(0)
            curr_node_type = type(curr_node)
            if curr_node_type == Atomic:
                names.append(curr_node.name)
            elif curr_node_type == Since or curr_node_type == Or or curr_node_type == And:
                for op in curr_node.operands:
                    queue.append(op)
            else:
                # Not, Historically, Once case
                queue.append(curr_node.argument)
        return names

    def write_nusmv(self, tableaux_filename:str):
        with open(tableaux_filename, "r") as file:
            lines = file.readlines()
        with open(self._fname, "w") as file:
            file.write(lines[0])
            
            # Boolean variables
            file.write("VAR\n")
            for name in self._extract_names():
                file.write(f"\t{name} : boolean;\n")
            index_st = lines.index("VAR\n")
            for i in range(index_st+1, len(lines)):
                file.write(f"{lines[i]}")
            # Spec
            file.write("LTLSPEC\n")
            file.write(f"\t{self.formula_str}\n")
            
def main():
    #formula = "!p S (q S (O a))"
    #formula = "O(on_b6_b5 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b8_b7 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b10_b9 & Y(O(on_b4_b3 & Y(O(on_b3_b2 & Y(O(on_b2_b1))))))) & O(on_b1_b2 & Y(O(on_b2_b3 & Y(O(on_b3_b4 & Y(O(on_b4_b5 & Y(O(on_b5_b6 & Y(O(on_b6_b7 & Y(O(on_b7_b8 & Y(O(on_b8_b9 & Y(O(on_b9_b10)))))))))))))))))"
    formula = "p S q"
    fsmv = PLTL2NuSmv(formula_str=formula, fname="pSq")
    fsmv.write_nusmv(tableaux_filename="./examples/pSq/pSq.txt")

if __name__ == "__main__":
    main()