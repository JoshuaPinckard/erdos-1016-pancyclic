"""Parse shape0.txt..shape4.txt WITNESS lines and append properly formatted rows to witnesses.csv."""
import re, ast

files = [("shape0.txt", "empirical shape (0,2)(1,5)(1,7)(3,34)(24,39) scaled + scanned 6th"),
         ("shape1.txt", "empirical shape (0,2)(0,37)(1,35)(3,18)(8,39) scaled + scanned 6th"),
         ("shape2.txt", "empirical shape (0,2)(0,33)(1,13)(3,34)(32,35) scaled + scanned 6th"),
         ("shape3.txt", "empirical shape (0,4)(0,5)(1,34)(2,35)(3,15) scaled + scanned 6th"),
         ("shape4.txt", "empirical shape (0,7)(1,8)(2,10)(2,11)(9,21) scaled + scanned 6th")]

rows = []
for fname, label in files:
    with open(fname) as f:
        for line in f:
            m = re.match(r"n=(\d+): WITNESS base5=(\[.*?\]) 6th=(\(.*?\))", line)
            if m:
                n = int(m.group(1))
                base5 = ast.literal_eval(m.group(2))
                sixth = ast.literal_eval(m.group(3))
                chords = base5 + [sixth]
                chord_str = " ".join(f"({a},{b})" for a, b in chords)
                rows.append(f'{n},"{chord_str}",{label}')

with open("witnesses.csv", "a") as out:
    for r in rows:
        out.write(r + "\n")
print(f"appended {len(rows)} rows")
