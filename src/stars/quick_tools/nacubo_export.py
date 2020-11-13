"""

    Export excel documents for nacubo

    institution columns


        Name of College/University
        Carnegie Classification:  Type of institution
        Classification - Control - public or private
        FTE
        Year of Data
        Gross Sq Feet of Year that Data given

    2.0 columns:

        MMBTU  consumed OP8
        Electrical Possible Kw - given the gird purchase consumption - verify if available in KW as that is usually what campus invoices state
        Water - OP 26 total water used in gallons
        Carbon Footprint - Scope 1 and 2 ft squared o green energy metric tons of carbon dioxide
        Waste - OP 22  - given out as Tons

    1.2 columns:
"""

from stars.apps.third_parties.utils import UnicodeWriter
import csv

from stars.apps.credits.models import DocumentationField, CreditSet
from stars.apps.submissions.models import (
                                           SubmissionSet,
                                           NumericSubmission,
                                           DateSubmission,
                                           ChoiceSubmission,
                                           CreditUserSubmission,
                                           TextSubmission
                                           )
first_columns = [
                 "Name",
                 "Institution Type",
                 "FTE",
                 "IPEDS ID",
                 "STARS Version",
                 "Date Submitted",
#                  "Gross Sq Feet"
                 ]

"""
  2.0
"""

outfile = open("nacubo/2.0.csv", 'wb')
# csvWriter = UnicodeWriter(outfile)
csvWriter = csv.writer(outfile)

headers = []
headers.extend(first_columns)

field_list_2_0 = [

    ("Institution Control", 4230, ChoiceSubmission),

    # OP-8
    ("Year", 3612, DateSubmission),
    ("Gross Sq Feet", 2810, NumericSubmission),
    ("MMBTU Consumed", 2811, NumericSubmission),
    ("Grid-purchased electricity for buildings", 3603, NumericSubmission),

    # OP 26
    ("Year", 3864, DateSubmission),
    ("Total Water Use", 3030, NumericSubmission),

    # OP 1
    # "Carbon Footprint",
    ("Year", 3646, DateSubmission),
    ("Scope 1 GHG emissions from stationary combustion", 3627, NumericSubmission),
    ("Scope 1 GHG emissions from other sources", 3628, NumericSubmission),
    ("Scope 2 GHG emissions from purchased electricity", 3629, NumericSubmission),
    ("Scope 2 GHG emissions from other sources", 3630, NumericSubmission),

    # Waste
    # OP 22
    ("Year", 3841, DateSubmission),
    ("Waste - Recycled", 2981, NumericSubmission),
    ("Waste - Composted", 2980, NumericSubmission),
    ("Waste - Reused", 3827, NumericSubmission),
    ("Waste - Garbage", 2979, NumericSubmission),]

for f in field_list_2_0:
    df = DocumentationField.objects.get(pk=f[1])
    units = ""
    if f[2] == NumericSubmission:
        units = " [%s]" % df.units
    headers.append("%s(%s) %s" % (f[0], df.credit.identifier, units))
csvWriter.writerow(headers)

print "# of 2.0 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=6).count()

for ss in SubmissionSet.objects.filter(status="r").filter(creditset=6):
    row = [
       ss.institution.name,
       ss.institution.profile.carnegie_class,
       ss.institution.profile.enrollment_fte,
       ss.institution.profile.ipeds_id,
       ss.creditset.version,
       str(ss.date_submitted)
       ]

    for f in field_list_2_0:
        klass = f[2]
        df = DocumentationField.objects.get(pk=f[1])

        cus = CreditUserSubmission.objects.filter(subcategory_submission__category_submission__submissionset=ss)
        cus = cus.get(credit=df.credit)

        if cus.submission_status == "na":
            row.append(u"Not Applicable")
        elif cus.submission_status == 'np' or cus.submission_status == 'ns':
            row.append(u"Not Pursuing")
        else:
            val = klass.objects.filter(documentation_field=df)
            val = unicode(val.get(credit_submission_id=cus.id).value)
            row.append(val)

    csvWriter.writerow(row)

outfile.close()

"""
  1.2
"""


print "# of 1.0 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=2).count()
print "# of 1.1 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=4).count()
print "# of 1.2 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=5).count()

outfile1_0 = open("nacubo/1.0.csv", 'wb')
outfile1_1 = open("nacubo/1.1.csv", 'wb')
outfile1_2 = open("nacubo/1.2.csv", 'wb')
csvWriter1_0 = UnicodeWriter(outfile1_0)
csvWriter1_1 = UnicodeWriter(outfile1_1)
csvWriter1_2 = UnicodeWriter(outfile1_2)
# csvWriter = csv.writer(outfile)

