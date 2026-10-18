import contextlib
import copy
import importlib.util
import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'shared/repo-safe-data-audit/local_llm_review.py'
FIXTURE = ROOT / 'tests/fixtures/repo-safe-data-audit-metadata.json'
SPEC = importlib.util.spec_from_file_location('local_llm_review', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LocalLlmReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='repo-safe-metadata-')
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name)
        self.output = self.private / 'suggestions.json'
        self.transport = mock.patch.object(MODULE, '_post_json', side_effect=self.fake_post)
        self.post = self.transport.start()
        self.addCleanup(self.transport.stop)

    def fake_post(self, request):
        self.sent = json.loads(request.data)
        records = json.loads(self.sent['messages'][1]['content'])
        result = {'classifications': [
            {'id': item['id'], 'category': 'ambiguous', 'confidence': 'low',
             'rationale': 'synthetic example requires content review'} for item in records
        ]}
        return self.envelope(result)

    @staticmethod
    def envelope(result, reason='stop'):
        return json.dumps({'choices': [{'finish_reason': reason,
            'message': {'content': json.dumps(result)}}]}).encode()

    def run_main(self, *args, **extra_env):
        env = {'REPO_AUDIT_LLM_MODEL': 'synthetic-test-model',
               'REPO_AUDIT_LLM_BASE_URL': 'http://127.0.0.1:1235/v1'}
        env.update(extra_env)
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
             mock.patch('sys.argv', [str(SCRIPT), *map(str, args)]), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = MODULE.main()
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()

    def infer(self, input_path=FIXTURE, output=None, **env):
        return self.run_main('--input', input_path, '--output', output or self.output,
            '--confirm-local-runtime', '--confirm-reviewed-metadata', **env)

    def test_dry_run_makes_no_request_and_no_output(self):
        code, stdout, _ = self.run_main('--input', FIXTURE, '--dry-run')
        self.assertEqual(code, 0)
        self.assertFalse(json.loads(stdout)['request_sent'])
        self.post.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_inference_requires_both_attestations(self):
        for flags in ([], ['--confirm-local-runtime'], ['--confirm-reviewed-metadata']):
            with self.subTest(flags=flags):
                code, _, _ = self.run_main('--input', FIXTURE, '--output', self.output, *flags)
                self.assertNotEqual(code, 0)
        self.post.assert_not_called()

    def test_rejects_unsafe_endpoints_before_request(self):
        for url in ['https://example.invalid/v1', 'http://localhost:1235/v1',
                    'http://127.0.0.1:1235@evil.invalid/v1',
                    'http://127.0.0.1:1235/v1?token=hidden',
                    'http://127.0.0.1:1235/v1#hidden', 'http://127.0.0.1:0/v1']:
            with self.subTest(url=url):
                code, _, _ = self.infer(REPO_AUDIT_LLM_BASE_URL=url)
                self.assertNotEqual(code, 0)
        self.post.assert_not_called()

    def test_rejects_content_nested_fields_and_duplicate_ids(self):
        base = json.loads(FIXTURE.read_text())
        variants = []
        for field, value in [('content', 'hidden'), ('path', {'secret': 'hidden'}),
                             ('size_bytes', True), ('git_tracked', 'yes')]:
            rows = copy.deepcopy(base)
            rows[0][field] = value
            variants.append(rows)
        variants.append([base[0], base[0]])
        for rows in variants:
            p = self.private / 'input.json'
            p.write_text(json.dumps(rows))
            code, stdout, stderr = self.infer(p)
            self.assertNotEqual(code, 0)
            self.assertNotIn('hidden', stdout + stderr)
        self.post.assert_not_called()

    def test_private_output_schema_and_no_model_text_on_stdout(self):
        code, stdout, stderr = self.infer()
        self.assertEqual(code, 0, stderr)
        self.assertNotIn('synthetic example', stdout)
        self.assertTrue(json.loads(self.output.read_text())['advisory_only'])
        records = json.loads(self.sent['messages'][1]['content'])
        self.assertEqual(set(records[0]), {'id', 'path', 'extension', 'size_bytes', 'git_tracked'})
        self.assertEqual(self.sent['response_format']['type'], 'json_schema')
        self.assertNotIn('tools', self.sent)

    def test_existing_output_is_never_overwritten_or_sent(self):
        self.output.write_text('KEEP')
        code, _, _ = self.infer()
        self.assertNotEqual(code, 0)
        self.assertEqual(self.output.read_text(), 'KEEP')
        self.post.assert_not_called()

    def test_refuses_output_inside_git_worktree_file(self):
        (self.private / '.git').write_text('gitdir: unrelated')
        code, _, _ = self.infer()
        self.assertNotEqual(code, 0)
        self.post.assert_not_called()

    def test_invalid_model_labels_unknown_duplicate_ids_and_truncation_fail_closed(self):
        item = {'id': '1', 'category': 'tooling', 'confidence': 'low', 'rationale': 'example'}
        other = dict(item, id='2')
        for result, reason in [
            ({'classifications': [item, item]}, 'stop'),
            ({'classifications': [item, dict(other, id='unexpected')]}, 'stop'),
            ({'classifications': [item, dict(other, category='publish')]}, 'stop'),
            ({'classifications': [item, dict(other, confidence='high')]}, 'stop'),
            ({'classifications': [item, dict(other, secret='hidden')]}, 'stop'),
            ({'classifications': [item, other]}, 'length'),
        ]:
            self.post.side_effect = None
            self.post.return_value = self.envelope(result, reason)
            code, stdout, stderr = self.infer()
            self.assertNotEqual(code, 0)
            self.assertFalse(self.output.exists())
            self.assertNotIn('hidden', stdout + stderr)

    def test_malformed_api_envelopes_fail_without_writing(self):
        self.post.side_effect = None
        for response in ([], {}, {'choices': []}, {'choices': [None]},
                         {'choices': [{'finish_reason': 'stop', 'message': {'content': []}}]}):
            self.post.return_value = json.dumps(response).encode()
            code, _, _ = self.infer()
            self.assertNotEqual(code, 0)
            self.assertFalse(self.output.exists())

    def test_proxy_disabled_and_redirects_refused(self):
        with mock.patch.object(MODULE.urllib.request, 'build_opener') as build:
            build.return_value.open.return_value.__enter__.return_value.read.return_value = b'{}'
            # Exercise real transport rather than the per-test mock.
            self.transport.stop()
            MODULE._post_json(MODULE.urllib.request.Request('http://127.0.0.1:1235/v1'))
            proxy, redirect = build.call_args.args
            self.assertEqual(proxy.proxies, {})
            with self.assertRaises(urllib.error.URLError):
                redirect.redirect_request(None, None, 302, '', {}, 'https://example.invalid')


if __name__ == '__main__':
    unittest.main()
