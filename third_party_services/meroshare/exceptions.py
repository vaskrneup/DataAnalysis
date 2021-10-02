class WrongMeroShareCredentials(Exception):
    """Any of the given credentials were wrong !!"""


class CantGetCapitalDetails(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShare/capital/' !!"""


class CapitalNotFound(Exception):
    """Cant find the capital with given dp !!"""


class CantGetOwnData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShare/ownDetail/'"""


class CantGetBankData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShareView/myDetail/<BOID>/'"""


class CantGetCoreBankData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/bankRequest/<BANK CODE>/'"""


class CantGetCurrentHoldingsShortNameData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/myPurchase/myShare/'"""


class CantGetShareData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShareView/myShare/'"""


class CantGetPortfolioData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShareView/myShare/'"""


class CantGetPurchaseSourceData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/myPurchase/search/'"""


class CantGetCurrentIssueData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShare/companyShare/currentIssue'"""


class CantGetApplicationReportData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShare/applicantForm/active/search/'"""


class CantGetOldApplicationReportData(Exception):
    """Cant get data from 'https://webbackend.cdsc.com.np/api/meroShare/migrated/applicantForm/search/'"""


class CantChangeMerosharePIN(Exception):
    """Cant change the PIN of meroshare from 'https://meroshare.cdsc.com.np/#/ownProfile'"""


class CantChangeMerosharePassword(Exception):
    """Cant change the password of meroshare from 'https://meroshare.cdsc.com.np/#/ownProfile'"""
