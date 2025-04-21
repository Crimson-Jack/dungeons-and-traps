class Message:
    def __init__(self, text, color, size):
        self.text = text
        self.color = color
        self.size = size

    def get_text(self):
        return self.text

    def get_color(self):
        return self.color

    def get_size(self):
        return self.size
