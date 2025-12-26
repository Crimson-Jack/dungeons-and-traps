class LevelDetails:
    def __init__(self, source_file:str, exit_point_enabled:bool = True, secret_code:str = None, name:str = None, description:str = None):
        self._source_file = source_file
        self._exit_point_enabled = exit_point_enabled
        self._secret_code = secret_code
        self._name = name
        self._description = description

    @property
    def source_file(self):
        return self._source_file

    @property
    def exit_point_enabled(self):
        return self._exit_point_enabled

    @property
    def secret_code(self):
        return self._secret_code
