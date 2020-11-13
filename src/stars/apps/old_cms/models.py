import time
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from stars.apps.helpers.utils import invalidate_template_cache


class AbstractContent(models.Model):
    ordinal = models.SmallIntegerField(default=0)
    published = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('ordinal', 'title')

    def __str__(self):
        return self.title

    def get_django_admin_url(self):
        return "/_ad/%s/%s/%d" % (
            self._meta.app_label,
            self.model_name,
            self.id,
        )


class CategoryMixin(models.Model):

    title = models.CharField(max_length=64)
    slug = models.SlugField(
        help_text='This is a URL-friendly version of the title. Do not change unless you want to change the link')
    content = models.TextField(
        blank=True, null=True, help_text='If left blank, the page will be populated with the teaser text from all the articles.')

    class Meta:
        abstract = True

    def get_articles(self):
        return self.newarticle_set.filter(published=True).order_by('ordinal')


class Category(CategoryMixin, AbstractContent):
    """
        Django-hosted CMS top-level category
    """

    class Meta:
        verbose_name_plural = "Categories"

    def get_absolute_url(self):
        return "/pages/%s/" % self.slug

    def get_published_subcategories(self):
        return self.subcategory_set.filter(published=True).order_by('ordinal')


class Subcategory(CategoryMixin, AbstractContent):
    parent = models.ForeignKey(Category)

    class Meta:
        verbose_name_plural = "Subcategories"

    def get_absolute_url(self):
        return "%s%s/" % (self.parent.get_absolute_url(), self.slug)

    def save(self, *args, **kwargs):
        super(Subcategory, self).save(*args, **kwargs)
        self.parent.save()  # Update timestamp for caching

    def update_timestamps(self):
        """
            All categories get new timestamps because I can't tell
            which category this article used to belong to.
            Of course, I could if I wrote a custom form for the admin,
            but that's not the only place these could be saved
        """
        for cat in Category.objects.all():
            cat.save()

    def get_published_articles(self):
        return self.newarticle_set.filter(published=True).order_by('ordinal')


class NewArticle(AbstractContent):
    """
        Django-hosted CMS article
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField()
    teaser = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    # subcategories = models.ManyToManyField(Subcategory, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    irc_id = models.IntegerField(
        blank=True, null=True, help_text='Only necessary for pages that used to exist in the IRC. New pages will not need this.')

    class Meta:
        ordering = ('ordinal', 'title', 'timestamp',)
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def get_absolute_url(self):
        if self.categories.count() > 0:
            return "%s%s.html" % (self.categories.all()[0].get_absolute_url(), self.slug)
        return "#"

    def update_timestamps(self):
        """
            All categories and subcategories get new timestamps
            because I can't tell which category this article
            used to belong to.
            Of course, I could if I wrote a custom form for the admin,
            but that's not the only place these could be saved
        """
        # for sub in Subcategory.objects.all():
        #     sub.save()
        for cat in Category.objects.all():
            cat.save()


class HomepageUpdate(AbstractContent):
    """
        Update that appears on homepage feed.
    """
    title = models.CharField(max_length=255)
    link = models.URLField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('ordinal', 'title', 'timestamp',)
        verbose_name = "Homepage Update"
        verbose_name_plural = "Homepage Updates"
