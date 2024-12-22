init python:
  class FMODError(RuntimeError):
    """
    Raised whenever a C library call to FMOD does not return an OK.
    """

    def __init__(self, result):
      self.message = 'FMOD encountered an error: ' + str(result)
      super().__init__(self.message)
      self.result = result

    def __str__(self):
      return self.message