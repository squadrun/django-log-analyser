from datetime import timedelta, datetime
from django.conf import settings
from django.core.management import BaseCommand

from log_analyser.models import DBLogReportDetail
from log_analyser.utils import fetch_log_from_rds, upload_log_to_s3, upload_report_to_s3, \
    create_pgbadger_report_from_log, delete_unneeded_files


class Command(BaseCommand):
    help = "Management command to Generate Report for RDS Postgres Logs"

    def add_arguments(self, parser):
        parser.add_argument('--tmp_log_location', action="store", type=str, required=False)

    def handle(self, *args, **options):
        db_instances = settings.RDS_DB_INSTANCE_IDENTIFIER
        log_file_tmp_path = options.get('tmp_log_location') or settings.RDS_TEMP_LOG_FILE_LOCATION

        if type(db_instances) is not list:
            db_instances = [db_instances]

        last_log_report_obj = DBLogReportDetail.objects.order_by('-log_datetime').first()
        log_datetime = last_log_report_obj.log_datetime + timedelta(hours=1) if last_log_report_obj is not None \
            else datetime.utcnow() - timedelta(hours=1)

        for db_instance in db_instances:
            rds_log_file_tmp_path = fetch_log_from_rds(log_datetime, db_instance, log_file_tmp_path)
            if rds_log_file_tmp_path is not None:
                self.stdout.write('Log from RDS stored at {0}'.format(rds_log_file_tmp_path))

                log_file_report_obj, compressed_log_file_path = upload_log_to_s3(rds_log_file_tmp_path, db_instance)
                self.stdout.write('Log file for object ID: {0} uploaded to S3'.format(log_file_report_obj.id))

                report_path = create_pgbadger_report_from_log(rds_log_file_tmp_path)
                self.stdout.write('Report stored at {0}'.format(report_path))

                upload_report_to_s3(report_path, db_instance)
                self.stdout.write('Report for log uploaded to S3')

                files_to_delete = [rds_log_file_tmp_path, report_path, compressed_log_file_path]
                delete_unneeded_files(files_to_delete)
