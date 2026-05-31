import re

with open('/Users/egbertielau/.openclaw/workspace/satisficing-lab/dashboard-v3.html', 'r') as f:
    content = f.read()

m = re.search(r'(<script>)(.*?)(</script>)', content, re.DOTALL)
js = m.group(2)

# Step 1: Rename global h() to escHtml()
js = re.sub(r'(?<!\w)function h\(', 'function escHtml(', js)

# Step 2: Replace ALL h(expr) calls to escHtml(expr)
# But need to distinguish function calls from string assignments like h += ...
# 
# Pattern: h is a function call when:
#   - h(...) appears not preceded by += or similar operator
#   - but it CAN appear inside a string template expression like + h(name) +
#
# We look for h(name) patterns where h is NOT the target of an assignment

# Strategy: find all h(...) that look like function calls
# and replace them, UNLESS they're preceded by operators like +=, =, etc

def replace_h_calls(js_code):
    """Replace h(arg) with escHtml(arg) but skip h += / h = / etc"""
    result = []
    i = 0
    while i < len(js_code):
        # Look for 'h(' 
        if js_code[i:i+2] == 'h(':
            # Check context before
            before = js_code[max(0, i-3):i].strip()
            
            # Skip if preceded by operator (assignment, comparison, arithmetic)
            # h +=, h =, h +, h ||, h &&, if (h, return h(, etc
            skip = False
            if before.endswith('+') or before.endswith('=') or before.endswith('>') or before.endswith('<'):
                skip = True
            if before.endswith('||') or before.endswith('&&') or before.endswith('?'):
                skip = True
            if before == 'h' or before == '':
                # Could be the start: var h... but 'h' before '(' without space is rare
                # Actually 'var h =' would have '= ' before
                pass
            
            # Also skip if this IS the function definition itself
            ctx = js_code[max(0, i-10):i+3]
            if 'function h' in ctx or 'function escHtml' in ctx:
                skip = True
            
            if not skip:
                # This is a function call, replace h( with escHtml(
                result.append('escHtml(')
                i += 2
                continue
        
        result.append(js_code[i])
        i += 1
    
    return ''.join(result)

# But this is too aggressive. Let me be smarter:
# Only replace h(expr) where h is NOT the target of a var or assignment

# Better approach: find all h(arg) patterns, check if h is preceded by
# whitespace/punctuation (indicating standalone function call)
# vs preceded by =/+=/> etc (indicating variable assignment)

js = replace_h_calls(js)

# Verify
if 'function h(' in js:
    print("ERROR: function h still defined!")
elif 'function escHtml(' in js:
    print("OK: global h renamed to escHtml")
else:
    print("WARNING: no escHtml found")

new_content = content[:m.start(2)] + js + content[m.end(2):]
with open('/Users/egbertielau/.openclaw/workspace/satisficing-lab/dashboard-v3.html', 'w') as f:
    f.write(new_content)

# Count replacements
h_calls = len(re.findall(r'escHtml\(', js))
print(f"escHtml() calls: {h_calls}")

# Check for remaining h( patterns that might be bugs
remaining = len(re.findall(r'(?<!\w)h\(', js))
print(f"Remaining h( patterns: {remaining}")
