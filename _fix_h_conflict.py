import re

with open('/Users/egbertielau/.openclaw/workspace/satisficing-lab/dashboard-v3.html', 'r') as f:
    content = f.read()

m = re.search(r'(<script>)(.*?)(</script>)', content, re.DOTALL)
js = m.group(2)

# Simple approach: replace var h = with var _h = inside functions
# But keep global function h() intact

# Find function bodies
funcs = list(re.finditer(r'function\s+(\w+)\s*\([^)]*\)', js))

changes = []
for i, fm in enumerate(funcs):
    fname = fm.group(1)
    if fname == 'h' or fname == 'a' or fname == 'escHtml':
        continue
    
    fstart = fm.start()
    brace = js.find('{', fstart)
    if brace == -1: continue
    depth = 1
    pos = brace + 1
    while depth > 0 and pos < len(js):
        if js[pos] == '{': depth += 1
        elif js[pos] == '}': depth -= 1
        pos += 1
    fend = pos
    body = js[fstart:fend]
    
    # Find var h =  or var h= declarations
    for vm in re.finditer(r'\bvar\s+h\s*=', body):
        abs_pos = fstart + vm.start()
        # Replace 'var h =' with 'var _h ='
        old_text = js[abs_pos:abs_pos + vm.end() - vm.start()]
        new_text = old_text.replace('var h', 'var _h', 1)
        changes.append((abs_pos, abs_pos + vm.end() - vm.start(), new_text))

# Apply in reverse
changes.sort(key=lambda x: x[0], reverse=True)
for start, end, new_text in changes:
    js = js[:start] + new_text + js[end:]

new_content = content[:m.start(2)] + js + content[m.end(2):]
with open('/Users/egbertielau/.openclaw/workspace/satisficing-lab/dashboard-v3.html', 'w') as f:
    f.write(new_content)

print(f"Renamed {len(changes)} var h -> var _h")
for start, _, new_text in sorted(changes, key=lambda x: x[0]):
    line = js[:start].count('\n') + 1
    print(f"  Line ~{line}")