headers = []
headers.extend(first_columns)

cs_1_0 = CreditSet.objects.get(pk=2)
cs_1_1 = CreditSet.objects.get(pk=4)
cs_1_2 = CreditSet.objects.get(pk=5)

# identifiers = []
#
# for f in field_list_2_0:
#     df = DocumentationField.objects.get(pk=f[1])
#     print "---------------------------"
#     print df
#     print "---------------------------"
#
#     ndf = df.get_for_creditset(cs_1_2)
#     print ndf
#
#     if ndf:
#         print "# %s" % ndf.credit.identifier
#         print "('%s', %d, %s)," % (
#             ndf.title,
#             ndf.id,
#             ndf.__class__.__name__)

field_list_1_2 = [
    # institution control

    # OP-7
    ('Year', 2294, TextSubmission),
    ('Building space', 1821, NumericSubmission),
    ('Total building energy consumption', 1820, NumericSubmission),
    ('Start and end dates of the energy consumption', 2294, TextSubmission),

    # OP-22
    ('Year', 2312, TextSubmission),
    ('Water consumption', 2012, NumericSubmission),

    # OP-4
    ('Year', 2278, TextSubmission),
    ('Scope 1 and 2 gross GHG emissions', 1772, NumericSubmission),
    ('Off-site, institution-catalyzed offsets generated', 1773, NumericSubmission),
    ('Carbon offsets purchased', 1774, NumericSubmission),

    # OP-17
    ('Year', 2308, TextSubmission),
    ('Weight of materials recycled', 1967, NumericSubmission),
    ('Weight of materials composted', 1968, NumericSubmission),
    ('Weight of materials disposed as garbage', 1969, NumericSubmission),
]

for f in field_list_1_2:
    df = DocumentationField.objects.get(pk=f[1])
    units = ""
    if f[2] == NumericSubmission:
        units = " [%s]" % df.units
    headers.append("%s(%s) %s" % (f[0], df.credit.identifier, units))

csvWriter1_0.writerow(headers)
csvWriter1_1.writerow(headers)
csvWriter1_2.writerow(headers)

for ss in SubmissionSet.objects.filter(status="r").exclude(creditset=6):
    row = [
        ss.institution.name,
        ss.institution.profile.carnegie_class,
        unicode(ss.institution.profile.enrollment_fte),
        unicode(ss.institution.profile.ipeds_id),
        ss.creditset.version,
        unicode(ss.date_submitted)
    ]

    for f in field_list_1_2:
        klass = f[2]
        df1_2 = DocumentationField.objects.get(pk=f[1])
        df = df1_2.get_for_creditset(ss.creditset)

        if df == None:
            row.append("Not Collected")
        else:
            cus = CreditUserSubmission.objects.filter(
                subcategory_submission__category_submission__submissionset=ss)
            cus = cus.get(credit=df.credit)

            if cus.submission_status == "na":
                row.append(u"Not Applicable")
            elif cus.submission_status == 'np' or cus.submission_status == 'ns':
                row.append(u"Not Pursuing")
            else:
                val = klass.objects.filter(documentation_field=df)
                val = unicode(val.get(credit_submission_id=cus.id).value)
                row.append(val)

    try:
        if ss.creditset.version == "1.0":
            csvWriter1_0.writerow(row)
        if ss.creditset.version == "1.1":
            csvWriter1_1.writerow(row)
        if ss.creditset.version == "1.2":
            csvWriter1_2.writerow(row)
    except:
        print row
        assert False

outfile1_0.close()
outfile1_1.close()
outfile1_2.close()


# print "Creating the Data Dictionary"

# for each field get the
#  - credit name and number
#  - credit info
#  - inline help text
#  - pop-up help text
#  - any units

# outfile = open("nacubo/2.0_data_dictionary.csv", 'wb')
# csvWriter = csv.writer(outfile)
#
# headers = [
#   "Field Name",
#   "Credit ID",
#   "Credit Name",
#   "Credit Criteria",
#   "Credit Measurement",
#   "Inline help-text",
#   "Pop-up help-text",
#   "Units"
# ]
#
# csvWriter.writerow(headers)
#
# for f in field_list:
#
#     klass = f[2]
#     df = DocumentationField.objects.get(pk=f[1])
#
#     row = [
#       df.title,
#       df.credit.identifier,
#       df.credit.title,
#       df.credit.criteria,  # @todo: convert from html
#       df.credit.measurement,
#       df.inline_help_text,
#       df.tooltip_help_text,
#       df.units
#     ]
#     csvWriter.writerow(row)
#
# outfile.close()
#
#
# print "# of 1.2 Institutions"
# print SubmissionSet.objects.filter(status="r").filter(creditset=5).count()
