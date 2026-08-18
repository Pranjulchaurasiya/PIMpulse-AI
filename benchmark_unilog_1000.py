import time
import asyncio
import polars as pl
from agents.unilog_pipeline import process_unilog_dataset

async def main():
    print("=" * 80)
    print("  PIMpulse AI — UniHack 2026 1000-Row Dataset Comprehensive Benchmark")
    print("=" * 80)

    t0 = time.perf_counter()
    res = await process_unilog_dataset(
        input_csv_path="Unihack__Sample_Dataset_-_Input.csv",
        max_rows=1000,
        output_csv_path="PIMpulse_Unilog_Enriched_1000.csv"
    )
    elapsed = time.perf_counter() - t0
    processed = res["processed_count"]
    throughput = processed / elapsed if elapsed > 0 else 0
    avg_latency = (elapsed / processed) * 1000.0 if processed > 0 else 0

    print(f"\n[PERFORMANCE METRICS]")
    print(f"Total Rows Processed:   {processed}")
    print(f"Total Columns Built:    {res['total_columns']} (Official 252-Column Standard)")
    print(f"Total Elapsed Time:     {elapsed:.2f} seconds")
    print(f"Throughput:             {throughput:.1f} SKUs/second (~{throughput * 3600 * 24:.0f} SKUs/day)")
    print(f"Average Latency:        {avg_latency:.2f} ms/SKU")
    print(f"Output CSV Path:        {res['output_csv']}")
    print(f"Output XLSX Path:       {res['output_xlsx']}")

    # Quality Gate Verification on the generated 1000-row CSV
    df = pl.read_csv("PIMpulse_Unilog_Enriched_1000.csv")
    inv_lens = df["INVOICE_DESC"].str.len_chars()
    mob_lens = df["MOBILE_DESC"].str.len_chars()

    inv_violations = df.filter(pl.col("INVOICE_DESC").str.len_chars() > 40).height
    mob_violations = df.filter((pl.col("MOBILE_DESC").str.len_chars() < 60) | (pl.col("MOBILE_DESC").str.len_chars() > 80)).height

    inv_pct = ((processed - inv_violations) / max(processed, 1)) * 100.0
    mob_pct = ((processed - mob_violations) / max(processed, 1)) * 100.0

    print(f"\n[MDM DATA QUALITY AUDIT]")
    print(f"INVOICE_DESC Compliance: {processed - inv_violations}/{processed} ({inv_pct:.1f}%) [Max: {inv_lens.max()}, Min: {inv_lens.min()}]")
    print(f"MOBILE_DESC Compliance:  {processed - mob_violations}/{processed} ({mob_pct:.1f}%) [Max: {mob_lens.max()}, Min: {mob_lens.min()}]")
    print(f"Zero Length Violations:  {'PASSED [100% PERFECT]' if inv_violations == 0 and mob_violations == 0 else 'FAILED'}")

    brands = df["BRAND_NAME"].unique().to_list()
    print(f"Unique Brands Resolved:  {len(brands)} {brands[:8]}...")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
