"""InvenTree plugin to display aggregated 3D print demand."""

from django.http import JsonResponse
from django.urls import re_path

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, UserInterfaceMixin

from part.models import Part, PartCategory
from stock.models import StockItem


class PrintDemandPlugin(SettingsMixin, UrlsMixin, UserInterfaceMixin, InvenTreePlugin):

    AUTHOR = 'Micromelon'
    DESCRIPTION = 'Dashboard panel showing aggregated 3D print demand across open orders'
    VERSION = '0.1.0'
    NAME = 'PrintDemand'
    SLUG = 'print-demand'
    TITLE = '3D Print Demand'

    SETTINGS = {
        'PART_CATEGORY': {
            'name': 'Part Category',
            'description': 'Category containing 3D printed parts',
            'model': 'part.partcategory',
        },
        'INCLUDE_SUBCATEGORIES': {
            'name': 'Include Subcategories',
            'description': 'Include parts from subcategories of the selected category',
            'default': True,
            'validator': bool,
        },
    }

    def setup_urls(self):
        return [
            re_path(r'^api/demand/', self.api_demand, name='api-demand'),
        ]

    def get_ui_panels(self, request, context, **kwargs):
        return []

    def get_ui_dashboard_items(self, request, context, **kwargs):
        return [
            {
                'key': 'print-demand',
                'title': '3D Print Demand',
                'description': 'Aggregated demand for 3D printed parts',
                'source': self.plugin_static_file('print_demand/dashboard.js'),
            },
        ]

    def api_demand(self, request):
        """Return aggregated demand data for all parts in the configured category."""
        category_pk = self.get_setting('PART_CATEGORY')

        if not category_pk:
            return JsonResponse(
                {'error': 'No part category configured. Set PART_CATEGORY in plugin settings.'},
                status=400,
            )

        try:
            category = PartCategory.objects.get(pk=category_pk)
        except PartCategory.DoesNotExist:
            return JsonResponse({'error': 'Configured category does not exist.'}, status=404)

        include_sub = self.get_setting('INCLUDE_SUBCATEGORIES')

        if include_sub:
            categories = category.get_descendants(include_self=True)
        else:
            categories = PartCategory.objects.filter(pk=category.pk)

        parts = Part.objects.filter(category__in=categories, active=True)

        results = []

        for part in parts:
            in_stock = part.total_stock
            allocated_build = part.allocation_count(
                build_order_allocations=True,
                sales_order_allocations=False,
            )
            allocated_sales = part.allocation_count(
                build_order_allocations=False,
                sales_order_allocations=True,
            )
            available = max(0, in_stock - allocated_build - allocated_sales)

            required_build = part.required_build_order_quantity()
            required_sales = part.required_sales_order_quantity()

            total_required = required_build + required_sales
            total_allocated = allocated_build + allocated_sales
            deficit = in_stock - total_required

            results.append({
                'pk': part.pk,
                'name': part.name,
                'IPN': part.IPN or '',
                'in_stock': float(in_stock),
                'allocated_build': float(allocated_build),
                'allocated_sales': float(allocated_sales),
                'available': float(available),
                'required_build': float(required_build),
                'required_sales': float(required_sales),
                'deficit': float(deficit),
            })

        results.sort(key=lambda x: x['deficit'])

        return JsonResponse(results, safe=False)
