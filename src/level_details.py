class LevelDetails:
    def __init__(self, source_file:str, secret_code:str = None, name:str = None, description:str = None, exit_point_enabled:bool = True, is_final_level:bool = False):
        self._source_file = source_file
        self._secret_code = secret_code
        self._name = name
        self._description = description
        self._exit_point_enabled = exit_point_enabled
        self._is_final_level = is_final_level

    @property
    def source_file(self):
        return self._source_file

    @property
    def secret_code(self):
        return self._secret_code

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def exit_point_enabled(self):
        return self._exit_point_enabled

    @property
    def is_final_level(self):
        return self._is_final_level
