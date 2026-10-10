import os
import tempfile
import unittest
from evoagent.evolution import EvolutionEngine
from evoagent.evolution_proof import run_prompt_evolution_proof
from evoagent.store import TaskStore


class AuthoredActivationTests(unittest.TestCase):
    def test_confirmed_misses_activate_only_after_validation_and_holdout_then_rollback(self):
        dataset = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evaluation_data', 'authored_activation_12.jsonl')
        with tempfile.TemporaryDirectory() as root:
            database = os.path.join(root, 'proof.db')
            report = run_prompt_evolution_proof(dataset, database)
            self.assertEqual('activated', report['evolution_run']['decision'])
            self.assertGreater(report['validation']['delta']['f1'], 0)
            self.assertGreater(report['holdout']['delta']['f1'], 0)
            self.assertEqual('controlled-offline-behavioral-evolution', report['claim_scope']['level'])
            self.assertEqual(['new-authored-controlled'], report['dataset']['source_kinds'])
            store = TaskStore(database)
            original = min(store.list_skill_versions('llm-review'), key=lambda item: item['version'])
            self.assertTrue(EvolutionEngine(store, seed_defaults=False).rollback('llm-review', original['version']))
            self.assertEqual(original['version'], store.get_active_skill_version('llm-review')['version'])
