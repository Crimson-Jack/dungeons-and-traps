from enum import IntEnum


class Weapon(IntEnum):
    SWORD = 1
    BOW = 2

    def next(self):
        my_class = self.__class__
        members = list(my_class)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def previous(self):
        my_class = self.__class__
        members = list(my_class)
        index = members.index(self) - 1
        if index < 0:
            index = len(members) - 1
        return members[index]
