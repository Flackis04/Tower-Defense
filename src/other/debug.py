import trace
import cProfile
import dis
import trace
import pycallgraph2
from pycallgraph2.output import GraphvizOutput
import main                  

                                               
def main_function():
    main.main()                                  

                 
                                             
                                                             
                                             

                               
                                                                    

                          
"""with pycallgraph2.PyCallGraph(output=GraphvizOutput()):
    main()  # ✅ Call the function"""

                     
cProfile.run('main_function()')                      
