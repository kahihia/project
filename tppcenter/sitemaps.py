from django.contrib.sitemaps import Sitemap, FlatPageSitemap
from django.core.urlresolvers import reverse
from appl.models import News, Product
from appl.func import getItemsList


class TppSiteMap(Sitemap):
    priority = None
    changefreq = None

    def __init__(self, info_dict):
        self.queryset = info_dict['model'].filter(item2value__attr__title="SLUG", item2value__title__isnull=False)
        self.date_field = 'create_date'
        self.priority = info_dict['priority']
        self.changefreq = 'never'
        self.urls = info_dict['urls']
        self.attrValues = info_dict['attrValues']

    def items(self):
        # Make sure to return a clone; we don't want premature evaluation.
        return self.queryset

    def lastmod(self, item):
        if self.date_field is not None:
            return getattr(item, self.date_field)
        return None

    def location(self, item):
        slug = self.attrValues[item.pk].get('SLUG', '')

        return reverse(self.urls, args=[slug[0]])

all_sitemaps = {}

site_maps = {
    'News': {
        'model': News.active.get_active(),
        'urls': 'news:detail',
        'priority': 0.6,
        'attrValues': getItemsList('News', 'SLUG')
    },
    'Product': {
        'model': Product.active.get_active(),
        'urls': 'products:detail',
        'priority': 0.6,
        'attrValues': getItemsList('Product', 'SLUG')
    },
}

for model_map, dict_map in site_maps.items():

    sitemap = TppSiteMap(dict_map)

    all_sitemaps[model_map] = sitemap


