from __future__ import annotations
from functools import lru_cache
import re

import requests as requests

from third_party_services.meroshare.exceptions import (
    CapitalNotFound, WrongMeroShareCredentials,
    CantGetOwnData, CantGetBankData, CantGetCoreBankData,
    CantGetCapitalDetails, CantGetShareData, CantGetPortfolioData,
    CantGetPurchaseSourceData, CantGetCurrentIssueData, CantGetApplicationReportData,
    CantGetOldApplicationReportData, CantGetCurrentHoldingsShortNameData,
)


class MeroShare:
    """
    Provides various function that is provided by the website.
    """
    headers = {
        "Connection": "keep-alive",
        "Host": "webbackend.cdsc.com.np",
        "Origin": "https://meroshare.cdsc.com.np",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    WRONG_PASSWORD_DOCUMENTATION_COMPILED_RE = re.compile(r"<documentation>(.*?)</documentation>")
    WRONG_PASSWORD_MESSAGE_COMPILED_RE = re.compile(r"<message>(.*?)</message>")

    def __init__(self, *, dp: str, username: str, password: str, pin: str):
        """
        :param dp: dp field that is used in login.
        :param username: username field that is used in login.
        :param password: password field that is used in login.
        """
        self.dp = str(dp)
        self.id = self.get_id_for_dp(str(dp))
        self.username = username
        self.password = password
        self.pin = pin

        self.account_data = {}
        self._bank_data = {}

    # FOR DATA THAT DOESN'T CHANGE !!
    @property
    @lru_cache(maxsize=1)
    def boid(self) -> str:
        """
            Gets boid of the user.
            NOTE: Will be cached !!
        """
        if not self.account_data:
            self.load_initial_account_data()

        return self.account_data.get("demat")

    @property
    @lru_cache(maxsize=1)
    def bank_data(self) -> dict:
        """
            Get data about the bank
            NOTE: Will be cached !!
        """

        if self._bank_data:
            return self._bank_data

        bank_data_resp = self.get(f"https://webbackend.cdsc.com.np/api/meroShareView/myDetail/{self.boid}")

        if bank_data_resp.ok:
            bank_data = bank_data_resp.json()
            self._bank_data = bank_data
            return self._bank_data
        else:
            raise CantGetBankData(f"Code CODE: '{bank_data_resp.status_code}' when getting bank details.")

    @property
    @lru_cache(maxsize=1)
    def bank_code(self) -> str:
        """
            Gets Bank code, that can be used to make further requests to get bank specific data.
            NOTE: Will be cached !!
        """

        return self.bank_data.get("bankCode")

    @property
    @lru_cache(maxsize=1)
    def crn(self) -> str:
        """
            Gets core bank details
            NOTE: Will be cached !!
        """

        core_bank_data_resp = self.get(f"https://webbackend.cdsc.com.np/api/bankRequest/{self.bank_code}")

        if core_bank_data_resp.ok:
            return core_bank_data_resp.json().get("crnNumber")
        else:
            raise CantGetCoreBankData(f"Got CODE: '{core_bank_data_resp.status_code}' when getting Core Bank Details.")

    # UTILS FUNCTIONS FOR MAKING REQUESTS !!
    def request(self, url: str, method="GET", headers: dict = None, *args, **kwargs) -> requests.Response:
        """Internal request handler for better control."""

        headers = headers or {}
        return requests.request(
            *args,
            method=method,
            url=url,
            headers={**self.headers, **headers},
            **kwargs
        )

    def get(self, url: str, *args, **kwargs) -> requests.Response:
        """Internal request handler for better control."""

        return self.request(url, *args, method="GET", **kwargs)

    def post(self, url: str, *args, **kwargs) -> requests.Response:
        """Internal request handler for better control."""

        return self.request(url, *args, method="POST", **kwargs)

    # UTILS FOR GETTING ADDITIONAL DATA !!
    def get_id_for_dp(self, dp) -> int:
        """Gets id for capital provided, if not found error will be raised."""

        capital_names = self.get("https://webbackend.cdsc.com.np/api/meroShare/capital/")

        if capital_names.ok:
            for name in capital_names.json():
                if name.get("code") == dp:
                    return name.get("id")

            raise CapitalNotFound(f"Capital with {dp} not found !")
        else:
            raise CantGetCapitalDetails(f"Got CODE: '{capital_names.status_code}' when getting capitals.")

    # FOR DATA THAT MIGHT CHANGE !!
    def load_initial_account_data(self) -> MeroShare:
        """Loads account details, that will be later used to make other requests."""

        own_details = self.get("https://webbackend.cdsc.com.np/api/meroShare/ownDetail/")
        if own_details.ok:
            self.account_data = {**self.account_data, **own_details.json()}
        else:
            raise CantGetOwnData(f"Got CODE: '{own_details.status_code}' when getting OwnDetail")

        return self

    def _get_shares_holdings(self, page: int, query_size: int = 200) -> dict:
        """Gets share holdings for a particular page."""

        share_detail_resp = self.post(
            "https://webbackend.cdsc.com.np/api/meroShareView/myShare/",
            json={
                "sortBy": "CCY_SHORT_NAME",
                "demat": [self.boid],
                "clientCode": self.dp,
                "page": page,
                "size": query_size,
                "sortAsc": True
            }
        )

        if share_detail_resp.ok:
            return share_detail_resp.json()
        else:
            raise CantGetShareData(f"Got CODE: '{share_detail_resp.status_code}' when getting MyShares.")

    def get_current_holdings_short_names(self):
        """Gets shortnames for current holdings from 'https://meroshare.cdsc.com.np/#/purchase'"""
        current_holdings_short_name_resp = self.get(
            "https://webbackend.cdsc.com.np/api/myPurchase/myShare/"
        )

        if current_holdings_short_name_resp.ok:
            return current_holdings_short_name_resp.json()
        else:
            raise CantGetCurrentHoldingsShortNameData(f"Got CODE: '{current_holdings_short_name_resp.status_code}'")

    def get_shares_holdings(self, query_size: int = 200, page: int = None) -> list[dict]:
        """Gets my current shares from 'https://meroshare.cdsc.com.np/#/shares'"""

        if page is None:
            current_page = 1
            all_shares = []

            while current_page is not None:
                share_data = self._get_shares_holdings(page=current_page, query_size=query_size)

                if share_data.get("totalItems") is None:
                    break

                if share_data.get("totalItems") < query_size:
                    current_page = None
                else:
                    current_page += 1

                all_shares += share_data.get("meroShareDematShare")

            return all_shares
        else:
            return self._get_shares_holdings(query_size=query_size, page=page).get("meroShareDematShare")

    def _get_portfolio_holdings(self, query_size: int = 200, page: int = None) -> dict:
        """Gets portfolio holdings with price for a particular page."""

        share_detail_resp = self.post(
            "https://webbackend.cdsc.com.np/api/meroShareView/myPortfolio/",
            json={
                "sortBy": "script",
                "demat": [self.boid],
                "clientCode": self.dp,
                "page": page,
                "size": query_size,
                "sortAsc": True
            }
        )

        if share_detail_resp.ok:
            return share_detail_resp.json()
        else:
            raise CantGetPortfolioData(f"Got CODE: '{share_detail_resp.status_code}' when getting PortfolioShares.")

    def get_portfolio_holdings(self, query_size: int = 200, page: int = None) -> dict:
        """Gets current shares with recent price from 'https://meroshare.cdsc.com.np/#/portfolio'"""

        if page is None:
            current_page = 1
            all_shares = []
            total_value_as_of_previous_closing = 0
            total_value_as_of_last_transaction = 0

            while current_page is not None:
                share_data = self._get_portfolio_holdings(page=current_page, query_size=query_size)

                if share_data.get("totalItems") is None:
                    break

                if share_data.get("totalItems") < query_size:
                    current_page = None
                else:
                    current_page += 1

                all_shares += share_data.get("meroShareMyPortfolio")
                total_value_as_of_last_transaction = share_data.get("totalValueOfLastTransPrice")
                total_value_as_of_previous_closing = share_data.get("totalValueOfPrevClosingPrice")

            return {
                "all_shares": all_shares,
                "total_value_as_of_last_transaction": total_value_as_of_last_transaction,
                "total_value_as_of_previous_closing": total_value_as_of_previous_closing,
            }
        else:
            share_data = self._get_shares_holdings(query_size=query_size, page=page)
            return {
                "all_shares": share_data.get("meroShareMyPortfolio"),
                "total_value_as_of_last_transaction": share_data.get("totalValueOfLastTransPrice"),
                "total_value_as_of_previous_closing": share_data.get("totalValueOfPrevClosingPrice"),
            }

    def get_purchase_source(self, scrip: str) -> list[dict]:
        """Gets purchase source data from 'https://meroshare.cdsc.com.np/#/purchase'"""

        scrip = scrip.upper()

        scrip_resp = self.post(
            "https://webbackend.cdsc.com.np/api/myPurchase/search/",
            json={
                "demat": self.boid,
                "scrip": scrip
            }
        )

        if scrip_resp.ok:
            return scrip_resp.json()
        else:
            raise CantGetPurchaseSourceData(f"Got CODE: {scrip_resp.status_code}.")

    def get_current_issue(self):
        """Gets current issue from 'https://meroshare.cdsc.com.np/#/asba'"""

        current_issue_resp = self.post(
            "https://webbackend.cdsc.com.np/api/meroShare/companyShare/currentIssue",
            json={
                "filterFieldParams": [
                    {
                        "key": "companyIssue.companyISIN.script",
                        "alias": "Scrip"
                    },
                    {
                        "key": "companyIssue.companyISIN.company.name",
                        "alias": "Company Name"
                    },
                    {
                        "key": "companyIssue.assignedToClient.name",
                        "value": "",
                        "alias": "Issue Manager"
                    }
                ],
                "page": 1,
                "size": 10,
                "searchRoleViewConstants": "VIEW_OPEN_SHARE",
                "filterDateParams": [
                    {"key": "minIssueOpenDate", "condition": "", "alias": "", "value": ""},
                    {"key": "maxIssueCloseDate", "condition": "", "alias": "", "value": ""}
                ]
            }
        )

        if current_issue_resp.ok:
            data = current_issue_resp.json()

            return {
                "current_issue": data.get("object"),
                "applicable_count": data.get("totalCount")
            }
        else:
            raise CantGetCurrentIssueData(f"Got CODE: {current_issue_resp.status_code}.")

    def _get_new_application_report(self, page, size=200):
        """Gets application report from active TAB"""

        application_report_resp = self.post(
            "https://webbackend.cdsc.com.np/api/meroShare/applicantForm/active/search/",
            json={
                "filterFieldParams": [
                    {"key": "companyShare.companyIssue.companyISIN.script", "alias": "Scrip"},
                    {"key": "companyShare.companyIssue.companyISIN.company.name",
                     "alias": "Company Name"}
                ],
                "page": page,
                "size": size,
                "searchRoleViewConstants": "VIEW_APPLICANT_FORM_COMPLETE",
                "filterDateParams": [
                    {"key": "appliedDate", "condition": "", "alias": "", "value": ""},
                    {"key": "appliedDate", "condition": "", "alias": "", "value": ""}
                ]
            }
        )

        if application_report_resp.ok:
            return application_report_resp.json()
        else:
            raise CantGetApplicationReportData(f"Got CODE: {application_report_resp.status_code}.")

    def _get_old_application_report(self, page, size=200):
        """Gets application report from Old Application Report TAB."""

        old_application_report_resp = self.post(
            "https://webbackend.cdsc.com.np/api/meroShare/migrated/applicantForm/search/",
            json={
                "filterFieldParams": [
                    {"key": "companyShare.companyIssue.companyISIN.script", "alias": "Scrip"},
                    {"key": "companyShare.companyIssue.companyISIN.company.name", "alias": "Company Name"}
                ],
                "page": page,
                "size": size,
                "searchRoleViewConstants": "VIEW",
                "filterDateParams": [
                    {"key": "appliedDate", "condition": "", "alias": "", "value": ""},
                    {"key": "appliedDate", "condition": "", "alias": "", "value": ""}
                ]
            }
        )

        if old_application_report_resp.ok:
            return old_application_report_resp.json()
        else:
            raise CantGetOldApplicationReportData(f"Got CODE: {old_application_report_resp.status_code}.")

    def _get_application_report_func(self, type_="NEW"):
        """For better management of application report functions !!"""

        report_functions = {
            "NEW": self._get_new_application_report,
            "OLD": self._get_old_application_report
        }
        return report_functions[type_]

    def _get_application_report(self, type_, page=None, size=200):
        """Gets application report from `https://meroshare.cdsc.com.np/#/asba` -> old or new"""

        if page is None:
            current_page = 1
            all_reports = []
            total_count = 0

            while current_page is not None:
                share_data = self._get_application_report_func(type_=type_)(page=current_page, size=size)  # NOQA

                if share_data.get("totalCount") is None:
                    break

                if share_data.get("totalCount") < size:
                    current_page = None
                else:
                    current_page += 1

                all_reports += share_data.get("object")
                total_count = share_data.get("totalCount")

            return {
                "all_reports": all_reports,
                "total_count": total_count
            }
        else:
            share_data = self._get_application_report_func(type_=type_)(page=page, size=size)  # NOQA
            return {
                "all_reports": share_data.get("object"),
                "total_count": share_data.get("totalCount")
            }

    def get_new_application_report(self, page=None, size=200):
        """Gets application report from `https://meroshare.cdsc.com.np/#/asba`"""
        return self._get_application_report(page=page, size=size, type_="NEW")

    def get_old_application_report(self, page=None, size=200):
        """Gets old application report from `https://meroshare.cdsc.com.np/#/asba`"""
        return self._get_application_report(page=page, size=size, type_="OLD")

    # FOR DOING A PARTICULAR TASK !!
    def login(self) -> MeroShare:
        """logs in to the site and saves auth token for making further requests."""

        login_resp = requests.post(
            "https://webbackend.cdsc.com.np/api/meroShare/auth/",
            json={
                "clientId": self.id,
                "username": self.username,
                "password": self.password,
            }
        )

        if login_resp.ok:
            # This will keep track of user authentication !!
            self.headers = {**self.headers, "Authorization": login_resp.headers.get("Authorization")}
            self.load_initial_account_data()  # load user data, for making further requests !!
            return self
        else:
            raise WrongMeroShareCredentials(
                f"\nDOCUMENTATION: {self.WRONG_PASSWORD_DOCUMENTATION_COMPILED_RE.findall(login_resp.text)}\n"
                f"MESSAGE: {self.WRONG_PASSWORD_MESSAGE_COMPILED_RE.findall(login_resp.text)}"
            )

    # TODO: ACCEPT PURCHASE SOURCE !!
    # TODO: DO EDIS i.e. TRANSFER SHARES AFTER ACCEPTING PURCHASE SOURCE !!
    # TODO: APPLY TO NEW IPOS !!
    # TODO: CHANGE PIN !!
    # TODO: CHANGE PASSWORD !!
