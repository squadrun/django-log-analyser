from django.db import models


class DBLogReportDetail(models.Model):
    log_datetime = models.DateTimeField(help_text="Datetime representation of the hour for which logs are stored "
                                                  "in the log file")
    log_file_path = models.CharField(max_length=1024, help_text="Relative path of the stored log file in S3 bucket")
    log_report_path = models.CharField(max_length=1024, null=True, blank=True,
                                       help_text="Relative path of the stored report in S3 bucket")
    db_instance = models.CharField(max_length=64, null=True, blank=True,
                                   help_text="Name of the DB Instance to which the logs belong")
