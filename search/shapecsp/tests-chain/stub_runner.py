import sys, os
# argv: source state --n N --min-b B --max-b B --wall-budget 0
n = sys.argv[sys.argv.index("--n")+1]
b = sys.argv[sys.argv.index("--min-b")+1]
here = os.path.dirname(os.path.abspath(__file__))
marker = os.path.join(here, "seen-%s-%s" % (n, b))
if not os.path.exists(marker):
    open(marker, "w").write("x")
    print("STUB: LOCKED n=%s b=%s" % (n, b)); sys.exit(2)
print("STUB: ok n=%s b=%s" % (n, b)); sys.exit(0)
