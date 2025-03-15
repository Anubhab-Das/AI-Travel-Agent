from tools.search_tools import SearchTools
from tools.browser_tools import BrowserTool
from tools.calculator_tools import CalculatorTools
from tools.flights_finder import flights_finder
from tools.hotels_finder import hotels_finder
from tools.weather_finder import weather_finder


class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.register_all_tools()

    def register_all_tools(self):
        self.tools["search_internet"] = SearchTools.search_internet
        self.tools["scrape_and_summarize_website"] = BrowserTool.scrape_and_summarize_website
        self.tools["calculate"] = CalculatorTools.calculate
        self.tools["flights_finder"] = flights_finder
        self.tools["hotels_finder"] = hotels_finder

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())

tool_registry = ToolRegistry()