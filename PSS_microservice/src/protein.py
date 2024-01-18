"""
Class we use to handle direct operations on protein data,
and also as an effective way of storing the data.
"""


class Coverage:
    def __init__(self, lower_bound, upper_bound):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    @property
    def lower_bound(self):
        return self._lower_bound

    def merge(self, other_cov):
        # If within bounds, merge into one larger coverage and return valid
        if self.lower_bound >= other_cov.lower_bound:
            if other_cov.upper_bound > self.lower_bound:
                return [Coverage(other_cov.lower_bound,
                                 max(self.upper_bound,
                                     other_cov.upper_bound))], True
        elif self.lower_bound < other_cov.lower_bound:
            if self.upper_bound > other_cov.lower_bound:
                return [Coverage(self.lower_bound,
                                 max(self.upper_bound,
                                     other_cov.upper_bound))], True

        return [self, other_cov], False


class Protein:
    def __init__(self, id, method="Unknown",
                 resolution="Unknown",
                 coverage="Unknown"):
        self._id = id
        self._method = method
        self._resolution = resolution
        self._coverage = coverage
        self._coverage_list = []
        self._is_alphafold = False

    def as_dict(self) -> dict:
        # Return all instance information into an effective
        # dictionary to be displayed in the combined JSON on the endpoint.
        return {
            'id': self.id,
            'method': self.method,
            'resolution': self.resolution,
            'coverage': self.coverage
        }

    def add_coverage(self, lower_bound, upper_bound):
        self._coverage_list.append(Coverage(lower_bound, upper_bound))

    def merge_coverages(self):
        change_made = True
        while (change_made):  # While updates are still being made
            change_made = False
            updated_list = self._coverage_list[:]
            for i in range(len(self._coverage_list)):
                for j in range(i + 1, len(self._coverage_list)):
                    # Dissolve 2 coverages into 1 bigger one
                    new_coverages, valid = self._coverage_list[i] \
                                           .merge(self._coverage_list[j])

                    # Remove old ones
                    updated_list.remove(self._coverage_list[i])
                    updated_list.remove(self._coverage_list[j])

                    # Add new merged coverage to list, if merge was ≈
                    # Dissolve 2 coverages into 1 bigger one
                    for coverage in new_coverages:
                        updated_list.append(coverage)

                    if valid:
                        change_made = True
                        # Exit - restart loop to compare new merged coverage
                        break

                if change_made:
                    # Exit - restart loop to compare new merged coverage
                    break

            if change_made:  # If the list was actually updated
                self._coverage_list = updated_list

    def calculate_coverages(self) -> int:
        # Running count of all coverage ranges,
        # call after merge preferably unless exceptional circumstances
        count = 0
        for coverage in self._coverage_list:
            count += (coverage.upper_bound - coverage.lower_bound)

        return count

    @property
    def id(self):
        return self._id

    @property
    def method(self):
        return self._method
    
    @property
    def is_alphafold(self):
        return self._is_alphafold
    
    @method.setter
    def is_alphafold(self, val: bool):
        self._is_alphafold = val

    @method.setter
    def method(self, val):
        if val == "NMR":
            self.resolution = "10"
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

    def __str__(self) -> str:
        return f'{self.id}\n \
                 - Method: {self.method}\n \
                 - Resolution: {self.resolution}\n \
                 - Coverage: {self.coverage}'
