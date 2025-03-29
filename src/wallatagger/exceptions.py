class EnvironmentConfigMissingError(Exception):
    pass


class TOMLConfigMissingError(Exception):
    pass


class WallabagAPIError(Exception):
    def __init__(self, message, request, response=None):
        super().__init__(message)
        self.request = request
        self.response = response
        if self.response:
            self.status_code = self.response.get("status_code", None)
        else:
            self.status_code = None


class EntryGetError(WallabagAPIError):
    pass


class EntryUpdateError(WallabagAPIError):
    pass


class NoNewEntries(Exception):
    pass


# https://www.geeksforgeeks.org/define-custom-exceptions-in-python/
