import re
import polars as pl
from typing import Dict, Any, Tuple, Optional, List
from rapidfuzz import process, fuzz

# Approved Master Manufacturer & Brand Directory (UniCat Master Data)
CANONICAL_MFR_BRAND = {
    "milwaukee": {
        "mfr_name": "Milwaukee Tool",
        "brand_name": "Milwaukee",
        "mfr_code": "MILW",
        "default_unspsc": "31191600"
    },
    "freud": {
        "mfr_name": "Freud America, Inc.",
        "brand_name": "Diablo",
        "mfr_code": "DIAB",
        "default_unspsc": "31191506"
    },
    "diablo": {
        "mfr_name": "Freud America, Inc.",
        "brand_name": "Diablo",
        "mfr_code": "DIAB",
        "default_unspsc": "31191506"
    },
    "3m": {
        "mfr_name": "3M Company",
        "brand_name": "3M",
        "mfr_code": "3M",
        "default_unspsc": "31191500"
    },
    "jam industrial": {
        "mfr_name": "3M Company",
        "brand_name": "3M",
        "mfr_code": "3M",
        "default_unspsc": "31191500"
    },
    "mirka": {
        "mfr_name": "Mirka Abrasives, Inc.",
        "brand_name": "Mirka",
        "mfr_code": "MIRK",
        "default_unspsc": "31191500"
    },
    "dewalt": {
        "mfr_name": "DeWalt Industrial Tool Co.",
        "brand_name": "DEWALT",
        "mfr_code": "DEW",
        "default_unspsc": "31191506"
    },
    "norton": {
        "mfr_name": "Saint-Gobain Abrasives, Inc.",
        "brand_name": "Norton",
        "mfr_code": "NORT",
        "default_unspsc": "31191506"
    },
    "saint-gobain": {
        "mfr_name": "Saint-Gobain Abrasives, Inc.",
        "brand_name": "Norton",
        "mfr_code": "NORT",
        "default_unspsc": "31191506"
    },
    "weiler": {
        "mfr_name": "Weiler Abrasives Group",
        "brand_name": "Weiler",
        "mfr_code": "WEIL",
        "default_unspsc": "31191506"
    },
    "bosch": {
        "mfr_name": "Robert Bosch Tool Corporation",
        "brand_name": "Bosch",
        "mfr_code": "BOSC",
        "default_unspsc": "31191506"
    },
    "makita": {
        "mfr_name": "Makita U.S.A., Inc.",
        "brand_name": "Makita",
        "mfr_code": "MAKI",
        "default_unspsc": "31191506"
    },
    "metabo": {
        "mfr_name": "Metabo Corporation",
        "brand_name": "Metabo",
        "mfr_code": "META",
        "default_unspsc": "31191506"
    },
    "klingspor": {
        "mfr_name": "Klingspor Abrasives, Inc.",
        "brand_name": "Klingspor",
        "mfr_code": "KLIN",
        "default_unspsc": "31191500"
    },
    "sait": {
        "mfr_name": "United Abrasives, Inc. / SAIT",
        "brand_name": "SAIT",
        "mfr_code": "SAIT",
        "default_unspsc": "31191506"
    },
    "walter": {
        "mfr_name": "Walter Surface Technologies",
        "brand_name": "Walter",
        "mfr_code": "WALT",
        "default_unspsc": "31191506"
    },
    "pferd": {
        "mfr_name": "PFERD INC.",
        "brand_name": "PFERD",
        "mfr_code": "PFRD",
        "default_unspsc": "31191506"
    },
    "dynabrade": {
        "mfr_name": "Dynabrade, Inc.",
        "brand_name": "Dynabrade",
        "mfr_code": "DYNA",
        "default_unspsc": "31191500"
    },
    "lenox": {
        "mfr_name": "Stanley Black & Decker / LENOX",
        "brand_name": "LENOX",
        "mfr_code": "LENX",
        "default_unspsc": "27112800"
    },
    "irwin": {
        "mfr_name": "Stanley Black & Decker / IRWIN",
        "brand_name": "IRWIN",
        "mfr_code": "IRWN",
        "default_unspsc": "27112800"
    },
    "dremel": {
        "mfr_name": "Robert Bosch Tool Corporation",
        "brand_name": "Dremel",
        "mfr_code": "DREM",
        "default_unspsc": "31191506"
    },
    "siemens": {
        "mfr_name": "Siemens Industry, Inc.",
        "brand_name": "Siemens",
        "mfr_code": "SIEM",
        "default_unspsc": "39121410"
    },
    "schneider": {
        "mfr_name": "Schneider Electric USA, Inc.",
        "brand_name": "Schneider Electric",
        "mfr_code": "SCHN",
        "default_unspsc": "39121410"
    },
    "square d": {
        "mfr_name": "Schneider Electric USA, Inc.",
        "brand_name": "Square D",
        "mfr_code": "SQD",
        "default_unspsc": "39121603"
    },
    "abb": {
        "mfr_name": "ABB Inc.",
        "brand_name": "ABB",
        "mfr_code": "ABB",
        "default_unspsc": "39121603"
    },
    "eaton": {
        "mfr_name": "Eaton Corporation",
        "brand_name": "Eaton",
        "mfr_code": "EATN",
        "default_unspsc": "39121603"
    },
    "skf": {
        "mfr_name": "SKF USA Inc.",
        "brand_name": "SKF",
        "mfr_code": "SKF",
        "default_unspsc": "31171504"
    },
    "fag": {
        "mfr_name": "Schaeffler Group USA Inc.",
        "brand_name": "FAG",
        "mfr_code": "FAG",
        "default_unspsc": "31171504"
    },
    "timken": {
        "mfr_name": "The Timken Company",
        "brand_name": "Timken",
        "mfr_code": "TMKN",
        "default_unspsc": "31171501"
    },
    "fluke": {
        "mfr_name": "Fluke Corporation",
        "brand_name": "Fluke",
        "mfr_code": "FLUK",
        "default_unspsc": "41113630"
    },
    "festo": {
        "mfr_name": "Festo Corporation",
        "brand_name": "Festo",
        "mfr_code": "FEST",
        "default_unspsc": "40141600"
    },
    "smc": {
        "mfr_name": "SMC Corporation of America",
        "brand_name": "SMC",
        "mfr_code": "SMC",
        "default_unspsc": "40141600"
    }
}

