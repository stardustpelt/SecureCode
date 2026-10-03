import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from code_analyzer.views import check_low_severity_issues, check_security_vulnerabilities


class AnalyzeReportPathTests(TestCase):
	def setUp(self):
		self.original_cwd = os.getcwd()
		self.temp_dir = tempfile.TemporaryDirectory()
		self.base_dir = Path(self.temp_dir.name) / 'base'
		self.work_dir = self.base_dir / 'work'
		(self.base_dir / 'tmp').mkdir(parents=True)
		self.work_dir.mkdir()
		os.chdir(self.work_dir)

	def tearDown(self):
		os.chdir(self.original_cwd)
		self.temp_dir.cleanup()

	def test_user_filename_cannot_escape_reports_directory(self):
		cases = [
			('../../tmp/x', 'x'),
			(r'..\x', 'x'),
			('a/b', 'b'),
			('', 'api_code'),
			('n' * 80, 'n' * 64),
			('bad\x00name', 'badname'),
		]

		for supplied_name, expected_name in cases:
			with self.subTest(filename=supplied_name):
				response = self.client.post(
					'/api/analyze/',
					data=json.dumps({'code': 'value = 1\n', 'filename': supplied_name}),
					content_type='application/json',
				)
				self.assertEqual(response.status_code, 200)
				result = response.json()
				self.assertEqual(result['filename'], expected_name)
				self.assertRegex(result['report_id'], r'^[0-9a-f]{32}$')
				self.assertTrue((self.work_dir / 'reports' / f"{result['report_id']}.pdf").is_file())

		self.assertFalse((self.base_dir / 'tmp' / 'x.pdf').exists())

	def test_uuid_report_id_downloads_pdf_and_non_uuid_is_not_found(self):
		response = self.client.post(
			'/api/analyze/',
			data=json.dumps({'code': 'value = 1\n', 'filename': 'display-name'}),
			content_type='application/json',
		)
		report_id = response.json()['report_id']

		download = self.client.get(f'/api/report/{report_id}/?download=true')
		self.assertEqual(download.status_code, 200)
		self.assertEqual(download['Content-Type'], 'application/pdf')
		self.assertEqual(self.client.get('/api/report/not-a-uuid/').status_code, 404)

	def test_same_display_name_creates_distinct_reports(self):
		report_ids = []
		for code in ('eval(user_input)\n', 'exec(user_input)\n'):
			response = self.client.post(
				'/api/analyze/',
				data=json.dumps({'code': code, 'filename': 'same-name'}),
				content_type='application/json',
			)
			self.assertEqual(response.status_code, 200)
			report_ids.append(response.json()['report_id'])

		self.assertNotEqual(report_ids[0], report_ids[1])
		first_report = (self.work_dir / 'reports' / f'{report_ids[0]}.pdf').read_bytes()
		second_report = (self.work_dir / 'reports' / f'{report_ids[1]}.pdf').read_bytes()
		self.assertNotEqual(first_report, second_report)

	def test_cors_and_hosts_are_restricted(self):
		self.assertNotIn('*', settings.ALLOWED_HOSTS)
		self.assertFalse(settings.CORS_ALLOW_ALL_ORIGINS)
		self.assertFalse(settings.CORS_ALLOW_CREDENTIALS)
		self.assertFalse(any('*' in origin for origin in settings.CORS_ALLOWED_ORIGINS))
		self.assertFalse(any('*' in origin for origin in settings.CSRF_TRUSTED_ORIGINS))

	def test_production_settings_require_a_secret_key(self):
		environment = os.environ.copy()
		environment.pop('DJANGO_SECRET_KEY', None)
		environment['DJANGO_DEBUG'] = '0'
		project_dir = Path(__file__).resolve().parents[1]
		result = subprocess.run(
			[sys.executable, '-c', 'import securecode_web.settings'],
			cwd=project_dir,
			env=environment,
			capture_output=True,
			text=True,
		)
		self.assertNotEqual(result.returncode, 0)
		self.assertIn('DJANGO_SECRET_KEY must be set', result.stderr)

	def test_upload_memory_thresholds_are_512_kb(self):
		self.assertEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 512 * 1024)
		self.assertEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 512 * 1024)

	def test_code_over_character_limit_returns_413(self):
		response = self.client.post(
			'/api/analyze/',
			data=json.dumps({'code': 'x' * 200_001}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 413)

	def test_non_string_code_returns_400(self):
		response = self.client.post(
			'/api/analyze/',
			data=json.dumps({'code': ['not', 'source']}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 400)

	def test_oversized_request_body_returns_413(self):
		body = json.dumps({'code': 'x' * (512 * 1024)})
		response = self.client.post('/api/analyze/', data=body, content_type='application/json')
		self.assertEqual(response.status_code, 413)

	def test_analysis_recursion_memory_and_value_errors_return_400(self):
		for error_type in (RecursionError, MemoryError, ValueError):
			with self.subTest(error=error_type.__name__):
				with patch('code_analyzer.views.check_indentation', side_effect=error_type()):
					response = self.client.post(
						'/api/analyze/',
						data=json.dumps({'code': 'value = 1'}),
						content_type='application/json',
					)
				self.assertEqual(response.status_code, 400)

	def test_old_reports_are_deleted_on_analysis_request(self):
		reports_dir = self.work_dir / 'reports'
		reports_dir.mkdir()
		old_report = reports_dir / 'expired.pdf'
		old_report.write_bytes(b'old report')
		old_timestamp = time.time() - (24 * 60 * 60 + 1)
		os.utime(old_report, (old_timestamp, old_timestamp))

		response = self.client.post(
			'/api/analyze/',
			data=json.dumps({'code': 'value = 1'}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 200)
		self.assertFalse(old_report.exists())

	def test_uploaded_code_over_character_limit_returns_413(self):
		uploaded = SimpleUploadedFile('large.py', b'x' * 200_001)
		response = self.client.post('/api/analyze/', {'file': uploaded})
		self.assertEqual(response.status_code, 413)

	def test_unexpected_errors_are_logged_but_not_returned(self):
		with self.assertLogs('code_analyzer.views', level='ERROR') as logged:
			with patch('code_analyzer.views.check_indentation', side_effect=RuntimeError('private detail')):
				response = self.client.post(
					'/api/analyze/',
					data=json.dumps({'code': 'value = 1'}),
					content_type='application/json',
				)

		self.assertEqual(response.status_code, 500)
		self.assertEqual(response.json(), {'error': 'Internal server error'})
		self.assertIn('private detail', logged.output[0])

	def test_analysis_reports_that_source_was_not_executed(self):
		response = self.client.post(
			'/api/analyze/',
			data=json.dumps({'code': 'value = 1'}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['output'], 'No code was executed.')

	def test_cli_download_route_is_not_exposed(self):
		self.assertEqual(self.client.get('/api/download/cli/').status_code, 404)

	def _scan_security_source(self, source):
		source_path = self.work_dir / 'scanner_case.py'
		source_path.write_text(source)
		return check_security_vulnerabilities(str(source_path)) or []

	def test_scanner_sample_files(self):
		samples_dir = Path(__file__).resolve().parents[2] / 'samples'
		bad_file = samples_dir / 'test_bad.py'
		good_file = samples_dir / 'test_good.py'
		bad_quality = check_low_severity_issues(str(bad_file)) or []
		good_quality = check_low_severity_issues(str(good_file)) or []

		self.assertTrue(any(item['type'] == 'Syntax Error' for item in bad_quality))
		self.assertFalse(any(item['type'] == 'Syntax Error' for item in good_quality))
		self.assertFalse(check_security_vulnerabilities(str(bad_file)))
		self.assertFalse(check_security_vulnerabilities(str(good_file)))

	def test_ast_detection_distinguishes_builtin_calls_and_import_aliases(self):
		findings = self._scan_security_source(
			'import re\n'
			'import builtins as bi\n'
			'from builtins import eval as evaluate\n'
			'import os as operating_system\n'
			'from os import system as launch\n'
			'import subprocess as proc\n'
			'from subprocess import run as run_command\n'
			'pattern = re.compile("[a-z]+")\n'
			'eval(user_input)\n'
			'object.eval(user_input)\n'
			'compile(user_input, "<string>", "exec")\n'
			'evaluate(user_input)\n'
			'bi.exec(user_input)\n'
			'operating_system.system(command)\n'
			'launch(command)\n'
			'proc.run(command, shell=True)\n'
			'proc.run(command, shell=False)\n'
			'run_command(command, shell=True)\n'
		)
		finding_types = [item['type'] for item in findings]

		self.assertEqual(finding_types.count('Code Injection - eval()'), 2)
		self.assertIn('Code Injection - exec()', finding_types)
		self.assertIn('Code Injection - compile()', finding_types)
		self.assertEqual(finding_types.count('Command Injection - os.system()'), 2)
		self.assertEqual(finding_types.count('Command Injection - shell=True'), 2)

	def test_placeholder_and_environment_secrets_are_ignored(self):
		findings = self._scan_security_source(
			'PASSWORD = ""\n'
			'TOKEN = "changeme"\n'
			'API_KEY = "<your-api-key>"\n'
			'SECRET_KEY = os.environ.get("SECRET_KEY")\n'
			'AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")\n'
			'REAL_TOKEN = "token-value-123"\n'
			'REAL_PASSWORD = "password-value-123"\n'
		)
		finding_types = [item['type'] for item in findings]

		self.assertNotIn('Hardcoded Secret Key', finding_types)
		self.assertNotIn('Hardcoded API Key', finding_types)
		self.assertNotIn('AWS Credentials', finding_types)
		self.assertIn('Hardcoded Token', finding_types)
		self.assertIn('Hardcoded Password', finding_types)
