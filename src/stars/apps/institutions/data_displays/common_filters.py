from stars.apps.institutions.data_displays.filters import Filter, RangeFilter
from stars.apps.submissions.models import SubmissionSet

BASE_1_0_QS = SubmissionSet.objects.filter(status='r')
BASE_1_0_QS = BASE_1_0_QS.filter(expired=False)
BASE_1_0_QS = BASE_1_0_QS.filter(creditset__version__startswith='1.')

COMMON_1_0_FILTERS = [
    Filter(
        key='institution__ms_institution__country',
        title='Country',
        item_list=[
            ('United States', "United States"),
            ('Canada', 'Canada'),
            ('All Other', 'ALL_OTHER_COUNTRIES')
        ],
        base_qs=BASE_1_0_QS
    ),
    Filter(
        key='institution__is_member',
        title='AASHE Membership',
        item_list=[
            ('AASHE Member', True),
            ('Not an AASHE Member', False)
        ],
        base_qs=BASE_1_0_QS
    ),
    Filter(
        key='institution__is_pcc_signatory',
        title='ACUPCC Signatory Status',
        item_list=[
            ('ACUPCC Signatory', True),
            ('Not an ACUPCC Signatory', False)
        ],
        base_qs=BASE_1_0_QS
    ),
    Filter(
        key='rating__name',
        title='STARS Rating',
        item_list=[
            ('Bronze', 'Bronze'),
            ('Silver', 'Silver'),
            ('Gold', 'Gold'),
            ('Platinum', 'Platinum'),
        ],
        base_qs=BASE_1_0_QS
    ),
    RangeFilter(
        key='institution__fte',
        title='FTE Enrollment',
        item_list=[
            ('Less than 200', 'u200', None, 200),
            ('200 - 499', 'u500', 200, 500),
            ('500 - 999', 'u1000', 500, 1000),
            ('1,000 - 1,999', 'u2000', 1000, 2000),
            ('2,000 - 4,999', 'u5000', 2000, 5000),
            ('5,000 - 9,999', 'u10000', 5000, 10000),
            ('10,000 - 19,999', 'u20000', 10000, 20000),
            ('Over 20,000', 'o20000', 20000, None),
        ],
        base_qs=BASE_1_0_QS
    ),
]

BASE_2_0_QS = SubmissionSet.objects.filter(status='r')
BASE_2_0_QS = BASE_2_0_QS.filter(expired=False)
BASE_2_0_QS = BASE_2_0_QS.filter(creditset__version__startswith='2.')

COMMON_2_0_FILTERS = [
    Filter(
        key='institution__ms_institution__country',
        title='Country',
        item_list=[
            ('United States', "United States"),
            ('Canada', 'Canada'),
            ('All Other', 'ALL_OTHER_COUNTRIES')
        ],
        base_qs=BASE_2_0_QS
    ),
    Filter(
        key='institution__is_member',
        title='AASHE Membership',
        item_list=[
            ('AASHE Member', True),
            ('Not an AASHE Member', False)
        ],
        base_qs=BASE_2_0_QS
    ),
    Filter(
        key='institution__is_pcc_signatory',
        title='ACUPCC Signatory Status',
        item_list=[
            ('ACUPCC Signatory', True),
            ('Not an ACUPCC Signatory', False)
        ],
        base_qs=BASE_2_0_QS
    ),
    Filter(
        key='rating__name',
        title='STARS Rating',
        item_list=[
            ('Bronze', 'Bronze'),
            ('Silver', 'Silver'),
            ('Gold', 'Gold'),
            ('Platinum', 'Platinum'),
        ],
        base_qs=BASE_2_0_QS
    ),
    RangeFilter(
        key='institution__fte',
        title='FTE Enrollment',
        item_list=[
            ('Less than 200', 'u200', None, 200),
            ('200 - 499', 'u500', 200, 500),
            ('500 - 999', 'u1000', 500, 1000),
            ('1,000 - 1,999', 'u2000', 1000, 2000),
            ('2,000 - 4,999', 'u5000', 2000, 5000),
            ('5,000 - 9,999', 'u10000', 5000, 10000),
            ('10,000 - 19,999', 'u20000', 10000, 20000),
            ('Over 20,000', 'o20000', 20000, None),
        ],
        base_qs=BASE_2_0_QS
    ),
]