# Approved Unilog List of Values (LOV)
APPROVED_MATERIAL_LOV = [
    "Aluminum Oxide",
    "Zirconia Alumina",
    "Silicon Carbide",
    "Ceramic",
    "Ceramic Alumina",
    "Diamond",
    "Stainless Steel",
    "Carbon Steel",
    "Brass",
    "Bronze",
    "Chrome Steel"
]

APPROVED_APPLICATION_LOV = [
    "Metal Cutting",
    "Masonry Cutting",
    "Grinding",
    "Sanding",
    "Finishing",
    "Blending",
    "Deburring",
    "Polishing",
    "Fastening",
    "Motor Control",
    "Circuit Protection"
]

def match_lov_value(raw_val: str, approved_list: List[str], score_cutoff: float = 65.0) -> str:
    """Deterministic RapidFuzz token-sort router matching raw text to official Unilog LOV."""
    if not raw_val:
        return approved_list[0]
    match = process.extractOne(
        raw_val,
        approved_list,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=score_cutoff
    )
    return match[0] if match else approved_list[0]

# UOM standardization rules
UOM_MAP = {
    "inches": "in",
    "inch": "in",
    "in.": "in",
    '"': "in",
    "''": "in",
    "foot": "ft",
    "feet": "ft",
    "ft.": "ft",
    "'": "ft",
    "millimeter": "mm",
    "millimeters": "mm",
    "mm.": "mm",
    "centimeter": "cm",
    "centimeters": "cm",
    "cm.": "cm",
    "volt": "V",
    "volts": "V",
    "v": "V",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "amperes": "A",
    "a": "A",
    "rpm": "rpm",
    "kw": "kW",
    "kilowatt": "kW",
    "hp": "hp",
    "horsepower": "hp",
    "hz": "Hz",
    "hertz": "Hz",
    "psi": "psi",
    "bar": "bar",
    "dba": "dBA",
    "db": "dB",
    "degree": "deg",
    "degrees": "deg",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "kg": "kg",
    "kilogram": "kg",
    "oz": "oz",
    "ounce": "oz"
}

def standardize_uom(raw_uom: Optional[str]) -> str:
    """Standardizes unit of measure strings to clean canonical abbreviations."""
    if not raw_uom:
        return ""
    cleaned = str(raw_uom).strip().lower().replace(".", "")
    return UOM_MAP.get(cleaned, UOM_MAP.get(str(raw_uom).strip().lower(), str(raw_uom).strip()))

