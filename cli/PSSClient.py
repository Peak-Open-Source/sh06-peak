import requests
import json


class PSSClient():
    """
    A helper class for creating and managing endpoint calls.

    Attributes
    ----------
    host : str
        The hostname of the API.
    port : str
        The corresponding port number to the API's host.
    address : str
        The full concatenated address of the hostname and port.

    Methods
    -------

    download(endpoint: str, args: list[str]) -> str || dict[str : str]:
        Performs a GET request on a specified endpoint and returns
        the results.
    get(endpoint: str, args: list[str]) -> dict[str : str]:
        Performs a GET request on a specified endpoint and returns
        the results after converting them from JSON.
    post(endpoint: str, args: list[str]) -> dict[str : str]:
        Performs a POST request on a specified endpoint and returns
        the results after converting them from JSON. These results
        are unlikely to mean anything aside from errors.
    """
    def __init__(self, host: str, port: int = None):
        self._host = host
        self._port = port
        self._address = host if port is None else f"{host}:{str(port)}"

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def address(self):
        return self._address

    def download(self, endpoint, args):
        """
        Performs a GET request on a given endpoint, with optional
        given arguments.

        Parameters
        ----------

        endpoint : str
            The endpoint to perform the GET request on.
        args : list[str]
            Additional arguments to be passed to the endpoint, like IDs and
            queries.

        Returns
        -------
        str || dict[str : str]:
            If successful, the resulting content of the GET request.
            If not successful, an error message in dictionary form.
        bool:
            Whether the request was successful or not.
        """
        result = requests.get(f"{self.address}/{endpoint}/"
                              + "/".join(f"{arg}" for arg in args))
        if result.ok:
            return result.content, True
        else:
            return {"error": "Request failed"}, False

    def get(self, endpoint, args):

        """
        Performs a GET request on a given endpoint, with optional
        given arguments. If successful, JSON loads the resulting content.

        Parameters
        ----------

        endpoint : str
            The endpoint to perform the GET request on.
        args : list[str]
            Additional arguments to be passed to the endpoint, like IDs and
            queries.

        Returns
        -------
        dict[str : str]:
            If successful, the resulting JSON loaded content
            of the GET request. If not successful, an error message
            in dictionary form.
        bool:
            Whether the request was successful or not.
        """
        content, success = self.download(endpoint, args)
        if success:
            return json.loads(content), True
        else:
            return content, False

    def post(self, endpoint, args):
        """
        Performs a POST request on a given endpoint, with optional
        given arguments.

        Parameters
        ----------

        endpoint : str
            The endpoint to perform the POST request on.
        args : list[str]
            Additional arguments to be passed to the endpoint, like IDs and
            files

        Returns
        -------
        dict[str : str]:
            If successful, the resulting JSON loaded content
            of the POST request, likely meaningless. If not successful,
            an error message in dictionary form.
        bool:
            Whether the request was successful or not.
        """
        result = requests.post(f"{self.address}/{endpoint}", json=args)
        if result.ok:
            return json.loads(result.content), True
        else:
            return {"error": "Request failed"}, False
