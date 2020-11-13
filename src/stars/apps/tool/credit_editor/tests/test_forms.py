"""Tests for apps/tool/credit_editor/forms.py.
"""
import tempfile

import django

from stars.apps.test_utils.live_server import StarsLiveServerTest
from stars.apps.tool.credit_editor.forms import RightSizeInputModelForm


# TODO: This doesn't really test anything much, except that a
# RightSizeModelForm will render.  The page isn't bootstrapped, so,
# since bootstrap is doing the right-sizing, we can't check the sizes.


class RightSizeInputModelFormLiveServerTest(StarsLiveServerTest):

    def runTest(self):
        super(RightSizeInputModelFormLiveServerTest, self).runTest()
        test_model_form = TestModelForm()
        html = tempfile.NamedTemporaryFile(suffix='.html')
        html.write("""
        <!DOCTYPE html>
        <HTML lang="en">
          <HEAD>
            <link rel="stylesheet/less"
                  type="text/css"
                  href="{STATIC_URL}bootstrap/css/bootstrap.css">
          </HEAD>
          <BODY>
            <script src="{STATIC_URL}bootstrap/js/jquery.js"
                    type="text/javascript"></script>
            <script src="{STATIC_URL}bootstrap/js/bootstrap.js"
                    type="text/javascript"></script>
            <DIV class="container">
              <FORM>
                {test_form}
              </FORM>
            </DIV>
          </BODY>
        </HTML>""".format(STATIC_URL=django.conf.settings.STATIC_URL,
                          test_form=test_model_form.as_ul()))
        html.flush()
        self.selenium.get('file:///' + html.name)


class TestModel(django.db.models.Model):
    text_input_1 = django.db.models.CharField(
        max_length=1,
        default='-')
    text_input_2 = django.db.models.CharField(
        max_length=2,
        default='--')
    text_input_3 = django.db.models.CharField(
        max_length=3,
        default='-M-')
    text_input_4 = django.db.models.CharField(
        max_length=4,
        default='-MM-')
    text_input_5 = django.db.models.CharField(
        max_length=5,
        default='-MMM-')
    text_input_6 = django.db.models.CharField(
        max_length=6,
        default='-MMMM-')
    text_input_7 = django.db.models.CharField(
        max_length=7,
        default='-MMMMM-')
    text_input_8 = django.db.models.CharField(
        max_length=8,
        default='-MMMMMM-')
    text_input_9 = django.db.models.CharField(
        max_length=9,
        default='-MMMMMMM-')
    text_input_10 = django.db.models.CharField(
        max_length=10,
        default='-MMMMMMMM-')
    text_input_11 = django.db.models.CharField(
        max_length=11,
        default='-MMMMMMMMM-')
    text_input_12 = django.db.models.CharField(
        max_length=12,
        default='-MMMMMMMMMM-')
    text_input_13 = django.db.models.CharField(
        max_length=13,
        default='-MMMMMMMMMMM-')
    text_input_14 = django.db.models.CharField(
        max_length=14,
        default='-MMMMMMMMMMMM-')
    text_input_15 = django.db.models.CharField(
        max_length=15,
        default='-MMMMMMMMMMMMM-')
    text_input_16 = django.db.models.CharField(
        max_length=16,
        default='-MMMMMMMMMMMMMM-')
    text_input_17 = django.db.models.CharField(
        max_length=17,
        default='-MMMMMMMMMMMMMMM-')
    text_input_18 = django.db.models.CharField(
        max_length=18,
        default='-MMMMMMMMMMMMMMMM-')
    text_input_19 = django.db.models.CharField(
        max_length=19,
        default='-MMMMMMMMMMMMMMMMM-')
    text_input_20 = django.db.models.CharField(
        max_length=20,
        default='-MMMMMMMMMMMMMMMMMM-')
    text_input_21 = django.db.models.CharField(
        max_length=21,
        default='-MMMMMMMMMMMMMMMMMMM-')
    text_input_22 = django.db.models.CharField(
        max_length=22,
        default='-MMMMMMMMMMMMMMMMMMMM-')
    text_input_23 = django.db.models.CharField(
        max_length=23,
        default='-MMMMMMMMMMMMMMMMMMMMM-')
    text_input_24 = django.db.models.CharField(
        max_length=24,
        default='-MMMMMMMMMMMMMMMMMMMMMM-')
    text_input_25 = django.db.models.CharField(
        max_length=25,
        default='-MMMMMMMMMMMMMMMMMMMMMMM-')
    text_input_26 = django.db.models.CharField(
        max_length=26,
        default='-MMMMMMMMMMMMMMMMMMMMMMMM-')
    text_input_27 = django.db.models.CharField(
        max_length=27,
        default='-MMMMMMMMMMMMMMMMMMMMMMMMM-')
    text_input_28 = django.db.models.CharField(
        max_length=28,
        default='-MMMMMMMMMMMMMMMMMMMMMMMMMM-')
    text_input_29 = django.db.models.CharField(
        max_length=29,
        default='-MMMMMMMMMMMMMMMMMMMMMMMMMMM-')
    text_input_30 = django.db.models.CharField(
        max_length=30,
        default='-MMMMMMMMMMMMMMMMMMMMMMMMMMMM-')


class TestModelForm(RightSizeInputModelForm):
    class Meta:
        model = TestModel
        fields = '__all__'
