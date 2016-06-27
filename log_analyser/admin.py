from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import DBLogReportDetail


class LogFileAndReportDetailAdmin(admin.ModelAdmin):
    list_display = ('log_datetime', 'log_report_path', 'db_instance', 'report_link')
    readonly_fields = ('log_datetime', 'log_file_path', 'db_instance', 'log_report_path')

    def report_link(self, obj):
        url = reverse('get-report', kwargs={'log_report_obj_id': obj.id})
        return mark_safe("<a href='{0}'>Report Link</a>".format(url))


admin.site.register(DBLogReportDetail, LogFileAndReportDetailAdmin)
