import gzip
import logging
import shutil
import re
import subprocess
from datetime import datetime

from boto3.session import Session
from botocore.exceptions import ClientError

from django.conf import settings
from django.utils.timezone import utc

from .constants import PREFIX_DIRECTORY_LOGS, PREFIX_DIRECTORY_REPORTS
from .models import DBLogReportDetail


logger = logging.getLogger(__name__)

aws_session = Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)
rds_client = aws_session.client('rds')
s3_resource = aws_session.resource('s3')

pattern_log_hour = re.compile('postgresql\.log\.([0-9-]+)')


def fetch_log_from_rds(log_datetime, db_instance, temp_log_file_location):
    rds_log_file_name = get_rds_log_file_name(log_datetime)
    rds_log_file_tmp_path = "{0}/{1}_{2}".format(temp_log_file_location, rds_log_file_name, db_instance)

    try:
        with open(rds_log_file_tmp_path, 'wb', buffering=50 * 1024) as postgres_log_file:
            additional_data_pending, marker = True, "0"
            while additional_data_pending:
                response = rds_client.download_db_log_file_portion(
                    DBInstanceIdentifier=db_instance,
                    LogFileName='error/'+rds_log_file_name,
                    Marker=marker
                )

                postgres_log_file.write(response.get('LogFileData'))

                additional_data_pending = response.get('AdditionalDataPending')
                marker = response.get('Marker')
    except ClientError as e:
        logger.info(e.message)
        return None
    else:
        return rds_log_file_tmp_path


def upload_log_to_s3(log_file_path, db_instance):
    compressed_log_file_path = log_file_path + '.gz'
    log_file_name = log_file_path.split('/')[-1]
    compressed_log_file_name = log_file_name + '.gz'

    log_hour_datetime = datetime.strptime(pattern_log_hour.findall(log_file_name)[0], '%Y-%m-%d-%H').replace(tzinfo=utc)
    s3_directory_string_log = get_s3_directory(log_hour_datetime)

    with open(log_file_path) as log_file, gzip.open(compressed_log_file_path, 'wb') as compressed_log_file:
        shutil.copyfileobj(log_file, compressed_log_file)

    logger.info("{0} Compressed".format(log_file_name))

    with open(compressed_log_file_path) as compressed_log_file:
        try:
            s3_resource.Object(settings.BUCKET_LOG_ANALYSER, s3_directory_string_log + compressed_log_file_name)\
                .put(Body=compressed_log_file)
        except ClientError as e:
            raise Exception(e.message)
        else:
            log_file_report_obj = DBLogReportDetail.objects\
                .create(log_datetime=log_hour_datetime,
                        log_file_path=s3_directory_string_log + compressed_log_file_name,
                        db_instance=db_instance)
            return log_file_report_obj, compressed_log_file_path


def upload_report_to_s3(report_file_path, db_instance):
    report_file_name = report_file_path.split('/')[-1]
    log_hour_datetime = datetime.strptime(pattern_log_hour.findall(report_file_name)[0], '%Y-%m-%d-%H')\
        .replace(tzinfo=utc, minute=0, second=0, microsecond=0)
    s3_directory_string_report = get_s3_directory(log_hour_datetime, prefix=PREFIX_DIRECTORY_REPORTS)
    with open(report_file_path, 'rb') as report_file:
        try:
            s3_resource.Object(settings.BUCKET_LOG_ANALYSER, s3_directory_string_report + report_file_name)\
                .put(Body=report_file)
        except ClientError as e:
            raise Exception(e.message)
        else:
            log_report_obj = DBLogReportDetail.objects\
                .filter(log_datetime=log_hour_datetime, db_instance=db_instance).first()
            log_report_obj.log_report_path = s3_directory_string_report + report_file_name
            log_report_obj.save()

            return log_report_obj


def get_s3_directory(datetime_obj, prefix=PREFIX_DIRECTORY_LOGS):
    return "{0}/{1}/".format(prefix, datetime_obj.strftime('%Y-%m-%d'))


def get_rds_log_file_name(datetime_obj=None):
    if datetime_obj is None:
        datetime_obj = datetime.utcnow()
    return "postgresql.log.{0}".format(datetime_obj.strftime('%Y-%m-%d-%H'))


def get_temporary_report_url(report_path):
    try:
        s3 = aws_session.client('s3')
        return s3.generate_presigned_url('get_object',
                                         Params={'Bucket': settings.BUCKET_LOG_ANALYSER, 'Key': report_path},
                                         ExpiresIn=600)
    except AttributeError:
        return None


def create_pgbadger_report_from_log(log_file_path):
    report_path = log_file_path + '.html'
    cmd = "pgbadger -p '%t:%r:%u@%d:[%p]:' -o {0} {1}".format(report_path, log_file_path)

    # TODO: Handle exceptions
    # TODO: Do not use shell=True
    subprocess.call(cmd, shell=True)
    return report_path


def delete_unneeded_files(file_paths):
    subprocess.call(['rm'] + file_paths)
