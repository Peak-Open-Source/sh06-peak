import json

class Protein:
    def __init__(self, id, method = "Unknown", resolution = "Unknown", coverage = "Unknown"):
        self._id = id
        self._method = method
        self._resolution = resolution
        self._coverage = coverage

    def as_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'resolution': self.resolution,
            'coverage': self.coverage
        }
    
    @property
    def id(self):
        return self._id

    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, val):
        self._method = val
    
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, val):
        self._resolution = val
    
    @property
    def coverage(self):
        return self._coverage
    
    @coverage.setter
    def coverage(self, val):
        self._coverage = val

    def __str__(self):
        return f'{self.uniprot_id}\n  - Method: {self.method}\n  - Resolution: {self.resolution}\n  - Coverage: {self.coverage}'
