class App:
    def __init__(self, name, containers):
        self.name = name
        self.containers = containers

    def __str__(self):
        return f"App name: {self.name}, Containers: {self.containers}"