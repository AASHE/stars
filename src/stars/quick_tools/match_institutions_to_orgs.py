from iss.models import Organization

from quick_tools.org_ids import org_ids
from apps.institutions.models import Institution, MemberSuiteInstitution


for i in Institution.objects.filter(ms_institution=None):

    try:
        msi = MemberSuiteInstitution.objects.get(org_name=i.name)
    except MemberSuiteInstitution.DoesNotExist as exc:
        print i, exc
        continue
    except MemberSuiteInstitution.MultipleObjectsReturned as exc:
        msi = MemberSuiteInstitution.objects.filter(
            org_name=i.name).order_by("account_num")[0]

    i.ms_institution = msi

    try:
        i.save()
    except Exception as exc:
        print "COULDN'T SAVE INSTITUTION: ", i, exc
