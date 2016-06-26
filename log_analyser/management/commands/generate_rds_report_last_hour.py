from django.core.management import BaseCommand

from log_analyser.utils import fetch_log_from_rds, upload_log_to_s3, upload_report_to_s3, \
    create_pgbadger_report_from_log


class Command(BaseCommand):
    def handle(self, *args, **options):
        rds_log_file_tmp_path = fetch_log_from_rds()
        self.stdout.write('Log from RDS stored at {0}'.format(rds_log_file_tmp_path))

        log_file_report_obj = upload_log_to_s3(rds_log_file_tmp_path)
        self.stdout.write('Log file for object ID: {0} uploaded to S3'.format(log_file_report_obj.id))

        report_path = create_pgbadger_report_from_log(rds_log_file_tmp_path)
        self.stdout.write('Report stored at {0}'.format(report_path))

        upload_report_to_s3(report_path)
        self.stdout.write('Report for log uploaded to S3')
