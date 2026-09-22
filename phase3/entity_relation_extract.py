from pathlib import Path
import argparse
import csv

from rdflib import Graph
from rdflib.namespace import RDF

PREFIXES = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix wsi: <http://example.org/wsi-workflow#> .

"""

def is_ttl_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("```"):
        return False
    if stripped.startswith("@prefix") or stripped.startswith("@base"):
        return True
    if stripped.startswith(("wsi:", "rdf:", "rdfs:", "owl:", "schema:", "prov:", "dct:", "xsd:", "ml:", "math:", "skos:", "dcterms:", "bio:", "cpath:", "patchgcn:", "path:", "ds:", "ex:")):
        return True
    if line[:1] in " \t" and stripped.startswith(("wsi:", "rdf:", "rdfs:", '"', "<")):
        return True
    return False


def qname(term, graph: Graph) -> str:
    try:
        return graph.namespace_manager.qname(term)
    except Exception:
        return str(term)


def fix_bad_escapes(text: str) -> str:
    valid = set("tbnrf\"'\\uU")
    out = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and text[i + 1] not in valid:
            out.append("\\\\")
            i += 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


parser = argparse.ArgumentParser()
parser.add_argument("--phase", type=str, default="phase3")
parser.add_argument("--step", type=str, default="b4")
parser.add_argument("--input_type", type=str, default="panther")
parser.add_argument("--prompt_type", type=str, default="final_prompt")
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent

result_path = root / args.phase / "results" / args.step / f"{args.prompt_type}_{args.input_type}.txt"
entities_path = root / args.phase / "results" / args.step / f"entities_{args.input_type}.csv"
relations_path = root / args.phase / "results" / args.step / f"relations_{args.input_type}.csv"

#### For Ground Truth Data
#result_path = root / "data" / "phase3" / f"{args.prompt_type}_{args.input_type}.txt"
#entities_path = root / "data" / "phase3" / f"entities_{args.input_type}.csv"
#relations_path = root / "data" / "phase3" / f"relations_{args.input_type}.csv"

raw_lines = result_path.read_text(encoding="utf-8").splitlines(keepends=True)
kept, dropped = [], []
for line in raw_lines:
    if is_ttl_line(line):
        kept.append(line)
    else:
        dropped.append(line)

ttl = fix_bad_escapes("".join(kept))
if "@prefix" not in ttl:
    ttl = PREFIXES + ttl

graph = Graph()
graph.parse(data=ttl, format="turtle")

entities_path.parent.mkdir(parents=True, exist_ok=True)

entity_rows = sorted(
    (qname(s, graph), qname(o, graph))
    for s, _, o in graph.triples((None, RDF.type, None))
)
with entities_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["entity", "type"])
    writer.writerows(entity_rows)

relation_rows = sorted({qname(p, graph) for _, p, _ in graph if p != RDF.type})
with relations_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["relation"])
    writer.writerows([[r] for r in relation_rows])

print(f"file: {result_path}")
print(f"total lines: {len(raw_lines)}")
print(f"kept ttl lines: {len(kept)}")
print(f"removed lines: {len(dropped)}")
print(f"entities: {len(entity_rows)}")
print(f"relations: {len(relation_rows)}")
print(f"saved: {entities_path}")
print(f"saved: {relations_path}")
