#!/bin/sh
#
# Runs all tests (listed below) for API.
# Runs 'em through coverage, and spits html report into ./api-coverage-report.
#
# Assumes it's run from the root of a STARS checkout.

USAGE="Usage: `basename $0` [-n] [credits|submissions|institutions]"

# Defaults:
RUN_COVERAGE=1
RUN_ALL_TESTS=1

while getopts h OPT
do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        n)
            RUN_COVEREAGE=
            ;;
        \?)
            echo $USAGE >&2
            exit 1
            ;;
    esac
done

for PARAM
do
    case "$PARAM" in
        credits)
            RUN_CREDITS_TESTS=1
            RUN_ALL_TESTS=
            ;;
        submissions)
            RUN_SUBMISSIONS_TESTS=1
            RUN_ALL_TESTS=
            ;;
        institutions)
            RUN_INSTITUTIONS_TESTS=1
            RUN_ALL_TESTS=
            ;;
        *)
            echo "invalid argument: $PARAM" >&2
            echo $USAGE >&2
            echo 2
            ;;
    esac
done

CREDITS_API_TESTS="credits.CreditSetResourceTestCase
                   credits.CategoryResourceTestCase
                   credits.SubcategoryResourceTestCase
                   credits.CreditResourceTestCase
                   credits.DocumentationFieldResourceTestCase"

SUBMISSIONS_API_TESTS="submissions.SubmissionSetResourceTestCase
                       submissions.CategorySubmissionResourceTestCase
                       submissions.SubcategorySubmissionResourceTestCase
                       submissions.CreditSubmissionResourceTestCase
                       submissions.DocumentationFieldSubmissionResourceTestCase"

INSTITUTIONS_API_TESTS="institutions.InstitutionResourceTestCase"

if [ $RUN_ALL_TESTS ]
then
    TESTS_TO_RUN="${CREDITS_API_TESTS}
                  ${SUBMISSIONS_API_TESTS}
                  ${INSTITUTIONS_API_TESTS}"
else
    if [ $RUN_CREDITS_TESTS ]
    then
        TESTS_TO_RUN=${CREDITS_API_TESTS}
    fi
    if [ $RUN_SUBMISSIONS_TESTS ]
    then
        TESTS_TO_RUN="${TESTS_TO_RUN} ${SUBMISSIONS_API_TESTS}"
    fi
    if [ $RUN_INSTITUTIONS_TESTS ]
    then
        TESTS_TO_RUN="${TESTS_TO_RUN} ${INSTITUTIONS_API_TESTS}"
    fi
fi

if [ $RUN_COVERAGE ]
then
    # Should set --source parameter based on $TESTS_TO_RUN.
    coverage run --source=stars/apps/submissions/newapi,stars/apps/credits/api,stars/apps/institutions/api ./manage.py test ${TESTS_TO_RUN}
    coverage html --omit="*/test.py" -d api-coverage-report
else
    ./manage.py test ${TESTS_TO_RUN}
fi
