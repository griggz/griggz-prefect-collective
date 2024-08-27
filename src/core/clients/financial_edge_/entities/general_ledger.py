from clients.financial_edge_.baseapi import BaseApi


class GeneralLedger(BaseApi):
    """[summary]

    Args:
        BaseApi ([type]): [description]
    """

    def __init__(self, *args, **kwargs):
        super(GeneralLedger, self).__init__(*args, **kwargs)
        self.entity = ""
        self.type = ""

    # POST FUNCTIONS
    def post_(self, *args, data=None):
        self.entity = "generalledger"
        self.type = "post"

        return self._sky_client._post(url=self._build_path(*args), data=data)

    def patch_(self, *args, data=None):
        self.entity = "generalledger"
        self.type = "patch"

        return self._sky_client._patch(url=self._build_path(*args), data=data)

    # GET FUNCTIONS
    def get_(self, *args, **kwargs):
        self.entity = "generalledger"
        self.type = "get"
        return self._sky_client._get(url=self._build_path(*args), **kwargs)
