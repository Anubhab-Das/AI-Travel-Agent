# tools/calculator_tools.py

from langchain.tools import tool

class CalculatorTools:
    @tool("Make a calculation")
    def calculate(operation):
        """
        Useful to perform any mathematical calculation, like '200*7' or '5000/2*10'.
        
        Parameters:
            operation (str): A mathematical expression as a string.
        
        Returns:
            str: The result of the calculation or an error message.
        """
        try:
            return eval(operation)
        except Exception as e:
            return f"Error in calculation: {e}"
