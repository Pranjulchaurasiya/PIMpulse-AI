import asyncio
import json
from graph import pimpulse_pipeline

async def main():
    queries = [
        "Frigidaire PDSH4816AF",
        "PDSH4816AF",
        "Trex 543140016 Lineage",
        "MlLW_ 49/94/0107 !!",
        "Siemens 3RT2015-1BB41",
        "SKF 6205-2RSH"
    ]
    for q in queries:
        print(f"\n==================== TESTING: {q} ====================")
        res = await pimpulse_pipeline.ainvoke({"raw_input": q})
        tax = res.get("taxonomy", {})
        print(f"Taxonomy: {tax.get('unspsc_code')} - {tax.get('class_name')}")
        print(f"Title: {res.get('standardized_title')}")
        print(f"INVOICE_DESC: {res.get('invoice_description')} ({len(res.get('invoice_description', ''))}/40)")
        print(f"MOBILE_DESC: {res.get('mobile_description')} ({len(res.get('mobile_description', ''))} chars)")
        print(f"Attributes: {list(res.get('attributes', {}).keys())}")
        print(f"Confidence: {res.get('confidence', {}).get('confidence_pct')}%")
        print(f"Auditor: {res.get('auditor_decision')}")

if __name__ == "__main__":
    asyncio.run(main())
