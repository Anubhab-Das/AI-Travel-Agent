from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def invoke_agent(self, messages, thread_id):
        
        pass
