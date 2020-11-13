#!/usr/bin/env python
"""Tool to export all rated reports for AASHE

The data is exported into comma-separated-value text files in the
following hierarchical structure.

root folder:    export

reports:        export/reports/*/reports.csv

                where '*' represents the versions of stars.  version
                2.0 reports, for example, are in
                export/reports/2.0/reports.csv.

                reports.csv contains a summary of stars reports.

details:        export/credits/*/**.csv

                where '*' represents, as above, the version of stars,
                and '**' represents the name of an individual credit.
                Credit OP-10, for instance, in version 2.0 of stars,
                is in "export/credits/2.0/OP-10: Landscape Management.csv".

What can you do with these files?  Loading them into a spreadsheet
program is probably a good idea, at least to poke around.  Then you
might want to load them into a database for more programmatic
manipulation.

Archive:  export.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
   855341  12-05-2019 10:52   export/credits/2.0/AC-10: Support for Research.csv
   387837  12-05-2019 10:52   export/credits/2.0/AC-11: Access to Research.csv
  1168240  12-05-2019 10:51   export/credits/2.0/AC-1: Academic Courses.csv
   650134  12-05-2019 10:51   export/credits/2.0/AC-2: Learning Outcomes.csv
   901069  12-05-2019 10:51   export/credits/2.0/AC-3: Undergraduate Program.csv
   564842  12-05-2019 10:51   export/credits/2.0/AC-4: Graduate Program.csv
   544711  12-05-2019 10:51   export/credits/2.0/AC-5: Immersive Experience.csv
   443417  12-05-2019 10:51   export/credits/2.0/AC-6: Sustainability Literacy Assessment.csv
   324836  12-05-2019 10:51   export/credits/2.0/AC-7: Incentives for Developing Courses.csv
  1890260  12-05-2019 10:52   export/credits/2.0/AC-8: Campus as a Living Laboratory.csv
   863706  12-05-2019 10:52   export/credits/2.0/AC-9: Academic Research.csv
   633606  12-05-2019 10:54   export/credits/2.0/EN-10: Inter-Campus Collaboration.csv
   501552  12-05-2019 10:54   export/credits/2.0/EN-11: Continuing Education.csv
   287360  12-05-2019 10:54   export/credits/2.0/EN-12: Community Service.csv
   825151  12-05-2019 10:54   export/credits/2.0/EN-13: Community Stakeholder Engagement.csv
   384758  12-05-2019 10:54   export/credits/2.0/EN-14: Participation in Public Policy.csv
    85518  12-05-2019 10:54   export/credits/2.0/EN-15: Trademark Licensing.csv
    59112  12-05-2019 10:54   export/credits/2.0/EN-16: Hospital Network.csv
   891127  12-05-2019 10:52   export/credits/2.0/EN-1: Student Educators Program.csv
   322807  12-05-2019 10:52   export/credits/2.0/EN-2: Student Orientation.csv
  2267959  12-05-2019 10:53   export/credits/2.0/EN-3: Student Life.csv
  1316564  12-05-2019 10:53   export/credits/2.0/EN-4: Outreach Materials and Publications.csv
   643607  12-05-2019 10:53   export/credits/2.0/EN-5: Outreach Campaign.csv
   297975  12-05-2019 10:53   export/credits/2.0/EN-6: Employee Educators Program.csv
   185102  12-05-2019 10:54   export/credits/2.0/EN-7: Employee Orientation.csv
   227162  12-05-2019 10:54   export/credits/2.0/EN-8: Staff Professional Development.csv
  1230279  12-05-2019 10:54   export/credits/2.0/EN-9: Community Partnerships.csv
   182999  12-05-2019 10:50   export/credits/2.0/IC-1: Institutional Boundary.csv
   154964  12-05-2019 10:50   export/credits/2.0/IC-2: Operational Characteristics.csv
    88234  12-05-2019 10:50   export/credits/2.0/IC-3: Academics and Demographics.csv
   503786  12-05-2019 11:02   export/credits/2.0/IN-1: Innovation 1.csv
   436144  12-05-2019 11:03   export/credits/2.0/IN-2: Innovation 2.csv
   376369  12-05-2019 11:03   export/credits/2.0/IN-3: Innovation 3.csv
   361983  12-05-2019 11:03   export/credits/2.0/IN-4: Innovation 4.csv
  1133173  12-05-2019 10:57   export/credits/2.0/OP-10: Landscape Management.csv
   660608  12-05-2019 10:57   export/credits/2.0/OP-11: Biodiversity.csv
   324585  12-05-2019 10:57   export/credits/2.0/OP-12: Electronics Purchasing.csv
   554711  12-05-2019 10:57   export/credits/2.0/OP-13: Cleaning Products Purchasing.csv
   306354  12-05-2019 10:57   export/credits/2.0/OP-14: Office Paper Purchasing.csv
   273247  12-05-2019 10:57   export/credits/2.0/OP-15: Inclusive and Local Purchasing.csv
   142973  12-05-2019 10:57   export/credits/2.0/OP-16: Life Cycle Cost Analysis.csv
   419028  12-05-2019 10:57   export/credits/2.0/OP-17: Guidelines for Business Partners.csv
   145788  12-05-2019 10:57   export/credits/2.0/OP-18: Campus Fleet.csv
   154727  12-05-2019 10:58   export/credits/2.0/OP-19: Student Commute Modal Split.csv
   670004  12-05-2019 10:55   export/credits/2.0/OP-1: Greenhouse Gas Emissions.csv
   145021  12-05-2019 10:58   export/credits/2.0/OP-20: Employee Commute Modal Split.csv
  1037998  12-05-2019 10:58   export/credits/2.0/OP-21: Support for Sustainable Transportation.csv
  1278932  12-05-2019 10:58   export/credits/2.0/OP-22: Waste Minimization.csv
   615717  12-05-2019 10:59   export/credits/2.0/OP-23: Waste Diversion.csv
   173385  12-05-2019 10:59   export/credits/2.0/OP-24: Construction and Demolition Waste Diversion.csv
   871070  12-05-2019 10:59   export/credits/2.0/OP-25: Hazardous Waste Management.csv
   567359  12-05-2019 10:59   export/credits/2.0/OP-26: Water Use.csv
   753766  12-05-2019 10:59   export/credits/2.0/OP-27: Rainwater Management.csv
    78556  12-05-2019 10:59   export/credits/2.0/OP-28: Wastewater Management.csv
   301718  12-05-2019 10:55   export/credits/2.0/OP-2: Outdoor Air Quality.csv
   354563  12-05-2019 10:55   export/credits/2.0/OP-3: Building Operations and Maintenance.csv
   427795  12-05-2019 10:55   export/credits/2.0/OP-4: Building Design and Construction.csv
   271550  12-05-2019 10:56   export/credits/2.0/OP-5: Indoor Air Quality.csv
   629866  12-05-2019 10:56   export/credits/2.0/OP-6: Food and Beverage Purchasing.csv
   340901  12-05-2019 10:56   export/credits/2.0/OP-7: Low Impact Dining.csv
   868288  12-05-2019 10:56   export/credits/2.0/OP-8: Building Energy Consumption.csv
   210816  12-05-2019 10:56   export/credits/2.0/OP-9: Clean and Renewable Energy.csv
   332329  12-05-2019 11:02   export/credits/2.0/PA-10: Assessing Employee Satisfaction.csv
   412249  12-05-2019 11:02   export/credits/2.0/PA-11: Wellness Program.csv
   284597  12-05-2019 11:02   export/credits/2.0/PA-12: Workplace Health and Safety.csv
   203160  12-05-2019 11:02   export/credits/2.0/PA-13: Committee on Investor Responsibility.csv
   291692  12-05-2019 11:02   export/credits/2.0/PA-14: Sustainable Investment.csv
    70470  12-05-2019 11:02   export/credits/2.0/PA-15: Investment Disclosure.csv
  1443401  12-05-2019 11:00   export/credits/2.0/PA-1: Sustainability Coordination.csv
  4703630  12-05-2019 11:00   export/credits/2.0/PA-2: Sustainability Planning.csv
  1376025  12-05-2019 11:01   export/credits/2.0/PA-3: Governance.csv
   821618  12-05-2019 11:01   export/credits/2.0/PA-4: Diversity and Equity Coordination.csv
   675459  12-05-2019 11:01   export/credits/2.0/PA-5: Assessing Diversity and Equity.csv
  1057251  12-05-2019 11:01   export/credits/2.0/PA-6: Support for Underrepresented Groups.csv
   429711  12-05-2019 11:01   export/credits/2.0/PA-7: Support for Future Faculty Diversity.csv
  1682486  12-05-2019 11:02   export/credits/2.0/PA-8: Affordability and Access.csv
   725554  12-05-2019 11:02   export/credits/2.0/PA-9: Employee Compensation.csv
  1530946  12-05-2019 11:06   export/credits/2.1/AC-10: Support for Research.csv
   760719  12-05-2019 11:06   export/credits/2.1/AC-11: Open Access to Research.csv
   724496  12-05-2019 11:04   export/credits/2.1/AC-1: Academic Courses.csv
  1520663  12-05-2019 11:04   export/credits/2.1/AC-2: Learning Outcomes.csv
  1490331  12-05-2019 11:05   export/credits/2.1/AC-3: Undergraduate Program.csv
   954475  12-05-2019 11:05   export/credits/2.1/AC-4: Graduate Program.csv
   808812  12-05-2019 11:05   export/credits/2.1/AC-5: Immersive Experience.csv
   639852  12-05-2019 11:05   export/credits/2.1/AC-6: Sustainability Literacy Assessment.csv
   534200  12-05-2019 11:05   export/credits/2.1/AC-7: Incentives for Developing Courses.csv
  2884421  12-05-2019 11:05   export/credits/2.1/AC-8: Campus as a Living Laboratory.csv
   781225  12-05-2019 11:06   export/credits/2.1/AC-9: Research and Scholarship.csv
  1357059  12-05-2019 11:09   export/credits/2.1/EN-10: Community Partnerships.csv
  1006704  12-05-2019 11:09   export/credits/2.1/EN-11: Inter-Campus Collaboration.csv
   682658  12-05-2019 11:09   export/credits/2.1/EN-12: Continuing Education.csv
   409285  12-05-2019 11:09   export/credits/2.1/EN-13: Community Service.csv
  1004509  12-05-2019 11:09   export/credits/2.1/EN-14: Participation in Public Policy.csv
   189267  12-05-2019 11:09   export/credits/2.1/EN-15: Trademark Licensing.csv
  1360216  12-05-2019 11:06   export/credits/2.1/EN-1: Student Educators Program.csv
   529977  12-05-2019 11:06   export/credits/2.1/EN-2: Student Orientation.csv
  3630557  12-05-2019 11:07   export/credits/2.1/EN-3: Student Life.csv
  1779805  12-05-2019 11:08   export/credits/2.1/EN-4: Outreach Materials and Publications.csv
   905377  12-05-2019 11:08   export/credits/2.1/EN-5: Outreach Campaign.csv
   653688  12-05-2019 11:08   export/credits/2.1/EN-6: Assessing Sustainability Culture.csv
   600368  12-05-2019 11:08   export/credits/2.1/EN-7: Employee Educators Program.csv
   261796  12-05-2019 11:08   export/credits/2.1/EN-8: Employee Orientation.csv
   446591  12-05-2019 11:08   export/credits/2.1/EN-9: Staff Professional Development.csv
   388938  12-05-2019 11:03   export/credits/2.1/IC-1: Institutional Boundary.csv
   147491  12-05-2019 11:03   export/credits/2.1/IC-2: Operational Characteristics.csv
   178120  12-05-2019 11:04   export/credits/2.1/IC-3: Academics and Demographics.csv
   101461  12-05-2019 11:21   export/credits/2.1/IN-10: Sustainable Dining Certification.csv
   118834  12-05-2019 11:21   export/credits/2.1/IN-11: Grounds Certification.csv
    55492  12-05-2019 11:21   export/credits/2.1/IN-12: Pest Management Certification.csv
    52118  12-05-2019 11:21   export/credits/2.1/IN-13: Spend Analysis.csv
   120945  12-05-2019 11:21   export/credits/2.1/IN-14: Bicycle Friendly University.csv
    82496  12-05-2019 11:21   export/credits/2.1/IN-15: Stormwater Modeling.csv
    52000  12-05-2019 11:21   export/credits/2.1/IN-16: Campus Water Balance.csv
    56976  12-05-2019 11:21   export/credits/2.1/IN-17: Natural Wastewater Systems.csv
   106655  12-05-2019 11:22   export/credits/2.1/IN-18: Pre-Submission Review.csv
    69811  12-05-2019 11:22   export/credits/2.1/IN-19: Community Stakeholder Engagement.csv
   113538  12-05-2019 11:21   export/credits/2.1/IN-1: Sustainability Course Designation.csv
    64185  12-05-2019 11:22   export/credits/2.1/IN-20: Pay Scale Equity.csv
    63440  12-05-2019 11:22   export/credits/2.1/IN-21: Adjunct Faculty Compensation.csv
   181304  12-05-2019 11:22   export/credits/2.1/IN-22: Campus Pride Index.csv
   103996  12-05-2019 11:22   export/credits/2.1/IN-23: Serving Underrepresented Groups.csv
   623830  12-05-2019 11:22   export/credits/2.1/IN-24: Innovation A.csv
   538805  12-05-2019 11:22   export/credits/2.1/IN-25: Innovation B.csv
   507107  12-05-2019 11:22   export/credits/2.1/IN-26: Innovation C.csv
   337438  12-05-2019 11:22   export/credits/2.1/IN-27: Innovation D.csv
    57574  12-05-2019 11:21   export/credits/2.1/IN-2: NSSE Sustainability Education Consortium.csv
   123846  12-05-2019 11:21   export/credits/2.1/IN-3: Academy-Industry Connections.csv
   140592  12-05-2019 11:21   export/credits/2.1/IN-4: Green Athletics.csv
   154670  12-05-2019 11:21   export/credits/2.1/IN-5: Green Event Certification.csv
    64484  12-05-2019 11:21   export/credits/2.1/IN-6: Hospital Network.csv
    77382  12-05-2019 11:21   export/credits/2.1/IN-7: Fair Trade Campus.csv
    80719  12-05-2019 11:21   export/credits/2.1/IN-8: Certified Green Cleaning.csv
   215094  12-05-2019 11:21   export/credits/2.1/IN-9: Green Laboratories.csv
   992291  12-05-2019 11:14   export/credits/2.1/OP-10: Biodiversity.csv
  2188779  12-05-2019 11:14   export/credits/2.1/OP-11: Sustainable Procurement.csv
   142394  12-05-2019 11:14   export/credits/2.1/OP-12: Electronics Purchasing.csv
   151771  12-05-2019 11:14   export/credits/2.1/OP-13: Cleaning and Janitorial Purchasing.csv
   142895  12-05-2019 11:14   export/credits/2.1/OP-14: Office Paper Purchasing.csv
   213037  12-05-2019 11:15   export/credits/2.1/OP-15: Campus Fleet.csv
   310574  12-05-2019 11:15   export/credits/2.1/OP-16: Student Commute Modal Split.csv
   275384  12-05-2019 11:15   export/credits/2.1/OP-17: Employee Commute Modal Split.csv
  1579420  12-05-2019 11:15   export/credits/2.1/OP-18: Support for Sustainable Transportation.csv
  1607834  12-05-2019 11:16   export/credits/2.1/OP-19: Waste Minimization and Diversion.csv
  1058272  12-05-2019 11:11   export/credits/2.1/OP-1: Greenhouse Gas Emissions.csv
   226148  12-05-2019 11:16   export/credits/2.1/OP-20: Construction and Demolition Waste Diversion.csv
  1015479  12-05-2019 11:16   export/credits/2.1/OP-21: Hazardous Waste Management.csv
   545932  12-05-2019 11:17   export/credits/2.1/OP-22: Water Use.csv
   653365  12-05-2019 11:17   export/credits/2.1/OP-23: Rainwater Management.csv
   413724  12-05-2019 11:11   export/credits/2.1/OP-2: Outdoor Air Quality.csv
   870265  12-05-2019 11:11   export/credits/2.1/OP-3: Building Operations and Maintenance.csv
   803921  12-05-2019 11:11   export/credits/2.1/OP-4: Building Design and Construction.csv
   928130  12-05-2019 11:12   export/credits/2.1/OP-5: Building Energy Consumption.csv
   418434  12-05-2019 11:12   export/credits/2.1/OP-6: Clean and Renewable Energy.csv
   632565  12-05-2019 11:13   export/credits/2.1/OP-7: Food and Beverage Purchasing.csv
  2388394  12-05-2019 11:13   export/credits/2.1/OP-8: Sustainable Dining.csv
  1345067  12-05-2019 11:13   export/credits/2.1/OP-9: Landscape Management.csv
   115886  12-05-2019 11:20   export/credits/2.1/PA-10: Investment Disclosure.csv
   335287  12-05-2019 11:20   export/credits/2.1/PA-11: Employee Compensation.csv
   492579  12-05-2019 11:20   export/credits/2.1/PA-12: Assessing Employee Satisfaction.csv
   623186  12-05-2019 11:20   export/credits/2.1/PA-13: Wellness Program.csv
   408855  12-05-2019 11:21   export/credits/2.1/PA-14: Workplace Health and Safety.csv
  1854634  12-05-2019 11:17   export/credits/2.1/PA-1: Sustainability Coordination.csv
  5054003  12-05-2019 11:18   export/credits/2.1/PA-2: Sustainability Planning.csv
  1603927  12-05-2019 11:19   export/credits/2.1/PA-3: Participatory Governance.csv
  1246478  12-05-2019 11:19   export/credits/2.1/PA-4: Diversity and Equity Coordination.csv
   866287  12-05-2019 11:19   export/credits/2.1/PA-5: Assessing Diversity and Equity.csv
  3866682  12-05-2019 11:19   export/credits/2.1/PA-6: Support for Underrepresented Groups.csv
  2204644  12-05-2019 11:19   export/credits/2.1/PA-7: Affordability and Access.csv
   381324  12-05-2019 11:20   export/credits/2.1/PA-8: Committee on Investor Responsibility.csv
   491153  12-05-2019 11:20   export/credits/2.1/PA-9: Sustainable Investment.csv
     4548  12-05-2019 11:22   export/credits/2.2/AC-10: Support for Sustainability Research.csv
     1648  12-05-2019 11:22   export/credits/2.2/AC-11: Open Access to Research.csv
     3580  12-05-2019 11:22   export/credits/2.2/AC-1: Academic Courses.csv
     2761  12-05-2019 11:22   export/credits/2.2/AC-2: Learning Outcomes.csv
     6826  12-05-2019 11:22   export/credits/2.2/AC-3: Undergraduate Program.csv
     2207  12-05-2019 11:22   export/credits/2.2/AC-4: Graduate Program.csv
     3734  12-05-2019 11:22   export/credits/2.2/AC-5: Immersive Experience.csv
     5372  12-05-2019 11:22   export/credits/2.2/AC-6: Sustainability Literacy Assessment.csv
     1691  12-05-2019 11:22   export/credits/2.2/AC-7: Incentives for Developing Courses.csv
    10165  12-05-2019 11:22   export/credits/2.2/AC-8: Campus as a Living Laboratory.csv
     3780  12-05-2019 11:22   export/credits/2.2/AC-9: Research and Scholarship.csv
     3617  12-05-2019 11:22   export/credits/2.2/EN-10: Community Partnerships.csv
     3894  12-05-2019 11:22   export/credits/2.2/EN-11: Inter-Campus Collaboration.csv
     2506  12-05-2019 11:22   export/credits/2.2/EN-12: Continuing Education.csv
     2135  12-05-2019 11:22   export/credits/2.2/EN-13: Community Service.csv
     1636  12-05-2019 11:22   export/credits/2.2/EN-14: Participation in Public Policy.csv
     1003  12-05-2019 11:22   export/credits/2.2/EN-15: Trademark Licensing.csv
     4825  12-05-2019 11:22   export/credits/2.2/EN-1: Student Educators Program.csv
     2699  12-05-2019 11:22   export/credits/2.2/EN-2: Student Orientation.csv
    11904  12-05-2019 11:22   export/credits/2.2/EN-3: Student Life.csv
     3832  12-05-2019 11:22   export/credits/2.2/EN-4: Outreach Materials and Publications.csv
     3586  12-05-2019 11:22   export/credits/2.2/EN-5: Outreach Campaign.csv
     3833  12-05-2019 11:22   export/credits/2.2/EN-6: Assessing Sustainability Culture.csv
     2677  12-05-2019 11:22   export/credits/2.2/EN-7: Employee Educators Program.csv
     1868  12-05-2019 11:22   export/credits/2.2/EN-8: Employee Orientation.csv
     2066  12-05-2019 11:22   export/credits/2.2/EN-9: Staff Professional Development and Training.csv
      661  12-05-2019 11:22   export/credits/2.2/IN-10: Energy System Certification.csv
      544  12-05-2019 11:22   export/credits/2.2/IN-11: External Reporting Assurance.csv
      586  12-05-2019 11:22   export/credits/2.2/IN-12: Fair Trade Campus.csv
      829  12-05-2019 11:22   export/credits/2.2/IN-13: Fleet Certification.csv
      997  12-05-2019 11:22   export/credits/2.2/IN-14: Food Bank.csv
     1087  12-05-2019 11:22   export/credits/2.2/IN-15: Full-Time Faculty Employment.csv
     1322  12-05-2019 11:22   export/credits/2.2/IN-16: Green Athletics.csv
     1024  12-05-2019 11:22   export/credits/2.2/IN-17: Green Cleaning Certification.csv
     1374  12-05-2019 11:22   export/credits/2.2/IN-18: Green Event Certification.csv
     1143  12-05-2019 11:22   export/credits/2.2/IN-19: Green Laboratory Program.csv
     1199  12-05-2019 11:22   export/credits/2.2/IN-1: Academy-Industry Connections.csv
     2339  12-05-2019 11:22   export/credits/2.2/IN-20: Grounds Certification.csv
      637  12-05-2019 11:22   export/credits/2.2/IN-21: Health and Safety Management Certification.csv
      982  12-05-2019 11:22   export/credits/2.2/IN-22: Hospital Network.csv
      775  12-05-2019 11:22   export/credits/2.2/IN-23: Laboratory Animal Welfare.csv
      642  12-05-2019 11:22   export/credits/2.2/IN-24: Natural Wastewater Systems.csv
      934  12-05-2019 11:22   export/credits/2.2/IN-25: Network for Student Social Innovation.csv
     1201  12-05-2019 11:22   export/credits/2.2/IN-26: Nitrogen Footprint.csv
      766  12-05-2019 11:22   export/credits/2.2/IN-27: Online Sustainability Course.csv
      707  12-05-2019 11:22   export/credits/2.2/IN-28: Pay Scale Equity.csv
     1027  12-05-2019 11:22   export/credits/2.2/IN-29: Pest Management Certification.csv
      565  12-05-2019 11:22   export/credits/2.2/IN-2: Anchor Institution Network.csv
      826  12-05-2019 11:22   export/credits/2.2/IN-30: Sanctuary Institution.csv
      666  12-05-2019 11:22   export/credits/2.2/IN-31: Serving Underrepresented Students.csv
      880  12-05-2019 11:22   export/credits/2.2/IN-32: Single-Use Plastic Ban.csv
      645  12-05-2019 11:22   export/credits/2.2/IN-33: Social Enterprise.csv
      635  12-05-2019 11:22   export/credits/2.2/IN-34: Spend Analysis.csv
      653  12-05-2019 11:22   export/credits/2.2/IN-35: Stakeholder Engagement Standard.csv
      647  12-05-2019 11:22   export/credits/2.2/IN-36: Stormwater Modeling.csv
      682  12-05-2019 11:22   export/credits/2.2/IN-37: Student Living Wage.csv
      720  12-05-2019 11:22   export/credits/2.2/IN-38: Sustainability Course Designation.csv
     1264  12-05-2019 11:22   export/credits/2.2/IN-39: Sustainability Office Diversity Program.csv
     1114  12-05-2019 11:22   export/credits/2.2/IN-3: Bicycle Friendly University.csv
     1442  12-05-2019 11:22   export/credits/2.2/IN-40: Sustainability Projects Fund.csv
     1001  12-05-2019 11:22   export/credits/2.2/IN-41: Textbook Affordability.csv
      950  12-05-2019 11:22   export/credits/2.2/IN-42: Voter Education and Support.csv
      762  12-05-2019 11:22   export/credits/2.2/IN-43: Water Balance.csv
     1033  12-05-2019 11:22   export/credits/2.2/IN-44: Wellbeing Certification.csv
      563  12-05-2019 11:22   export/credits/2.2/IN-45: Work College.csv
      612  12-05-2019 11:22   export/credits/2.2/IN-46: Zero Waste Certification.csv
     1145  12-05-2019 11:22   export/credits/2.2/IN-47: Innovation A.csv
     1159  12-05-2019 11:22   export/credits/2.2/IN-48: Innovation B.csv
     1159  12-05-2019 11:22   export/credits/2.2/IN-49: Innovation C.csv
      976  12-05-2019 11:22   export/credits/2.2/IN-4: Campus Pride Index.csv
     1159  12-05-2019 11:22   export/credits/2.2/IN-50: Innovation D.csv
      859  12-05-2019 11:22   export/credits/2.2/IN-5: Carbon Mitigation Project Development.csv
      670  12-05-2019 11:22   export/credits/2.2/IN-6: Center for Sustainability Across the Curriculum.csv
      591  12-05-2019 11:22   export/credits/2.2/IN-7: Community Garden.csv
     2090  12-05-2019 11:22   export/credits/2.2/IN-8: Dining Services Certification.csv
      743  12-05-2019 11:22   export/credits/2.2/IN-9: Diversity and Equity Recognition.csv
     4256  12-05-2019 11:22   export/credits/2.2/OP-10: Biodiversity.csv
     4000  12-05-2019 11:22   export/credits/2.2/OP-11: Sustainable Procurement.csv
     1266  12-05-2019 11:22   export/credits/2.2/OP-12: Electronics Purchasing.csv
     1035  12-05-2019 11:22   export/credits/2.2/OP-13: Cleaning and Janitorial Purchasing.csv
     1262  12-05-2019 11:22   export/credits/2.2/OP-14: Office Paper Purchasing.csv
     2034  12-05-2019 11:22   export/credits/2.2/OP-15: Campus Fleet.csv
     3430  12-05-2019 11:22   export/credits/2.2/OP-16: Commute Modal Split.csv
     3345  12-05-2019 11:22   export/credits/2.2/OP-17: Support for Sustainable Transportation.csv
    13329  12-05-2019 11:22   export/credits/2.2/OP-18: Waste Minimization and Diversion.csv
      981  12-05-2019 11:22   export/credits/2.2/OP-19: Construction and Demolition Waste Diversion.csv
     6443  12-05-2019 11:22   export/credits/2.2/OP-1: Emissions Inventory and Disclosure.csv
     5250  12-05-2019 11:22   export/credits/2.2/OP-20: Hazardous Waste Management.csv
     5302  12-05-2019 11:22   export/credits/2.2/OP-21: Water Use.csv
     2573  12-05-2019 11:22   export/credits/2.2/OP-22: Rainwater Management.csv
     5727  12-05-2019 11:22   export/credits/2.2/OP-2: Greenhouse Gas Emissions.csv
     2304  12-05-2019 11:22   export/credits/2.2/OP-3: Building Design and Construction.csv
     1932  12-05-2019 11:22   export/credits/2.2/OP-4: Building Operations and Maintenance.csv
     5821  12-05-2019 11:22   export/credits/2.2/OP-5: Building Energy Efficiency.csv
     4704  12-05-2019 11:22   export/credits/2.2/OP-6: Clean and Renewable Energy.csv
     5612  12-05-2019 11:22   export/credits/2.2/OP-7: Food and Beverage Purchasing.csv
     8140  12-05-2019 11:22   export/credits/2.2/OP-8: Sustainable Dining.csv
     6078  12-05-2019 11:22   export/credits/2.2/OP-9: Landscape Management.csv
     2541  12-05-2019 11:22   export/credits/2.2/PA-10: Sustainable Investment.csv
     1109  12-05-2019 11:22   export/credits/2.2/PA-11: Investment Disclosure.csv
     2090  12-05-2019 11:22   export/credits/2.2/PA-12: Employee Compensation.csv
     3898  12-05-2019 11:22   export/credits/2.2/PA-13: Assessing Employee Satisfaction.csv
     3325  12-05-2019 11:22   export/credits/2.2/PA-14: Wellness Program.csv
     1463  12-05-2019 11:22   export/credits/2.2/PA-15: Workplace Health and Safety.csv
     5833  12-05-2019 11:22   export/credits/2.2/PA-1: Sustainability Coordination.csv
     6489  12-05-2019 11:22   export/credits/2.2/PA-2: Sustainability Planning.csv
     4630  12-05-2019 11:22   export/credits/2.2/PA-3: Inclusive and Participatory Governance.csv
     1257  12-05-2019 11:22   export/credits/2.2/PA-4: Reporting Assurance.csv
     4758  12-05-2019 11:22   export/credits/2.2/PA-5: Diversity and Equity Coordination.csv
     4885  12-05-2019 11:22   export/credits/2.2/PA-6: Assessing Diversity and Equity.csv
     9785  12-05-2019 11:22   export/credits/2.2/PA-7: Support for Underrepresented Groups.csv
     2174  12-05-2019 11:22   export/credits/2.2/PA-8: Affordability and Access.csv
     1833  12-05-2019 11:22   export/credits/2.2/PA-9: Committee on Investor Responsibility.csv
      546  12-05-2019 11:22   export/credits/2.2/PRE-1: Executive Letter.csv
     3166  12-05-2019 11:22   export/credits/2.2/PRE-2: Points of Distinction.csv
     3466  12-05-2019 11:22   export/credits/2.2/PRE-3: Institutional Boundary.csv
      678  12-05-2019 11:22   export/credits/2.2/PRE-4: Operational Characteristics.csv
      914  12-05-2019 11:22   export/credits/2.2/PRE-5: Academics and Demographics.csv
    43729  12-05-2019 12:07   export/reports/2.0/reports.csv
    57851  12-05-2019 12:07   export/reports/2.1/reports.csv
      325  12-05-2019 12:07   export/reports/2.2/reports.csv
---------                     -------
120363929                     300 files

"""
import csv
import datetime
import string


from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet
from stars.apps.third_parties.utils import (export_credit_csv,
                                            export_submissionset_csv)


def clean_filename(filename):

    for target, replacement in [
            ('/', '-'), (':', ''), (" ", "_")]:

        string.replace(filename, target, replacement)

    return filename


for creditset in CreditSet.objects.filter(version__gte="2"):

    submissionsets = SubmissionSet.objects.filter(
        status='r').order_by(
            "institution__name").filter(
                creditset=creditset).exclude(
                    institution__name="AASHE Test Campus")

    for category in creditset.category_set.all():

        for subcategory in category.subcategory_set.all():

            for credit in subcategory.credit_set.all():

                filename = 'export/credits/%s/%s.csv' % (
                    creditset.version, credit)

                filename = clean_filename(filename)

                export_credit_csv(credit,
                                  submissionsets,
                                  outfilename=filename)

    filename = 'export/reports/%s/reports.csv' % creditset.version

    filename = clean_filename(filename)

    export_submissionset_csv(submissionsets, outfilename=filename)
