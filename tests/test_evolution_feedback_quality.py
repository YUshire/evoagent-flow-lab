import os
import tempfile
import unittest

from evoagent.evolution import EvolutionEngine
from evoagent.evolution_v2 import RootCauseEvolutionGenerator
from evoagent.store import TaskStore


class EvolutionFeedbackQualityTests(unittest.TestCase):
    def test_retry_duplicates_and_accepted_reviews_are_not_failure_signals(self):
        with tempfile.TemporaryDirectory() as root:
            store = TaskStore(os.path.join(root, 'test.db'))
            store.create('task', 'org/repo', 1, {})
            for _ in range(3):
                store.record_failure_case('task', 'execution_error', {'finding': None})
            store.record_failure_case('task', 'accepted', {'finding': {'rule_id': 'SEC-EVAL'}})
            store.record_failure_case('task', 'false_positive', {'finding': {'rule_id': 'SEC-EVAL'}})
            class Generator:
                def generate(self, cases, base):
                    self.cases = cases
                    return {'candidate_prompt': base}
            generator = Generator()
            result = EvolutionEngine(store, candidate_generator=generator).auto_propose()
            self.assertEqual('deferred', result['decision'])
            self.assertEqual(2, result['failure_cases_used'])
            self.assertEqual({'execution_error', 'false_positive'}, {c['category'] for c in generator.cases})

    def test_few_shot_example_is_used_by_the_evaluated_prompt(self):
        class Client:
            provider = 'fake-test'
            model = 'fixture'
            def complete_json(self, *args):
                return {'candidate': {'few_shot_examples': [{'input':'SAFE_DIFF', 'output':'{"findings":[]}'}]}}
        generated = RootCauseEvolutionGenerator(Client()).generate([], 'Return JSON severity fix test.')
        self.assertIn('SAFE_DIFF', generated['candidate_prompt'])
        self.assertIn('SAFE_DIFF', generated['change_diff'])

    def test_invalid_examples_do_not_enter_a_candidate_prompt(self):
        class Client:
            provider = 'fake-test'
            model = 'fixture'
            def complete_json(self, *args):
                return {'candidate': {'few_shot_examples': [{'input':False, 'output':7}]}}
        with self.assertRaisesRegex(ValueError, 'few_shot_examples'):
            RootCauseEvolutionGenerator(Client()).generate([], 'base')
