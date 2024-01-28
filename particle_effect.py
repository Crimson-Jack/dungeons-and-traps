from particle_spark import ParticleSpark


class ParticleEffect:
    def __init__(self, surface, position, colors, number_of_sparks, ratio):
        self.surface = surface
        self.position = position
        self.colors = colors
        self.sparks = []
        self.max_number_of_sparks = number_of_sparks
        self.ratio = ratio

    def update(self, map_offset):
        if self.sparks:
            self.delete_expired_sparks()
            for spark in self.sparks:
                spark.update_position(map_offset)
                spark.move()

    def draw(self):
        if self.sparks:
            for spark in self.sparks:
                spark.draw(self.surface)

    def add_spark(self):
        if self.max_number_of_sparks > 0:
            spark_position = list(self.position)
            spark = ParticleSpark(spark_position, self.get_next_color(), self.ratio)
            self.sparks.append(spark)
            self.max_number_of_sparks -= 1

    def delete_expired_sparks(self):
        sparks_copy = [spark for spark in self.sparks if not spark.is_expired()]
        self.sparks = sparks_copy

    def is_expired(self):
        is_expired = False

        if self.max_number_of_sparks == 0:
            sparks_copy = [spark for spark in self.sparks if not spark.is_expired()]
            if len(sparks_copy) == 0:
                is_expired = True

        return is_expired

    def get_next_color(self):
        next_color = self.colors.pop(0)
        self.colors.append(next_color)
        return next_color
