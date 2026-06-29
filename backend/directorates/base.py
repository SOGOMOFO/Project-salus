from abc import ABC, abstractmethod

class Directorate(ABC):
    NAME = "Base Directorate"

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def objectives(self):
        pass

    @abstractmethod
    def report(self):
        pass
