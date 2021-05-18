import requests
import urllib3

import schemas

urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"


class SuapApi:
    BASE_URL = "https://suap.ifba.edu.br/api/v2/"
    API_PATH = {
        "refresh_token": "autenticacao/token/refresh/",
        "token_user": "autenticacao/token/",
        "user_data": "minhas-informacoes/meus-dados",
        "periods": "minhas-informacoes/meus-periodos-letivos/",
        "report_card": "minhas-informacoes/boletim/{}/{}/",
        "virtual_classes": "minhas-informacoes/turmas-virtuais/{}/{}/",
        "list_virtual_class": "minhas-informacoes/turmas-virtuais/{}/",
    }

    def __init__(self, registration=None, password=None, token=None):
        self._token = token
        self._payload_auth = {"username": registration, "password": password}
        self._headers = None

    @property
    def headers(self):
        return {
            "Accept": "application/json",
            "Authorization": f"JWT {self._token}",
        }

    @staticmethod
    def __check_response(response):
        if response.ok:
            return response.json()
        return response.raise_for_status()

    def __post_request(self, path_resource, **kwargs):
        kwargs.setdefault("data", self._payload_auth)
        kwargs.setdefault("headers", self.headers)

        path_complete = self.BASE_URL + path_resource
        response = requests.post(path_complete, **kwargs)
        return self.__check_response(response)

    def __get_request(self, path_resource, **kwargs):
        kwargs.setdefault("headers", self.headers)

        path_complete = self.BASE_URL + path_resource
        response = requests.get(path_complete, **kwargs)
        return self.__check_response(response)

    def get_token_user(self):
        token_content = self.__post_request(self.API_PATH["token_user"])
        self._token = token_content["token"]
        return self._token

    def refresh_token(self):
        payload_refresh_token = dict(token=self._token)
        token_updated = self.__post_request(
            self.API_PATH["refresh_token"], data=payload_refresh_token
        )
        self._token = token_updated["token"]
        return self._token

    def user_data(self):
        user_data_json = self.__get_request(self.API_PATH["user_data"])
        return schemas.UserDataModel(**user_data_json)

    def list_periods(self):
        period_json = self.__get_request(self.API_PATH["periods"])
        return schemas.PeriodModel.parse_obj(period_json)

    def report_card(self, year, period):
        report_card_json = self.__get_request(
            self.API_PATH["report_card"].format(year, period)
        )
        return schemas.ReportCardModel.parse_obj(report_card_json)

    def virtual_period_classes(self, year, period):
        virtual_period_classes_json = self.__get_request(
            self.API_PATH["virtual_classes"].format(year, period)
        )
        return schemas.VirtualPeriodClassesModel.parse_obj(virtual_period_classes_json)

    def virtual_class(self, class_id):
        virtual_class_json = self.__get_request(
            self.API_PATH["list_virtual_class"].format(class_id)
        )
        return schemas.VirtualClassModel(**virtual_class_json)
