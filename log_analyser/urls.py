from django.conf.urls import url

from .views import get_report


urlpatterns = [
    url(r'^get-report/(?P<log_report_obj_id>\d+)', get_report, name='get-report'),
]
