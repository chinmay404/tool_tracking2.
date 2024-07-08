import csv
from django.http import HttpResponse
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def export_data(request, table_name, app, time=None, start_date=None, end_date=None, filter=None):
    model = apps.get_model(app_label=app, model_name=table_name)
    if not model:
        return HttpResponse("Invalid table name.", status=400)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{table_name}_data.csv"'

    writer = csv.writer(response)
    field_names = [field.name for field in model._meta.fields]
    writer.writerow(field_names)

    queryset = model.objects.all()

    if time:
        if time == 'today':
            queryset = queryset.filter(created_at__date=timezone.now().date())
        elif time == 'this_month':
            queryset = queryset.filter(created_at__month=timezone.now().month, created_at__year=timezone.now().year)
        elif time == 'custom_days':
            if start_date and end_date:
                start_date = timezone.now().date() - timedelta(days=int(start_date))
                end_date = timezone.now().date() - timedelta(days=int(end_date))
                queryset = queryset.filter(created_at__date__range=[start_date, end_date])

    if filter:
        filter_key, filter_value = filter.split('=')
        filter_condition = {filter_key: filter_value}
        queryset = queryset.filter(**filter_condition)

    for instance in queryset:
        writer.writerow([getattr(instance, field) for field in field_names])

    return response

