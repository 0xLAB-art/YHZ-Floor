import ast, dis, json, sys, types
program, public = sys.argv[1:]
source = open(program).read()
tree = ast.parse(source)
bindings = {}
for n in tree.body:
    if isinstance(n, ast.Import):
        for a in n.names:
            if a.name.split('.')[0] not in {'json', 'sys', 'base64'}:
                bindings[a.asname or a.name.split('.')[0]] = (a.name if a.asname else a.name.split('.')[0], None)
    if isinstance(n, ast.ImportFrom):
        for a in n.names:
            if n.module not in {'json', 'sys', 'base64'}:
                bindings[a.asname or a.name] = (n.module, a.name)
maps = {}
uses = set()
def trace(frame, event, arg):
    if frame.f_code.co_filename != program:
        return None
    frame.f_trace_opcodes = True
    if event == 'opcode':
        code = frame.f_code
        if code not in maps:
            maps[code] = {i.offset: i for i in dis.get_instructions(code)}
        instruction = maps[code].get(frame.f_lasti)
        if instruction and instruction.opname in {'LOAD_NAME', 'LOAD_GLOBAL', 'LOAD_FAST', 'LOAD_DEREF'} and instruction.argval in bindings:
            name = instruction.argval
            module_name, member = bindings[name]
            module = sys.modules.get(module_name)
            expected = getattr(module, member, None) if member else module
            actual = frame.f_globals.get(name) if instruction.opname == 'LOAD_GLOBAL' else frame.f_locals.get(name, frame.f_globals.get(name))
            if module is not None and expected is not None and actual is expected:
                uses.add((name, module_name, member or '', frame.f_lineno, instruction.opname))
    return trace
sys.argv = [program, public]
scope = {'__name__': '__main__', '__file__': program}
sys.settrace(trace)
try:
    exec(compile(source, program, 'exec'), scope)
finally:
    sys.settrace(None)
    sys.stderr.write('\nIMPORT_USE_AUDIT:' + json.dumps(sorted(uses)) + '\n')
