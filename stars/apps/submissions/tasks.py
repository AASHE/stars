"""
    Celery tasks
"""
from logging import getLogger

from celery import shared_task
from celery.decorators import task
from django.contrib.auth.models import User
from django.core.cache import cache

from stars.apps.credits.models import CreditSet, Subcategory
from stars.apps.institutions.models import Institution, MigrationHistory
from stars.apps.migrations.utils import (
    create_ss_mirror,
    migrate_ss_version,
    migrate_submission,
)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.api import (
    CategoryPieChart,
    SubategoryPieChart,
    SummaryPieChart,
)
from stars.apps.submissions.export.excel import build_report_export
from stars.apps.submissions.export.pdf import build_certificate_pdf
from stars.apps.submissions.models import SubmissionSet, SubcategoryQuartiles

logger = getLogger()


@task()
def hello_world():
    " A simple test task so I can test celery "
    logger.info("Hello World")


@task()
def build_pdf_export(id):
    # returns the name of the exported file.
    logger.info("starting pdf export(ss: %d)" % id)
    ss = SubmissionSet.objects.get(pk=id)
    pdf = ss.get_pdf()
    logger.info("pdf export done(ss: %d)" % id)
    print pdf.name
    return pdf.name


@task()
def build_excel_export(id):
    ss = SubmissionSet.objects.get(pk=id)
    logger.info("starting excel export(ss: %d)" % id)
    report = build_report_export(ss)
    logger.info("excel export done(ss: %d)" % id)
    return report


@task()
def take_snapshot_task(ss, user):
    logger.info("starting snapshot: (%d) %s" % (ss.id, ss))
    ss.take_snapshot(user=user)
    logger.info("snapshot completed: (%d) %s" % (ss.id, ss))


@task()
def build_certificate_export(id):
    logger.info("starting certificate export(ss: %d)" % id)
    ss = SubmissionSet.objects.get(pk=id)
    pdf = build_certificate_pdf(ss)
    logger.info("cert build successful")
    from django.core.files.temp import NamedTemporaryFile

    tempfile = NamedTemporaryFile(suffix=".pdf", delete=False)
    pdf.write_pdf(target=tempfile)
    tempfile.close()
    logger.info("cert export done(ss: %d)" % ss.id)
    logger.info(tempfile.name)
    return tempfile.name


@task()
def send_certificate_pdf(id):

    logger.info("starting to send certificate (ss: %d)" % id)
    ss = SubmissionSet.objects.get(pk=id)

    pdf = build_certificate_pdf(ss)

    et = EmailTemplate.objects.get(slug="certificate_to_staff")
    email_context = {"ss": ss}
    et.send_email(
        mail_to=["monika.urbanski@aashe.org"],
        context=email_context,
        attachments=((ss.institution.slug, pdf.getvalue(), "application/pdf"),),
        title="New Certificate: %s" % ss,
    )


@task()
def send_email_with_certificate_attachment(
    ss_id, email_template, email_context, recipients
):

    ss = SubmissionSet.objects.get(pk=ss_id)
    certificate = build_certificate_pdf(submissionset)

    email_template.send_email(
        mail_to=recipients,
        context=email_context,
        attachments=(
            (submissionset.institution.slug, certificate.getvalue(), "application/pdf"),
        ),
    )


@task()
def perform_migration(old_ss_id, new_cs_id, user_email):
    """
        Run the migration and then
        email the Liaison, copying the user
        (if the emails are different)
    """
    # logger = getLogger('stars.user')

    logger.info("Running migration for %d to %s" % (old_ss_id, new_cs_id))

    old_ss = SubmissionSet.objects.get(pk=old_ss_id)
    new_cs = CreditSet.objects.get(pk=new_cs_id)

    logger.info("Running migration for %d to %s" % (old_ss_id, new_cs))

    new_ss = migrate_ss_version(old_ss, new_cs)

    email_to = [old_ss.institution.contact_email]
    if user_email not in email_to:
        email_to.append(user_email)

    try:
        et = EmailTemplate.objects.get(slug="migration_success")
        email_context = {"old_ss": old_ss, "new_ss": new_ss}
        et.send_email(email_to, email_context)

    except EmailTemplate.DoesNotExist:
        logger.error(
            "Migration email template missing",
            extra={"user_email": user_email},
            exc_info=True,
        )

    mh = MigrationHistory(
        institution=new_ss.institution, source_ss=old_ss, target_ss=new_ss
    )
    mh.save()

    logger.info("Done migration for %d to %s" % (old_ss_id, new_cs_id))


@task()
def perform_data_migration(old_ss_id, user_id):
    """
        Just duplicates a submission and archives the old one

        A data migration pulls in data but doesn't use the latest creditset,
        it simply keeps the current creditset.
    """
    old_ss = SubmissionSet.objects.get(pk=old_ss_id)

    logger.info("Running data migration for %d to %s" % (old_ss_id))

    try:
        user = User.objects.get(pk=user_id)
    except:
        user = None

    new_ss = create_ss_mirror(
        old_submissionset=old_ss,
        new_creditset=old_ss.institution.current_submission.creditset,
        registering_user=user,
    )
    new_ss.is_locked = False
    new_ss.save()

    old_ss.institution.current_submission = new_ss
    old_ss.institution.save()

    mh = MigrationHistory(
        institution=new_ss.institution, source_ss=old_ss, target_ss=new_ss
    )
    mh.save()


@task()
def rollover_submission(old_ss_id):
    logger.info("Running Rollover for %d" % old_ss_id)
    old_ss = SubmissionSet.objects.get(pk=old_ss_id)

    logger.info("Creating mirror for %d" % old_ss_id)
    new_ss = create_ss_mirror(old_ss)
    new_ss.is_locked = False
    new_ss.is_visible = True
    new_ss.save()
    new_ss.institution.current_submission = new_ss
    new_ss.institution.save()

    logger.info("Done rollover for %d" % old_ss_id)


def update_pie_api_cache():
    """
        Clear each endpoint's cache and then re-fetch it
    """
    cs = CreditSet.objects.get(pk=5)

    from tastypie.api import Api

    v1_api = Api(api_name="v1")
    v1_api.register(SummaryPieChart())
    v1_api.register(CategoryPieChart())
    v1_api.register(SubategoryPieChart())

    cat_view = CategoryPieChart()
    s_view = SubategoryPieChart()

    # summary
    for cat in cs.category_set.filter(include_in_score=True):
        kwargs = {"pk": cat.id}
        cat_view.obj_get(**kwargs)

        for sub in cat.subcategory_set.all():
            kwargs = {"pk": sub.id}
            s_view.obj_get(**kwargs)


@shared_task(name="submissions.load_subcategory_quartiles")
def load_subcategory_quartiles():
    """Load the SubcategoryQuartiles table.

    Creates SubcategoryQuartiles records for subcategories that don't
    have them.

    """
    # Make sure there's a SubcategoryQuartiles object for each
    # combination of institution_type and Subcategory:
    for institution_type in Institution.get_institution_types():
        for subcategory in Subcategory.objects.all():
            try:
                SubcategoryQuartiles.objects.get(
                    institution_type=institution_type, subcategory=subcategory
                )
            except SubcategoryQuartiles.DoesNotExist:
                SubcategoryQuartiles.objects.create(
                    institution_type=institution_type, subcategory=subcategory
                )
    # Calculate the quartiles:
    for subcategory_quartiles in SubcategoryQuartiles.objects.all():
        subcategory_quartiles.calculate()
