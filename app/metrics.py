from app.chunking import count_tokens
from app.corpus import CorpusManifest
from app.models import Metrics


def compute_metrics(manifest: CorpusManifest, quarantined_file_ids: set[str] | None = None) -> Metrics:
    """Ingestible surface = files not quarantined/archived. Passing
    quarantined_file_ids lets POST /fix recompute the "after" number live
    without re-running ingestion.
    """
    quarantined = quarantined_file_ids or set()
    live_files = [f for f in manifest.files if f.file_id not in quarantined]
    tokens = sum(count_tokens(f.full_text) for f in live_files)
    return Metrics(doc_count=len(live_files), ingestible_tokens=tokens)
