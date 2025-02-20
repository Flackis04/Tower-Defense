import trace
import cProfile
import dis
import trace
import pycallgraph2
from pycallgraph2.output import GraphvizOutput
from market import Market, make_market, MarketButton
import main  # Import main.py

# Ensure main() is correctly defined in main.py
def main_function():
    main.main()  # Call the function from main.py

# Trace execution
tracer = trace.Trace(count=True, trace=True)
tracer.run('main_function()')  # ✅ Pass function as a string
  # ✅ Function should be passed, not a string

# Disassemble function bytecode
#dis.dis(main)  # ✅ Or use dis.Bytecode(main).dis() for Python 3.11+

# Call graph visualization
"""with pycallgraph2.PyCallGraph(output=GraphvizOutput()):
    main()  # ✅ Call the function"""

# Profile performance
#cProfile.run('main()')  # ✅ Pass as a string
