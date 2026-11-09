class HydrofiaError(Exception):
    pass


class InvalidHydrofiaFileError(HydrofiaError):
    pass


class InvalidDateError(HydrofiaError):
    pass


class InvalidBatchError(HydrofiaError):
    pass
