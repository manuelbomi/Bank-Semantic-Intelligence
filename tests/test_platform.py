"""Fast offline regression tests requiring only Python standard library."""
import tempfile
import unittest
from pathlib import Path
from bank_semantic.synthetic import generate
from bank_semantic.ingest import rows, reviews
from bank_semantic.extract import extract_all, validate
from bank_semantic.graph import build
from bank_semantic.identity import exact_email_links
from bank_semantic.assistant import answer
from bank_semantic.evaluate import retrieval_eval


class PlatformTests(unittest.TestCase):
    """Each test documents an important functional or governance invariant."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        generate(n=30, folder=self.folder)

    def tearDown(self):
        self.tmp.cleanup()

    def test_deterministic_fixture_counts(self):
        self.assertEqual(len(rows(self.folder, "accounts")), 60)
        self.assertEqual(len(rows(self.folder, "transactions")), 240)

    def test_graph_edges_have_endpoints(self):
        graph = build(self.folder, extract_all(reviews(self.folder)))
        ids = {node["id"] for node in graph["nodes"]}
        self.assertTrue(all(e["source"] in ids and e["target"] in ids
                            for e in graph["edges"]))

    def test_llm_hallucination_rejected(self):
        review = reviews(self.folder)[0]
        with self.assertRaises(ValueError):
            validate(review, [{"relation": "MORTGAGE_INTEREST",
                               "evidence": "Text that does not exist"}])

    def test_unconsented_reviews_excluded(self):
        facts = extract_all(reviews(self.folder))
        self.assertTrue(all(f["consent_for_analytics"] for f in facts))

    def test_hr_isolation(self):
        with self.assertRaises(PermissionError):
            answer("HR headcount", "analyst", self.folder)
        self.assertIn("Training completion", answer("HR training", "hr", self.folder)["answer"])

    def test_customer_requires_identity(self):
        with self.assertRaises(PermissionError):
            answer("my accounts", "customer", self.folder)
        response = answer("my accounts", "customer", self.folder, actor_customer_id=3)
        self.assertEqual(len(response["account_ids"]), 2)

    def test_email_linkage_is_not_name_only(self):
        matches = exact_email_links(self.folder)
        self.assertTrue(all(m["decision"] == "candidate_exact_email" for m in matches))
        self.assertLess(len(matches), 30)  # Some CRM profiles omit emails.

    def test_policy_retrieval(self):
        response = answer("How do I reset my mobile password?", "customer", self.folder, 1)
        self.assertIn("faq-password", response["citations"])

    def test_metric_retrieval(self):
        self.assertIn("Active customers", answer("customer KPI", "executive", self.folder)["answer"])

    def test_retrieval_quality(self):
        result = retrieval_eval()
        self.assertGreaterEqual(result["recall_at_3"], 2 / 3)


if __name__ == "__main__":
    unittest.main()
