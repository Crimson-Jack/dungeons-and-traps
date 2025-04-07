class SpriteCostume:
    def __init__(self, image, number_of_frames):
        self._image = image
        self._number_of_frames = number_of_frames

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def number_of_frames(self):
        return self._number_of_frames
