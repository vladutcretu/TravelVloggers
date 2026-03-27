class EmailAlreadyExistsError(Exception):
    pass


class UserDoesntExistError(Exception):
    pass


class EmailOrPasswordIncorrectError(Exception):
    pass


class AccessTokenInvalidError(Exception):
    pass


class VloggerAlreadyExistsError(Exception):
    pass


class VloggerDoesntExistError(Exception):
    pass


class VideoIdAlreadyExistsError(Exception):
    pass


class CountryDoesntExistError(Exception):
    pass


class YoutubeDataNotFoundError(Exception):
    pass
