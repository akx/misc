import ast
import sys


class ImportedNameFinder(ast.NodeVisitor):
    def __init__(self):
        # Hack – py3.8+ dicts are sorted so we're using them as sorted sets
        self.imported_names = {}

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names[alias.name] = 1

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names[alias.name] = 1


parsed = ast.parse(sys.stdin.read(), filename="<stdin>")
finder = ImportedNameFinder()
finder.visit(parsed)

print("__all__ = [")
for name in finder.imported_names:
    print(f"    '{name}',")
print("]")
