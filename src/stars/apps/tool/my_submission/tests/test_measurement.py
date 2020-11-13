"""Tests of behavior related to measurements (metric or US).
"""
import time
from selenium.webdriver.common.by import By

from stars.apps.registration.utils import init_submissionset
from stars.apps.test_utils.live_server import StarsLiveServerTest


class MeasurementLiveServerTest(StarsLiveServerTest):

    fixtures = ['basic_creditset.json']
    # the fixture used to be creditset_v2.json, but it had integrity issues
    # when loading

    def setUp(self, *args, **kwargs):
        super(MeasurementLiveServerTest, self).setUp(*args, **kwargs)
        time.sleep(1)
        init_submissionset(self.institution, self.user)
        self.go_to_reporting_tool()

    def test_for_cache_bug(self):
        """If the view through which users edit credit fields is
        cached, a serious bug can be triggered by the following
        behavior.

          - Pull up a credit with a NumericSubmission field representing
            acres.
          - Enter X.
          - Go to the Settings view.
          - Click the checkbox to indicate your preference for metric,
            then click the Save button.
          - Pull up that same credit.
          - The X acres should display as Y hectares, though
            if the view is cached, X acres are still shown.  If the user
            saves the credit at this point, the X is treated as X
            hectares.  Since we store quantities in their US measure,
            we'd convert X (presumably hectares) into Z acres.  *Then*,
            the next time we pull up that credit, Z acres are converted
            into ZZ hectares, ZZ being a confusing and incorrect number,
            a real numberwang (and a fractionally imaginary wangernumb!).
        """
        # Go to submission:
        my_submission_link = self.patiently_find(look_for='My Submission',
                                                 by=By.LINK_TEXT)
        my_submission_link.click()

        # Pull up credit:
        ic_2_link = self.patiently_find(
            look_for='IC-2: Operational Characteristics',
            by=By.LINK_TEXT)
        ic_2_link.click()

        # Enter 200 acres:
        input_element = self.get_text_input_element(
            'NumericSubmission_2-value')
        input_element.send_keys("200")

        # Save:
        save_in_progress_button = self.get_button_with_text('In progress')
        save_in_progress_button.click()

        # Go to settings:
        time.sleep(1)
        settings_link = self.patiently_find(look_for='Settings',
                                            by=By.LINK_TEXT)
        settings_link.click()

        # Use metric system!
        use_metric_checkbox = self.patiently_find(
            look_for='id_prefers_metric_system',
            by=By.ID)
        use_metric_checkbox.click()

        # Save:
        save_button = self.get_button_with_text('Save')
        save_button.click()

        # Back to the submission . . .
        my_submission_link = self.patiently_find(look_for='My Submission',
                                                 by=By.LINK_TEXT)
        my_submission_link.click()

        # . . . and back to the credit:
        ic_2_link = self.patiently_find(
            look_for='IC-2: Operational Characteristics',
            by=By.LINK_TEXT)
        ic_2_link.click()

        # What were 200 acres should now be ~81 hectares:
        input_element = self.get_text_input_element(
            'NumericSubmission_2-metric_value')
        page_says = input_element.get_attribute('value')

        self.assertEqual(page_says, '80.9372')
