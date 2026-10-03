import json
import os
from pathlib import Path
import tempfile

from django.test import TestCase


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