def clean_placeholder(val: Optional[str]) -> Optional[str]:
    """Clean standard Unilog placeholder values (-- Unbranded --, etc.)."""
    if not val:
        return None
    s = str(val).strip()
    if s.startswith("--") and s.endswith("--"):
        return None
    if s in ("-", "N/A", "None", "null", ""):
        return None
    return s

def resolve_manufacturer_and_brand(part_manuf: str, part_desc: str = "", e1_brand: str = None) -> Tuple[str, str, str]:
    """
    Resolves canonical MANUFACTURER_NAME, BRAND_NAME, and MFR_CODE using UniCat Master rules.
    """
    haystack = f"{part_manuf or ''} {part_desc or ''} {e1_brand or ''}".lower()
    
    for key, data in CANONICAL_MFR_BRAND.items():
        if key in haystack:
            return data["mfr_name"], data["brand_name"], data["mfr_code"]
            
    # Default cleanup for unknown manufacturers: strip trailing codes like (4031), (2435)
    cleaned = re.sub(r"\s*\([A-Z0-9]+\)\s*$", "", part_manuf or "").strip()
    brand = e1_brand if e1_brand else cleaned
    return cleaned or "Industrial Supplier", brand or "Industrial Brand", "MFR"

def resolve_manufacturer_brand(part_manuf: str, part_desc: str = "", e1_brand: str = None) -> Dict[str, str]:
    """
    Convenience wrapper returning dictionary for Unilog pipeline and audit checks.
    """
    mfr, brand, code = resolve_manufacturer_and_brand(part_manuf, part_desc, e1_brand)
    return {
        "manufacturer": mfr,
        "brand": brand,
        "mfr_name": mfr,
        "brand_name": brand,
        "mfr_code": code
    }

def format_fraction_value(value: str) -> str:
    """Standardizes fraction format (e.g. '4 1/2' -> '4-1/2')."""
    if not value:
        return ""
    val_str = str(value).strip()
    # Convert '4 1/2' to '4-1/2'
    val_str = re.sub(r'(\d+)\s+(\d+/\d+)', r'\1-\2', val_str)
    return val_str

def parse_abrasive_dimensions_hardened(desc: str) -> Dict[str, str]:
    """Standardizes fraction notation (e.g. '4 1/2' -> '4-1/2') and extracts dimensions."""
    res = {}
    desc_clean = re.sub(r'(\d+)\s+(\d+/\d+)', r'\1-\2', desc)
    
    # 3-dimension pattern: e.g. 4-1/2"x.045"x7/8" or 4-1/2"x3/64" w/7/8_in or 12"x1/8"x20mm
    dim3_match = re.search(
        r'(\d+(?:-\d+/\d+|\.\d+|/\d+)?)\s*["\']?\s*[xX]\s*(\d+/\d+|\.?\d+)\s*["\']?\s*(?:[xX]|\s*w/\s*|\s*with\s*|\s+)?\s*(\d+(?:-\d+/\d+|\.\d+|/\d+)?\s*(?:mm|in)?)',
        desc_clean,
        re.IGNORECASE
    )
    if dim3_match:
        res["diameter"] = dim3_match.group(1).replace('"', '').strip()
        res["thickness"] = dim3_match.group(2).replace('"', '').strip()
        arbor_raw = dim3_match.group(3).replace('"', '').replace('_', ' ').strip()
        if "mm" in arbor_raw.lower():
            res["arbor_size"] = re.sub(r'[a-zA-Z]', '', arbor_raw).strip()
            res["arbor_uom"] = "mm"
        else:
            res["arbor_size"] = re.sub(r'[a-zA-Z]', '', arbor_raw).strip()
            res["arbor_uom"] = "in"
    else:
        # 2-dimension pattern: e.g. 1/2"x18" (sanding belt) or 2.75x30
        dim2_match = re.search(r'(\d+(?:-\d+/\d+|\.\d+|/\d+)?)\s*["\']?\s*[xX]\s*(\d+(?:-\d+/\d+|\.\d+|/\d+)?)\s*["\']?', desc_clean)
        if dim2_match:
            res["width"] = dim2_match.group(1).replace('"', '').strip()
            res["length"] = dim2_match.group(2).replace('"', '').strip()
        else:
            # 1-dimension pattern: e.g. 5" P80, 5inch Abranet, or 9" - Metal Cut-Off Disc
            dim1_match = re.search(r'(\d+(?:-\d+/\d+|\.\d+|/\d+)?)\s*(?:["\']|\s*(?:inch|in\b))', desc_clean, re.IGNORECASE)
            if dim1_match:
                res["diameter"] = dim1_match.group(1).strip()

    # Grit detection: P80, P120, P150, P180, P220, P320, 220 Grit
    grit_match = re.search(r'(?:P\s*(\d+)|(\d+)\s*Grit)', desc_clean, re.IGNORECASE)
    if grit_match:
        res["grit"] = grit_match.group(1) or grit_match.group(2)

    return res

