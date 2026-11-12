import ast
import unittest
from audit import transform


class TransformTests(unittest.TestCase):
    def apply(self, source):
        return transform(source, {'json', 'sys', 'base64'})

    def test_unused_module(self):
        source = 'import hashlib\nprint(7)\n'
        result, edits, imports, _ = self.apply(source)
        self.assertEqual(result, '\nprint(7)\n')
        self.assertEqual(edits[0]['before'], 'import hashlib\n')
        self.assertEqual(imports[0]['classification'], 'conservatively_unused')

    def test_alias_used(self):
        source = 'import hashlib as h\nprint(h.sha256(b"x"))\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_from_import_used_annotation(self):
        source = 'from typing import Tuple\ndef f() -> Tuple[int, int]:\n    return 1, 2\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_mixed_statement_preserved(self):
        source = 'from typing import List, Tuple\ndef f() -> Tuple[int, int]:\n    return 1, 2\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_nested_import_preserved(self):
        source = 'def f():\n    import hashlib\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_shadowed_binding_preserved(self):
        source = 'import hashlib\ndef f(hashlib):\n    return hashlib\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_dynamic_globals_preserved(self):
        source = 'import hashlib\nprint(globals()["hash" + "lib"])\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_dynamic_modules_preserved(self):
        source = 'import hashlib\nimport sys\nprint(sys.modules)\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_string_annotation_preserved(self):
        source = 'from typing import Tuple\ndef f() -> "Tuple[int, int]":\n    return 1, 2\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_wildcard_preserved(self):
        source = 'from typing import *\nprint(7)\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_unknown_module_side_effects_preserved(self):
        source = 'import unknown_plugin\nprint(7)\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_semicolon_preserved(self):
        source = 'import hashlib; print(7)\n'
        self.assertEqual(self.apply(source)[0], source)

    def test_multiline_removal(self):
        source = 'from typing import (\n    List,\n    Dict,\n)\nprint(7)\n'
        result = self.apply(source)[0]
        self.assertEqual(result, '\n\n\n\nprint(7)\n')
        ast.parse(result)

    def test_syntax_preserved(self):
        source = 'import hashlib\nnot python @\n'
        self.assertEqual(self.apply(source)[0], source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
