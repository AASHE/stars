import logging
import os
import requests
import shutil
import time
import uuid
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError

from stars.apps.bt_etl import (
    datapoints, institutions, reports, submissionvalues)


ETL_SCRIPTS = [
    (datapoints, "datapoint.json"),
    (institutions, "institution.json"),
    (reports, "report.json"),
    (submissionvalues, "submissionvalue.json")]


BT_HOST = settings.STARS_BENCHMARKS_HOST


logger = logging.getLogger()


class Command(BaseCommand):
    help = """
        Extracts and transforms data for the STARS Benchamarking Tool
        and notifies the BT that the data is available.
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.start_time = time.time()
        self.key = uuid.uuid4().get_hex()
        self.etl_dir = os.path.join(settings.MEDIA_ROOT, "etl")
        self.target_dir = os.path.join(self.etl_dir, self.key)
        os.mkdir(self.target_dir)
        self.bt_api_url = "https://%s/api/etl/" % BT_HOST

    def handle(self, *args, **options):

        if BT_HOST is None:
            error_message = (
                "No BT_HOST variable set in environment.  ETL failed.")
            logger.error(error_message)
            raise CommandError(error_message)
            return

        self.run_etl_scripts()
        self.package_files_for_bt()
        self.trigger_bt_webworker()

        # cull_old_exports()

    def run_etl_scripts(self):
        """Runs ETL scripts, returns list of files generated."""
        for etl_script, outfile in ETL_SCRIPTS:
            out_path = os.path.join(self.target_dir, outfile)
            etl_script.extract_and_transform(out_path)

    def package_files_for_bt(self):
        """ Compresses the data and puts them in a special
        place.  Returns compressed file name."""
        archive_name = shutil.make_archive(
            base_name=self.target_dir,
            format="gztar",
            root_dir=self.etl_dir,
            base_dir=self.key)
        return archive_name

    def trigger_bt_webworker(self):

        post_data = {
            'key': self.key,
            'timestamp': '%d' % int(time.time()),
        }
        response = requests.post(self.bt_api_url, data=post_data)

        return response

    def cull_old_exports(self):
        pass

# runs the extract and transorm script
# stores the files under /media/etl/[key].tar.gz
# issues a GET request to /api/etl/?key=[key]&timestamp=[timestamp]
# exports should be deleted after some time period (a week?)
# key must be unique timestamp is the time of the export

# The tar archive must contain a directory named key. So,
# fk12jf.tar.gz should expand to a folder called fk12jf.

# It must also contain the following files:

# datapoint.json
# institution.json
# report.json
# submissionvalue.json