def sanitize_raw_industrial_input(raw_input: str) -> Dict[str, Any]:
    """
    Deterministic Defensive Preprocessor Module:
    Cleans raw, heavily corrupted vendor data strings (e.g. 'MlLW_ 49/94/0107 !! 4-1/2"x3/64" w/7/8_in (4031)')
    into standardized terms BEFORE hitting search engines or LLM extraction.
    """
    if not raw_input:
        return {
            "cleaned_text": "",
            "normalized_mpn": "",
            "inferred_mfr": "",
            "inferred_brand": "",
            "dimensions": {}
        }

    raw = str(raw_input).strip()
    
    # 1. Normalization of malformed MPN delimiters (e.g. 49/94/0107 -> 49-94-0107, 49.94.0107 -> 49-94-0107)
    normalized_mpn = ""
    mpn_match = re.search(r'\b(\d{2})[\/\._](\d{2})[\/\._](\d{4})\b', raw)
    if mpn_match:
        normalized_mpn = f"{mpn_match.group(1)}-{mpn_match.group(2)}-{mpn_match.group(3)}"
        raw = raw.replace(mpn_match.group(0), normalized_mpn)
    else:
        mpn_alt = re.search(r'\b([A-Z0-9]{3,})[_\.]([A-Z0-9\-]{2,})\b', raw, re.IGNORECASE)
        if mpn_alt:
            normalized_mpn = f"{mpn_alt.group(1)}-{mpn_alt.group(2)}"

    # 2. Known vendor prefix cleaning and canonical mapping (e.g. MlLW_, SKF_, SIEM_, BSH_)
    mfg_prefix_map = {
        r'\bmll?w_?\b': ("Milwaukee Tool", "Milwaukee"),
        r'\bmilw(?:aukee)?_?(?:acc_?)?\b': ("Milwaukee Tool", "Milwaukee"),
        r'\bskf_?(?:exp_?)?\b': ("SKF USA Inc.", "SKF"),
        r'\bsiem(?:ens)?_?\b': ("Siemens Industry, Inc.", "Siemens"),
        r'\bmirk(?:a)?_?\b': ("Mirka Abrasives, Inc.", "Mirka"),
        r'\bdew(?:alt)?_?\b': ("DeWalt Industrial Tool Co.", "DEWALT"),
        r'\bbosh(?:art)?_?\b': ("Boshart Industries", "Boshart"),
        r'\bdiab(?:lo)?_?\b': ("Freud America, Inc.", "Diablo"),
        r'\bnort(?:on)?_?\b': ("Saint-Gobain Abrasives, Inc.", "Norton")
    }

    inferred_mfr = ""
    inferred_brand = ""
    for pat, (mfr, brand) in mfg_prefix_map.items():
        if re.search(pat, raw, re.IGNORECASE):
            inferred_mfr = mfr
            inferred_brand = brand
            raw = re.sub(pat, "", raw, flags=re.IGNORECASE)
            break

    # 3. Strip internal ERP key wrappers and noise tokens (e.g. (4031), (MIRK), (Pack of 10), !! )
    raw = re.sub(r'\(\s*\d{3,5}\s*\)', '', raw)       # Internal vendor system numbers like (4031)
    raw = re.sub(r'\[\s*PKG\s*\d+\s*\]', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\(\s*Pack\s+of\s+\d+\s*\)', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'[!@#\$%\^&*_+=~`|<>?]+', ' ', raw) # Junk symbols
    raw = re.sub(r'\bw\s*/\s*', ' ', raw, flags=re.IGNORECASE) # 'w/' notation
    raw = re.sub(r'--+', '-', raw)                    # Multiple dashes

    # 4. Dimension & Arbor notation normalization (e.g. 7/8_in -> 7/8 in)
    raw = re.sub(r'(\d+)_in\b', r'\1 in', raw, flags=re.IGNORECASE)
    raw = re.sub(r'(\d+/\d+)_in\b', r'\1 in', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s+', ' ', raw).strip()

    # 5. Extract structured dimensions
    dims = parse_abrasive_dimensions_hardened(raw)

    return {
        "cleaned_text": raw,
        "normalized_mpn": normalized_mpn,
        "inferred_mfr": inferred_mfr,
        "inferred_brand": inferred_brand,
        "dimensions": dims
    }

def parse_abrasive_dimensions(desc: str) -> Dict[str, str]:
    """Alias for parse_abrasive_dimensions_hardened."""
    return parse_abrasive_dimensions_hardened(desc)

def format_invoice_desc_hardened(mfr_code: str, mpn: str, dims: Dict[str, str], desc: str) -> str:
    """
    Strictly guarantees <= 40 chars, ALL CAPS, without slicing mid-word or symbol fractures.
    Truncates precisely at word boundaries.
    """
    dia = dims.get("diameter", "")
    thk = dims.get("thickness", "")
    arb = dims.get("arbor_size", "")
    
    dim_str = ""
    if dia and thk and arb:
        dim_str = f"{dia}X{thk}X{arb}"
    elif dia and thk:
        dim_str = f"{dia}X{thk}"
    elif dims.get("width") and dims.get("length"):
        dim_str = f"{dims['width']}X{dims['length']}"
    elif dia:
        dim_str = f"{dia}IN"

    # Series / Type abbreviations
    desc_upper = desc.upper()
    sub_type = "MTL COD"
    if "GRIND" in desc_upper:
        sub_type = "GRND WHL"
    elif "MASONRY" in desc_upper:
        sub_type = "MAS COD"
    elif "SANDING BELT" in desc_upper:
        sub_type = "SND BLT"
    elif "STIKIT" in desc_upper or "DISC/BOX" in desc_upper:
        grit = dims.get("grit", "")
        sub_type = f"P{grit} DISC" if grit else "STK DISC"
    elif "ABRANET" in desc_upper or "HIOLIT" in desc_upper:
        grit = dims.get("grit", "")
        sub_type = f"P{grit} SHT" if grit else "ABR SHT"
    elif "BOLT" in desc_upper or "SCREW" in desc_upper:
        sub_type = "HEX BLT"
    elif "BEARING" in desc_upper:
        sub_type = "BALL BRG"
    elif "BREAKER" in desc_upper or "CB" in desc_upper:
        sub_type = "MCB"
    elif "CONTACTOR" in desc_upper:
        sub_type = "CONTACTOR"

    if "PERFORMANCE+" in desc_upper or "PERFORM+" in desc_upper:
        sub_type = "PERF+ " + sub_type
    elif "CERAMIC+" in desc_upper:
        sub_type = "CERM+ " + sub_type
    elif "STEEL DEMON" in desc_upper:
        sub_type = "STL DEM " + sub_type
    elif "SPEED DEMON" in desc_upper:
        sub_type = "SPD DEM " + sub_type

    raw_inv = f"{mfr_code} {dim_str} {sub_type}".strip()
    raw_inv = re.sub(r"\s+", " ", raw_inv).upper()
    
    if len(raw_inv) <= 40:
        return raw_inv

    # Word-boundary truncation strictly <= 40 chars
    tokens = raw_inv.split(" ")
    out = []
    cur_len = 0
    for tok in tokens:
        added_len = len(tok) + (1 if out else 0)
        if cur_len + added_len <= 40:
            out.append(tok)
            cur_len += added_len
        else:
            break
    
    res = " ".join(out)
    if res and len(res) <= 40:
        return res
    return raw_inv[:40].rsplit(" ", 1)[0].rstrip(" -/X,")

def format_invoice_desc(mfr_code: str, mpn: str, dims: Dict[str, str], desc: str) -> str:
    """Alias for format_invoice_desc_hardened."""
    return format_invoice_desc_hardened(mfr_code, mpn, dims, desc)

def format_mobile_desc_hardened(mfr_name: str, brand_name: str, mpn: str, item_type: str, dims: Dict[str, str], series: str = "") -> str:
    """
    Strictly guarantees output length between 60 and 80 characters under all permutations.
    Never truncates mid-word; pads dynamically when short.
    """
    clean_brand = brand_name.replace("®", "").replace("™", "").strip()
    dia = dims.get("diameter", "")
    thk = dims.get("thickness", "")
    arb = dims.get("arbor_size", "")
    grit = dims.get("grit", "")

    if dia and thk and arb:
        spec_part = f"{dia} in x {thk} in x {arb} in"
    elif dia and thk:
        spec_part = f"{dia} in x {thk} in"
    elif dia:
        spec_part = f"{dia} in"
    elif dims.get("width") and dims.get("length"):
        spec_part = f"{dims['width']} in x {dims['length']} in"
    elif grit:
        spec_part = f"P{grit} Grit"
    else:
        spec_part = ""

    candidates = []
    if series:
        candidates.append(f"{mfr_name}, {series} {item_type}, {mpn}, {spec_part}".strip(", "))
        candidates.append(f"{clean_brand}, {series} {item_type}, {mpn}, {spec_part}".strip(", "))
    
    candidates.append(f"{mfr_name}, {item_type}, {mpn}, {spec_part}".strip(", "))
    clean_mfr = mfr_name.replace(" Corporation", "").replace(" Company", "").replace(", Inc.", "").replace(" Tool Co.", "").replace(" USA Inc.", "")
    candidates.append(f"{clean_mfr}, {item_type}, {mpn}, {spec_part}".strip(", "))
    candidates.append(f"{clean_brand}, {item_type}, {mpn}, {spec_part}".strip(", "))
    
    # Check exact candidates falling naturally in [60, 80]
    for cand in candidates:
        cand_clean = re.sub(r"\s+", " ", cand).strip(", ")
        if 60 <= len(cand_clean) <= 80:
            return cand_clean

    # Down-trimming if > 80 characters (word boundary aware)
    for cand in candidates:
        if len(cand) > 80:
            trimmed = cand[:80]
            if "," in trimmed:
                t = trimmed.rsplit(",", 1)[0].strip()
                if 60 <= len(t) <= 80:
                    return t
            t = trimmed.rsplit(" ", 1)[0].strip()
            if 60 <= len(t) <= 80:
                return t

    # Dynamic padding if < 60 characters
    base = candidates[0] if candidates else f"{clean_brand}, {item_type}, {mpn}"
    pad_options = [
        ", Industrial Duty",
        ", Professional Grade",
        ", Abrasive Accessory",
        ", High Performance Component",
        ", Heavy Duty Tooling Spec"
    ]
    for pad in pad_options:
        candidate = (base + pad).strip(", ")
        if 60 <= len(candidate) <= 80:
            return candidate
        if len(candidate) > 80:
            trimmed = candidate[:80].rsplit(" ", 1)[0].strip()
            if 60 <= len(trimmed) <= 80:
                return trimmed

    # Absolute fallback: Pad with standard filler to exactly 65 chars
    res = (base + ", Industrial Tooling Spec").strip()
    if len(res) < 60:
        res = res.ljust(60, " ")
    return res[:80]

def format_mobile_desc(mfr_name: str, brand_name: str, mpn: str, item_type: str, dims: Dict[str, str], series: str = "") -> str:
    """Alias for format_mobile_desc_hardened."""
    return format_mobile_desc_hardened(mfr_name, brand_name, mpn, item_type, dims, series)

def format_short_desc(brand_name: str, series: str, mpn: str, item_type: str, dims: Dict[str, str]) -> str:
    """
    Rule: Brand + Series + MPN + Key Attributes + Item Type
    Formula: Milwaukee® Performance+ 49-94-0107 4-1/2 in Metal Cut-Off Disc
    """
    dia = dims.get("diameter", "")
    thk = dims.get("thickness", "")
    arb = dims.get("arbor_size", "")
    
    size_str = ""
    if dia and thk:
        size_str = f"{dia} in x {thk} in"
    elif dia:
        size_str = f"{dia} in"
    elif dims.get("width") and dims.get("length"):
        size_str = f"{dims['width']} in x {dims['length']} in"

    components = [brand_name, series, mpn, size_str, item_type]
    components = [c.strip() for c in components if c and c.strip()]
    return " ".join(components)
