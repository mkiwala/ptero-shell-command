from .base import BaseAPITest
import os


class TestCwd(BaseAPITest):
    def test_job_working_directory(self):
        webhook_target = self.create_webhook_server([200])

        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'webhooks': {
                'ended': webhook_target.url,
            },
        }

        self.post(self.jobs_url, post_data)

        webhook_data = webhook_target.stop()
        actual_working_directory = webhook_data[0]['stdout'].strip('\n')
        self.assertEqual(self.job_working_directory, actual_working_directory)

    def test_job_working_directory_does_not_exist(self):
        webhook_target = self.create_webhook_server([200])

        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': '/does/not/exist',
            'webhooks': {
                'error': webhook_target.url,
            },
        }

        post_response = self.post(self.jobs_url, post_data)
        webhook_data = webhook_target.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'chdir(/does/not/exist): No such file or directory'
            },
        ]
        self.assertEqual(webhook_data, expected_data)

    def test_job_working_directory_access_denied(self):
        webhook_target = self.create_webhook_server([200])

        os.chmod(self.job_working_directory, 0)
        post_data = {
            'commandLine': ['/bin/pwd'],
            'user': self.job_user,
            'workingDirectory': self.job_working_directory,
            'webhooks': {
                'error': webhook_target.url,
            },
        }

        post_response = self.post(self.jobs_url, post_data)
        webhook_data = webhook_target.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'chdir(%s): Permission denied' % self.job_working_directory
            },
        ]
        self.assertEqual(webhook_data, expected_data)
