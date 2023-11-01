import json

"""
Class we use to handle direct operations on protein data, 
and also as an effective way of storing the data.
"""

class Protein:
    def __init__(self, id, database, method = "Unknown", resolution = "Unknown", coverage = "Unknown"):
        self._id = id
        self._database = database
        self._method = method
        self._resolution = resolution
        self._coverage = coverage

    def as_dict(self):
        # Return all instance information into an effective dictionary to be displayed in the combined JSON on the endpoint.
        return {
            'id': self.id,
            'database': self.database,
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
    
    @property
    def database(self):
        return self._database
    
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
        return f'{self.id}\n  - Database: {self.database}\n - Method: {self.method}\n  - Resolution: {self.resolution}\n  - Coverage: {self.coverage}'
