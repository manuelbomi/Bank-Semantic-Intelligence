"""Identity resolution: safe deterministic baseline plus optional Splink 4 lab.

Probabilistic scores are candidates for review, NOT canonical identity proof.
"""
from .ingest import rows


def exact_email_links(folder):
    """Propose links for exact emails, avoiding name-only identity merges."""
    customers = rows(folder, "customers")
    crm = rows(folder, "crm_profiles")
    index = {c["email"].strip().casefold(): c["customer_id"] for c in customers}
    return [{"crm_id": p["record_id"], "customer_id": index[p["email"].strip().casefold()],
             "decision": "candidate_exact_email", "evidence": "normalized_email"}
            for p in crm if p["email"].strip().casefold() in index]


def splink_candidates(folder, threshold=0.8):
    """Run a small Splink 4 linkage experiment using DuckDB.

    The tiny fixture is not statistically representative. Review model output,
    tune blocking rules and calibrate on labels before any automated merge.
    """
    try:
        from splink import Linker, SettingsCreator, block_on
        import splink.comparison_library as cl
        from splink.internals.duckdb.database_api import DuckDBAPI
    except ImportError as exc:
        raise RuntimeError("Install splink>=4,<5 and duckdb>=1,<2") from exc
    source = [{"unique_id": "BANK-" + c["customer_id"],
               "full_name": c["full_name"], "email": c["email"], "region": c["region"],
               "source": "bank"} for c in rows(folder, "customers")]
    source += [{"unique_id": p["record_id"], "full_name": p["full_name"],
                "email": p["email"], "region": p["region"], "source": "crm"}
               for p in rows(folder, "crm_profiles")]
    settings = SettingsCreator(
        link_type="link_only", unique_id_column_name="unique_id",
        comparisons=[cl.ExactMatch("email"), cl.JaroWinklerAtThresholds("full_name", [0.9, 0.75]),
                     cl.ExactMatch("region")],
        blocking_rules_to_generate_predictions=[block_on("email"), block_on("full_name")],
    )
    linker = Linker(source, settings, db_api=DuckDBAPI())
    linker.training.estimate_u_using_random_sampling(max_pairs=100000)
    linker.training.estimate_parameters_using_expectation_maximisation(block_on("email"))
    linker.training.estimate_parameters_using_expectation_maximisation(block_on("full_name"))
    return linker.inference.predict(threshold_match_probability=threshold).as_record_dict()
