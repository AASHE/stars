from django.forms import Widget
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from stars.apps.credits.models import (CreditSet,
                                       Category,
                                       Subcategory,
                                       Credit,
                                       DocumentationField)


class SelectTreeWidget(Widget):
    template_name = "credits/widgets/select_tree.html"

    def __init__(self, attrs=None, template_name=None):
        super(SelectTreeWidget, self).__init__(attrs)
        if template_name:
            self.template_name = template_name
        if attrs and 'ordinal' in attrs:
            self.ordinal = attrs['ordinal']
        else:
            self.ordinal = ''

    def render(self, name, value, attrs=None):
        if value is not None:
            init_val = self.get_select_tree_array(value)
        else:
            init_val = []
        final_attrs = self.build_attrs(attrs,
                                       name=name)
        select_list = self.get_select_list(final_attrs)
        template = get_template(self.template_name)
        context = {
            'value': init_val,
            'name': name,
            'select_list': select_list,
            'attrs': final_attrs
        }
        result = mark_safe(template.render(context))
        return result

    def ordinal_id(self, id):
        if self.ordinal:
            return '-'.join([id, str(self.ordinal)])
        else:
            return id


class CategorySelectTree(SelectTreeWidget):

    def get_select_tree_array(self, value):
        cat = Category.objects.get(pk=value)
        cs = cat.creditset
        return [cs.id, cat.id]

    def get_select_list(self, attrs):
        return [
            {
                "label": "Creditset",
                "data_callback": "populateCreditsets",
                "data_child": attrs["id"],
                "data_child_callback": "populateCategories",
                "name": "creditset",
                "id": self.ordinal_id("creditset"),
            },
            {
                "label": "Category",
                "name": attrs["name"],
                "id": attrs["id"]
            }
        ]


class SubcategorySelectTree(CategorySelectTree):

    def get_select_tree_array(self, value):
        sub = Subcategory.objects.get(pk=value)
        cat = sub.category
        cs = cat.creditset
        return [cs.id, cat.id, sub.id]

    def get_select_list(self, attrs):

        select_list = super(SubcategorySelectTree, self).get_select_list(attrs)
        return self.update_select_list(old_list=select_list,
                                       attrs=attrs,
                                       label="subcategory",
                                       parent_id=self.ordinal_id("category"),
                                       callback="populateSubcategories")

    def update_select_list(self, old_list, attrs, label, parent_id, callback):
        select_list = old_list
        # set the previous parent-child relationship
        select_list[-2]["data_child"] = parent_id

        # update the leaf (old parent) to use the newest label
        select_list[-1]["label"] = label

        # now add the parent back
        parent_select = {
            "data_child": attrs['id'],
            "data_child_callback": callback,
        }
        parent_select['label'] = parent_select['name'] = parent_select['id'] = parent_id
        select_list.insert(-1, parent_select)
        return select_list


class CreditSelectTree(SubcategorySelectTree):

    def get_select_tree_array(self, value):
        crd = Credit.objects.get(pk=value)
        sub = crd.subcategory
        cat = sub.category
        cs = cat.creditset
        return [cs.id, cat.id, sub.id, crd.id]

    def get_select_list(self, attrs):

        select_list = super(CreditSelectTree, self).get_select_list(attrs)
        return self.update_select_list(old_list=select_list,
                                       attrs=attrs,
                                       label="credit",
                                       parent_id=self.ordinal_id(
                                           "subcategory"),
                                       callback="populateCredits")


class DocumentationFieldSelectTree(CreditSelectTree):

    def get_select_tree_array(self, value):
        df = DocumentationField.objects.get(pk=value)
        cred = df.credit
        sub = cred.subcategory
        cat = sub.category
        cs = cat.creditset
        return [cs.id, cat.id, sub.id, cred.id, df.id]

    def get_select_list(self, attrs):

        select_list = super(DocumentationFieldSelectTree,
                            self).get_select_list(attrs)
        return self.update_select_list(old_list=select_list,
                                       attrs=attrs,
                                       label="field",
                                       parent_id=self.ordinal_id("credit"),
                                       callback="populateFields")

# class DocumentationFieldSelectTree(Widget):
#
#     def get_select_list(self, attrs):
#         return [
#                 {
#                  "label": "Creditset",
#                  "data_callback": "populateCreditsets",
#                  "data_child": "category",
#                  "data_child_callback": "populateCategories",
#                  "name": "creditset",
#                  "id": "creditset",
#                 },
#                 {
#                  "label": "Category",
#                  "data_child": "subcategory",
#                  "data_child_callback": "populateSubcategories",
#                  "name": "category",
#                  "id": "category",
#                 },
#                 {
#                  "label": "Subcategory",
#                  "data_child": "credit",
#                  "data_child_callback": "populateCredits",
#                  "name": "subcategory",
#                  "id": "subcategory",
#                 },
#                 {
#                  "label": "Credit",
#                  "data_child": attrs["id"],
#                  "data_child_callback": "populateFields",
#                  "name": "credit",
#                  "id": "credit",
#                 },
#                 {
#                  "label": "Field",
#                  "id": attrs["id"],
#                  "name": attrs["name"]
#                  }
#                 ]
#
#     def get_select_tree_array(self, value):
#         if value is None:
#             return None
#         else:
#             df = DocumentationField.objects.get(pk=value)
#             cred = df.credit
#             sub = cred.subcategory
#             cat = sub.category
#             cs = cat.creditset
#             return [
#                     cs.id,
#                     cat.id,
#                     sub.id,
#                     cred.id,
#                     df.id
#                     ]
