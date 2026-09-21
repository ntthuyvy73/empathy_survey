# -*- coding: utf-8 -*-
"""P1 WAVE 3 — KHU TRUNG MANH + LAM GIAU (dataset, link du lieu).

VAN DE cua ban khu trung cu (dedup_ris.norm_title): chi bo ky tu khong phai chu-so
NHUNG giu khoang trang -> ba loai trung VAN LOT:
  1. Ngoac nhon BibTeX cua ACL: "{PATIENT}"/"Empathy-driven {A}rabic" -> "a rabic"
     KHAC "arabic" -> khong khop ban OpenAlex/WoS cua CUNG bai.
  2. LaTeX/Unicode: "{PATIENT}-$\\psi$" vs "PATIENT-Psi" (chu Hy Lap) -> khac nhau.
  3. Khac khoang trang: "Context Word" vs "ContextWord".
Khoa moi (strong key): bo ngoac nhon -> bo LaTeX -> NFKD ve ASCII -> bo TAT CA ky tu
khong phai chu-so KE CA khoang trang. Kem khoa DOI chuan hoa va khoa arXiv-id (bat cap
preprint <-> ban xuat ban qua DOI 10.48550/arXiv.xxxx). Gop nhom bang union-find.

Ket qua: MOI bai bao = 1 dong duy nhat, co cot 'sources'/'n_sources' cho biet bai do
xuat hien o nhung CSDL nao (tra loi 'bai nao lap lai o nhieu noi').
Lam giau tu abstract (quet HOP abstract cua ca nhom -> recall cao nhat):
  - cot 'dataset'      : ten bo du lieu (da biet + ung vien moi), '' neu khong thay
  - cot 'link_data'    : URL du lieu/ma nguon duoc nhac (github, huggingface, zenodo...)
  - cot 'link_host'    : loai nguon cua link (github/huggingface/...)
  - kem availability, therapy, era nhu wave3_analysis.py
Xuat: search_exports/wave3_unique_for_screening.csv  (danh sach sang loc CHINH THUC)
      search_exports/wave3_duplicate_groups.csv      (nhat ky: nhom nao gop tu dau)
      _notes/wave3_unique_report.md                  (bao cao)
Chay: python wave3_unique_enrich.py"""
import os
import re
import csv
import sys
import glob
import unicodedata
from collections import Counter, defaultdict
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dedup_ris as D
import extract_datasets as XD
from p1_query_terms import CUTOFF_DATE_W3

NOTES = os.path.dirname(os.path.abspath(__file__))
EXPORTS = D.EXPORTS
CUTOFF_YEAR = int(CUTOFF_DATE_W3[:4])
# do dai toi thieu cua khoa tieu de de duoc phep gop theo tieu de (~4-5 tu)
MIN_TITLE_KEY = 25
# do tin cay sieu du lieu khi chon tieu de dai dien: OpenAlex co mot so ban ghi
# gan SAI tieu de voi DOI (vd 'Hymn Of Consecration' deo DOI cua 'Rate My Therapist')
SRC_TRUST = {"PubMed": 0, "WoS": 1, "ACL": 2, "arXiv": 3, "OpenAlex": 4}


# ---------------------------------------------------------------- khoa chuan hoa
def strong_key(t):
    """Khoa tieu de manh: chiu duoc ngoac BibTeX, LaTeX, Unicode, khac khoang trang."""
    if not t:
        return ""
    s = t.replace("{", "").replace("}", "")          # {PATIENT} -> PATIENT
    s = re.sub(r"\$[^$]*\$", " ", s)                 # $\psi$ -> (bo)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)               # \psi, \textbf
    s = re.sub(r"<[^>]+>", " ", s)                   # <i>...</i>
    s = re.sub(r"&[a-z]+;", " ", s)                  # &amp;
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "", s)                 # bo CA khoang trang
    # JMIR/tap chi y khoa dat hau to '(Preprint)' cho ban tien an -> bo de ban tien an
    # va ban xuat ban cua CUNG bai gop lam mot
    return re.sub(r"(?:preprint|inpress|earlyaccess|authorversion)$", "", s)


ARXIV_RE = re.compile(r"(?:arxiv[:/\s]|abs/|10\.48550/arxiv\.)\s*(\d{4}\.\d{4,5})", re.I)


def arxiv_id_of(rec):
    m = ARXIV_RE.search(rec.get("raw", "") or "")
    return m.group(1) if m else ""


def norm_doi2(d):
    d = D.norm_doi(d)
    return re.sub(r"v\d+$", "", d)                   # bo hau to version neu co


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


# ---------------------------------------------------------------- trich xuat
URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"'\)\]\},;]+", re.I)
BARE_RE = re.compile(r"\b(?:github\.com|huggingface\.co|gitlab\.com|zenodo\.org|osf\.io|"
                     r"figshare\.com|dataverse\.[a-z.]+|kaggle\.com|codeocean\.com|"
                     r"anonymous\.4open\.science)/[^\s<>\"'\)\]\},;]+", re.I)
# NOI LUU DU LIEU/MA NGUON that su -> tinh la link du lieu (va dung cho nhan 'open')
DATA_HOSTS = [("github.io", "github"), ("github.com", "github"),
              ("huggingface.co", "huggingface"), ("gitlab", "gitlab"), ("zenodo", "zenodo"),
              ("osf.io", "osf"), ("figshare", "figshare"), ("dataverse", "dataverse"),
              ("kaggle", "kaggle"), ("codeocean", "codeocean"),
              ("4open.science", "anonymous-4open"), ("drive.google", "google-drive"),
              ("sites.google", "google-sites"), ("dropbox", "dropbox"),
              ("sourceforge", "sourceforge"), ("physionet", "physionet"),
              ("openslr", "openslr"), ("bitbucket", "bitbucket"),
              ("datadryad", "dryad"), ("dryad", "dryad"), ("openneuro", "openneuro"),
              ("mendeley.com/datasets", "mendeley-data"), ("ldc.upenn", "ldc"),
              # kho du lieu tro qua DOI: doi.org/10.5281/zenodo..., .../10.17605/OSF.IO/...
              # (cac ten tren da khop san trong URL); them tien to DOI khong chua ten kho:
              ("10.7910/dvn", "dataverse"), ("10.24433", "codeocean"),
              ("10.13026", "physionet"), ("10.18112", "openneuro"),
              ("modelscope", "modelscope"), ("parl.ai", "parlai")]
# DANG KY thu nghiem/de cuong -> huu ich nhung KHONG phai link du lieu (cot rieng)
REGISTRY = [("clinicaltrials.gov", "ClinicalTrials"), ("isrctn", "ISRCTN"),
            ("chictr.org", "ChiCTR"), ("crd.york.ac.uk", "PROSPERO"),
            ("prospero", "PROSPERO"), ("anzctr", "ANZCTR"), ("drks.de", "DRKS"),
            ("umin.ac.jp", "UMIN"), ("irct.ir", "IRCT"), ("trialregister", "NTR"),
            ("clinicaltrialsregister.eu", "EU-CTR"), ("researchregistry", "ResearchRegistry")]
# LOAI HAN: giay phep, ha tang trich dan, nha xuat ban, rac quang cao
DENY = ("creativecommons.org", "doi.org", "orcid.org", "w3.org", "webofscience",
        "scopus.com", "pubmed.ncbi", "ncbi.nlm.nih.gov", "semanticscholar",
        "researchgate", "springer", "sciencedirect", "onlinelibrary.wiley", "wiley.com",
        "tandfonline", "sagepub", "frontiersin", "mdpi.com", "jmir.org", "elsevier",
        "academic.oup.com", "nature.com", "journals.plos", "biomedcentral",
        "ieee.org", "ieeexplore", "acm.org", "aclanthology", "arxiv.org",
        "shutterstock", "brainyquote", "perfectessaywriter", "medium.com",
        "youtube.com", "youtu.be", "wikipedia.org", "linkedin.com", "twitter.com",
        "facebook.com", "apa.org", "who.int", "cdc.gov", "nih.gov",
        "opendatacommons.org", "usability.gov", "alsoasked.com", "iaeme.com")


def extract_links(blob):
    """Tra ve (link du lieu, nhan noi luu, link dang ky thu nghiem).
    Bo link giay phep/nha xuat ban/trich dan/rac; tach rieng link dang ky."""
    blob = blob.replace("\\n", " ").replace("\n", " ")   # abstract co '\n' nguyen van
    found = []
    for m in list(URL_RE.finditer(blob)) + list(BARE_RE.finditer(blob)):
        u = m.group(0).rstrip(".,;:)]}’'\"")
        if u.lower().startswith("www."):
            u = "https://" + u
        elif not u.lower().startswith("http"):
            u = "https://" + u
        if u not in found:
            found.append(u)
    data, hosts, regs = [], [], []
    for u in found:
        low = u.lower()
        host = re.sub(r"^https?://", "", low).split("/")[0]
        # bo URL cut cut ('https://www', 'https://register') hoac khong co TLD hop le
        if "." not in host or not re.search(r"\.[a-z]{2,}$", host):
            continue
        reg = next((lab for frag, lab in REGISTRY if frag in low), "")
        if reg:
            if u not in regs:
                regs.append(f"{reg}: {u}")
            continue
        # PHAI xet kho du lieu TRUOC DENY: doi.org/10.5281/zenodo... va
        # doi.org/10.17605/OSF.IO/... la link DU LIEU that, du chua 'doi.org'
        h = next((lab for frag, lab in DATA_HOSTS if frag in low), "")
        if not h:
            if any(d in low for d in DENY):
                continue
            h = "khac"
        data.append(u)
        if h not in hosts:
            hosts.append(h)
    return data, hosts, regs


AVAIL_OPEN = re.compile(
    r"github\.com|huggingface|zenodo|osf\.io|gitlab\.com|"
    r"publicly (?:available|released|accessible)|open[- ]sourced?|freely available|"
    r"openly available|made (?:publicly )?available|"
    r"we (?:release|publish|open[- ]source)|will be (?:released|made (?:publicly )?available)|"
    r"code (?:and data )?(?:is|are|will be) available|data(?:set)? (?:is|are|will be) available|"
    r"available (?:at|on|via) (?:https?://|our)", re.I)
AVAIL_COND = re.compile(r"upon (?:reasonable )?request|on (?:reasonable )?request|by request|"
                        r"data use agreement|available from the (?:corresponding )?author", re.I)
AVAIL_CLOSED = re.compile(r"not (?:be )?(?:publicly |openly )?(?:available|released|shared)|"
                          r"cannot be (?:shared|released|made available)|proprietary|"
                          r"confidential|privacy (?:concerns|restrictions|reasons)", re.I)
DATA_MENTION = re.compile(r"\b(dataset|datasets|corpus|corpora|benchmark|benchmarks)\b", re.I)


def availability(blob, has_data_host):
    """has_data_host = co link toi NOI LUU DU LIEU da biet (github/HF/zenodo...),
    khong tinh link 'khac' vi chua chac la du lieu."""
    o = bool(AVAIL_OPEN.search(blob)) or has_data_host
    c, cl = bool(AVAIL_COND.search(blob)), bool(AVAIL_CLOSED.search(blob))
    if o and cl:
        return "mixed"
    if o:
        return "open"
    if c:
        return "conditional"
    if cl:
        return "closed"
    return "unstated"


# --- ten dataset -------------------------------------------------------------
# STOP mo rong: them ten MO HINH/PHUONG PHAP/do do hay bi bat nham o vong truoc
EXTRA_STOP = {
    "seq2seq", "sequencetosequence", "asr", "tts", "cvae", "vae", "gan", "gans", "sam",
    "lstm", "bilstm", "gru", "mlp", "svm", "knn", "crf", "hmm", "tfidf", "tf-idf",
    "pca", "lda", "nmf", "sgd", "adam", "relu", "bpe", "ner", "pos", "srl", "mt",
    "nlu", "nlg", "vad", "eeg", "ecg", "hrv", "gsr", "roc", "mae", "rmse", "mse",
    "kl", "js", "em", "map", "mrr", "ndcg", "cer", "wer", "eer", "ui", "ux", "hci",
    "iot", "ar", "vr", "xr", "gpu", "cpu", "ram", "sdk", "ide", "os", "pdf", "csv",
    "json", "xml", "html", "css", "sql", "aws", "gcp", "cot", "rag", "peft", "moe",
    "kd", "nas", "sota", "qa", "ir", "rl", "il", "gnn", "gcn", "gat", "transformer",
    "bertscore", "rouge", "bleu", "meteor", "cider", "spice", "f1", "auc", "auroc",
    "who", "un", "nih", "nhs", "fda", "irb", "gdpr", "hipaa", "apa", "dsm", "icd",
    "phq", "gad", "pcl", "bdi", "hamd", "panas", "wai", "miti", "misc", "ctrs",
    "mi", "cbt", "dbt", "act", "ipt", "mbct", "emdr", "sfbt", "rebt", "esc",
    "llm", "llms", "gpt", "chatgpt", "bert", "roberta", "t5", "bart", "llama",
    "qwen", "vicuna", "mistral", "gemini", "claude", "palm", "opt", "glm",
    "pfa", "peld", "mdd", "ptsd", "adhd", "ocd", "gad7", "sad", "bpd", "asd",
    "mhps", "vas", "dss", "bbn", "css", "csc", "csd", "chds", "chms", "htp",
    "ai", "nlp", "ml", "dl", "usa", "uk", "eu", "us", "covid",
}
STOP = {s.lower() for s in XD.STOP} | EXTRA_STOP

INTRO_VERB = (r"(?:introduce|present|propose|construct|build|release|collect|create|develop|"
              r"curate|compile|annotate|design|contribute|publish|establish)")
DATA_NOUN = r"(?:dataset|data set|corpus|benchmark|collection|resource)"
# "we introduce X, a ... dataset" / "dataset named X" / "X, a new corpus"
PAT_NAMED = re.compile(
    rf"\b{DATA_NOUN}s?\s+(?:named|called|dubbed|termed)\s+([A-Z][\w\-]{{1,28}})", re.I)
PAT_INTRO_NAME = re.compile(
    rf"\bwe\s+(?:\w+\s+){{0,2}}{INTRO_VERB}\s+(?:a\s+|an\s+|the\s+)?(?:new\s+|novel\s+|"
    rf"large[- ]scale\s+)?(?:{DATA_NOUN}\s+)?(?:named|called|dubbed)?\s*"
    rf"\b([A-Z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*)\b")
PAT_X_IS_DATA = re.compile(
    rf"\b([A-Z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*)\s*,?\s+(?:is|as)?\s*"
    rf"(?:a|an|the)\s+(?:\w+[- ]){{0,3}}{DATA_NOUN}\b")


def looks_like_name(tok):
    """Ten dataset thuong: >=2 chu HOA, hoac CamelCase, hoac co so; >=3 ky tu."""
    if len(tok) < 3 or tok.lower() in STOP:
        return False
    if tok.isdigit():
        return False
    caps = sum(c.isupper() for c in tok)
    return (caps >= 2 or re.search(r"[a-z][A-Z]", tok)
            or (caps >= 1 and any(c.isdigit() for c in tok)))


# Ten dataset TRUNG voi tu tieng Anh thong dung -> neu tim thuong se bat nham hang loat
# (do do thuc te: 'peer' khop 441 bai, 'heart' 119, 'split' 33 vi la tu thuong).
# Voi cac ten nay CHI tinh khi van ban viet HOA toan bo (PEER, HEART) — chap nhan bo sot
# de doi lay do chinh xac, vi Vy con sang loc tay o buoc sau.
AMBIG_WORDS = {
    "care", "calls", "cactus", "compass", "hailey", "heart", "hope", "imbue", "magnet",
    "medic", "midas", "partner", "peer", "recap", "smile", "split", "studies", "epitome",
    "harbor", "helping", "insight", "mind", "omind", "pair", "sense", "story", "trust",
}


def _all_caps(seg):
    al = [c for c in seg if c.isalpha()]
    return len(al) > 20 and sum(c.isupper() for c in al) / len(al) > 0.7


def caps_safe(title, abstracts):
    """Bo cac doan VIET HOA TOAN BO truoc khi tim ten mo ho o dang HOA. Hai nguon nhieu:
      - tieu de WoS viet hoa het ('THE LANGUAGE OF EMPATHY ... PEER SUPPORT')
      - tieu de muc cua abstract co cau truc ('IMPLICATIONS FOR ... PATIENT CARE:')
    Vi vay tach tieu de thanh doan RIENG va cat them o dau ':' (khong chi '.!?')."""
    segs = [title]
    for ab in abstracts:
        segs += re.split(r"(?<=[.!?:])\s+|\n", ab)
    return " ".join(s for s in segs if not _all_caps(s))


def known_names(title, abstracts, known_list, ambig):
    """Tra ve (ten sach, ten hien thi). Ten mo ho duoc danh dau '(?)' de Vy biet
    la can kiem tra tay — vi ngay ca khi VIET HOA, 'CARE'/'COMPASS'/'SPLIT' van co
    the la thang do, ten thu nghiem hay acronym khac chu khong phai bo du lieu."""
    blob = title + "  " + "  ".join(abstracts)
    low = blob.lower()
    safe = caps_safe(title, abstracts)
    clean, show = [], []
    for k in known_list:
        if k in ambig:
            if re.search(r"\b" + re.escape(k.upper()) + r"\b", safe):
                clean.append(k)
                show.append(k + "(?)")
        elif re.search(r"\b" + re.escape(k) + r"\b", low):
            clean.append(k)
            show.append(k)
    order = sorted(range(len(clean)), key=lambda i: clean[i])
    return [clean[i] for i in order], [show[i] for i in order]


def candidate_names(title, blob):
    cands = []
    # 1. tien to truoc dau ':' trong tieu de (mau bai gioi thieu bo du lieu)
    m = re.match(r"\s*([A-Za-z0-9][\w\-Ψψ ]{1,30}?)\s*:", title.replace("{", "").replace("}", ""))
    if m and DATA_MENTION.search(blob):
        for tok in re.findall(r"[A-Za-z][\w\-]*", m.group(1)):
            if looks_like_name(tok):
                cands.append(tok)
    # 2. cac mau cau ro rang
    for pat in (PAT_NAMED, PAT_INTRO_NAME, PAT_X_IS_DATA):
        for mm in pat.finditer(blob):
            tok = mm.group(1)
            if looks_like_name(tok):
                cands.append(tok)
    # 3. acronym trong ngoac don, chi khi cau co dau hieu du lieu
    if DATA_MENTION.search(blob):
        for tok in re.findall(r"\(([A-Z][A-Za-z0-9\-]{2,})\)", blob):
            if looks_like_name(tok):
                cands.append(tok)
    out, seen = [], set()
    for c in cands:
        if c.lower() not in seen:
            seen.add(c.lower())
            out.append(c)
    return out


# ---------------------------------------------------------------- doc du lieu
def clean_title(t):
    """Bo ngoac nhon BibTeX va the danh dau de tieu de doc duoc."""
    t = (t or "").replace("{", "").replace("}", "")
    t = re.sub(r"\$\\?([A-Za-z]+)\$", r"\1", t)          # $\psi$ -> psi
    t = re.sub(r"</?[a-z]+[^>]*>", "", t)                # <i>, <scp>
    t = re.sub(r"&lt;[^&]*&gt;", "", t)
    return re.sub(r"\s+", " ", t).strip()


def pick_title(g):
    """Chon tieu de dai dien bang BO PHIEU DA SO: tieu de giong cac ban khac nhat
    thang. Ly do: OpenAlex co ban ghi gan SAI tieu de vao DOI dung — tieu de rac do
    lech han so voi cac ban con lai nen se thua. Hoa thi uu tien nguon tin cay hon.
    Tra ve (tieu de sach, danh sach tieu de lech de ghi vao nhat ky)."""
    import difflib
    ts = [(r["source"], r["title"]) for r in g if r["title"]]
    if not ts:
        return "", []
    if len(ts) == 1:
        return clean_title(ts[0][1]), []
    keys = [strong_key(t) for _, t in ts]
    scores = []
    for i, (src, t) in enumerate(ts):
        sim = sum(difflib.SequenceMatcher(None, keys[i], keys[j]).ratio()
                  for j in range(len(ts)) if j != i)
        scores.append((-sim, SRC_TRUST.get(src, 5), "{" in t, -len(t), i))
    scores.sort()
    best = scores[0][4]
    # tieu de lech han (giong <0.5 so voi ban duoc chon) -> dau hieu sieu du lieu sai
    lech = [t for i, (_, t) in enumerate(ts) if i != best
            and difflib.SequenceMatcher(None, keys[best], keys[i]).ratio() < 0.5]
    return clean_title(ts[best][1]), lech


def read_csv_rows(path):
    if not os.path.exists(path):
        return []
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    return []


def load_pool():
    """Pool da biet: wave1 + wave2 + expert + 123 bai da chot -> tap khoa manh."""
    recs = D.parse_file(os.path.join(EXPORTS, "all_dedup.ris"), "pool_w1")
    for f in sorted(glob.glob(os.path.join(EXPORTS, "*_w2.ris"))
                    + glob.glob(os.path.join(EXPORTS, "*_w2.nbib"))):
        recs += (D.parse_nbib(f, "pool_w2") if f.lower().endswith(".nbib")
                 else D.parse_file(f, "pool_w2"))
    keys, dois, axs = set(), set(), set()
    for r in recs:
        k = strong_key(r["title"])
        if k:
            keys.add(k)
        if r["ndoi"]:
            dois.add(norm_doi2(r["ndoi"]))
        a = arxiv_id_of(r)
        if a:
            axs.add(a)
    for row in read_csv_rows(os.path.join(EXPORTS, "citation_expert.csv")):
        k = strong_key(row.get("title", ""))
        if k:
            keys.add(k)
        m = re.search(r"10\.\d{4,9}/\S+", row.get("doi_url", "") or "")
        if m:
            dois.add(norm_doi2(m.group(0)))
        m2 = ARXIV_RE.search(row.get("doi_url", "") or "")
        if m2:
            axs.add(m2.group(1))
    for row in read_csv_rows(os.path.join(EXPORTS, "included_resources.csv")):
        k = strong_key(row.get("title", ""))
        if k:
            keys.add(k)
    return keys, dois, axs, len(recs)


def main():
    # --- danh muc dataset da biet: KNOWN cu + dataset_key cua 123 bai da chot ----
    known_list = list(XD.KNOWN)
    for row in read_csv_rows(os.path.join(EXPORTS, "included_resources.csv")):
        dk = (row.get("dataset_key") or "").strip().lower()
        if dk and dk not in known_list:
            known_list.append(dk)
    known_list = [k for k in known_list if len(k) >= 3]
    ambig = set(XD.AMBIG) | AMBIG_WORDS
    ambig_dung = sorted(k for k in known_list if k in ambig)
    print(f"Danh muc dataset da biet: {len(known_list)} ten "
          f"(KNOWN cu {len(XD.KNOWN)} + tu included_resources)")
    print(f"  {len(ambig_dung)} ten trung tu tieng Anh thuong -> chi tinh khi VIET HOA: "
          f"{', '.join(ambig_dung)}")

    pool_keys, pool_dois, pool_axs, n_pool = load_pool()
    print(f"Pool da biet: {n_pool} ban ghi -> {len(pool_keys)} khoa manh / "
          f"{len(pool_dois)} doi / {len(pool_axs)} arXiv-id")

    # --- doc toan bo wave 3 -----------------------------------------------------
    files = sorted(glob.glob(os.path.join(EXPORTS, "*_w3.ris"))
                   + glob.glob(os.path.join(EXPORTS, "*_w3.nbib")))
    if not files:
        sys.exit("Chua thay file *_w3 — chay harvest_wave3.py / p1_wave3_delta.py truoc.")
    recs, per_file = [], {}
    for f in files:
        src = D.source_of(f)
        rs = (D.parse_nbib(f, src) if f.lower().endswith(".nbib") else D.parse_file(f, src))
        per_file[os.path.basename(f)] = len(rs)
        recs.extend(rs)
    print(f"Doc {len(files)} file wave 3: {len(recs)} ban ghi tho")

    # --- gop nhom bang union-find ----------------------------------------------
    uf = UF()
    for i, r in enumerate(recs):
        r["_i"] = i
        r["_key"] = strong_key(r["title"])
        r["_doi"] = norm_doi2(r["ndoi"])
        r["_ax"] = arxiv_id_of(r)
        uf.find(("rec", i))
        # CHI gop theo tieu de khi tieu de du DAI. Tieu de ngan/chung chung
        # ('WITHDRAWN', 'Shop Talk', 'Books Reviewed', 'Working Paper') xuat hien o
        # nhieu bai KHAC NHAU; neu gop se noi day chuyen ca nhung bai khong lien quan.
        if len(r["_key"]) >= MIN_TITLE_KEY:
            uf.union(("t", r["_key"]), ("rec", i))
        if r["_doi"]:
            uf.union(("d", r["_doi"]), ("rec", i))
        if r["_ax"]:
            uf.union(("a", r["_ax"]), ("rec", i))
    groups = defaultdict(list)
    for r in recs:
        groups[uf.find(("rec", r["_i"]))].append(r)
    print(f"Gop thanh {len(groups)} bai bao DUY NHAT "
          f"(giam {len(recs) - len(groups)} ban ghi trung)")

    # --- xu ly tung nhom --------------------------------------------------------
    uniq, dupgroups = [], []
    n_in_pool = 0
    beyond = []
    for gid, g in groups.items():
        srcs = sorted({r["source"] for r in g})
        # dai dien: uu tien co DOI, roi abstract dai nhat
        rep = sorted(g, key=lambda r: (bool(r["_doi"]), len(r["abstract"] or "")),
                     reverse=True)[0]
        title, title_lech = pick_title(g)
        years = sorted({r["year"] for r in g if r["year"]})
        year = rep["year"] or (years[0] if years else "")
        venue = max((r["venue"] or "" for r in g), key=len)
        doi_url = next((r["doi_url"] for r in g if r["doi_url"]), "")
        # HOP abstract ca nhom -> recall cao nhat cho link/ten dataset
        abstracts = sorted({(r["abstract"] or "").strip() for r in g if r["abstract"]},
                           key=len, reverse=True)
        blob_all = title + "  " + "  ".join(abstracts)
        abstract = abstracts[0] if abstracts else ""

        if year and int(year) > CUTOFF_YEAR:
            beyond.append((srcs, year, title))
            continue
        # trung pool cu?
        if (any(r["_key"] and r["_key"] in pool_keys for r in g)
                or any(r["_doi"] and r["_doi"] in pool_dois for r in g)
                or any(r["_ax"] and r["_ax"] in pool_axs for r in g)
                or any(r["an"] and r["an"] in pool_dois for r in g)):
            n_in_pool += 1
            continue

        links, hosts, regs = extract_links(blob_all)
        kn, kn_show = known_names(title, abstracts, known_list, ambig)
        cd = candidate_names(title, blob_all)
        cd = [c for c in cd if c.lower().replace("-", "") not in
              {k.replace("-", "").replace(" ", "") for k in kn}]
        dataset = "; ".join(kn_show + [c for c in cd if c.lower() not in {k.lower() for k in kn}])
        av = availability(blob_all, any(h != "khac" for h in hosts))
        ther = sorted({v for k, v in XD.THERAPY.items() if k in blob_all.lower()})
        era = ("pre-2021" if year and int(year) < 2021 else "2021+") if year else ""
        if kn:
            bucket = "known-dataset"
        elif cd:
            bucket = "candidate-new"
        elif DATA_MENTION.search(blob_all):
            bucket = "mentions-data"
        else:
            bucket = "no-data-signal"

        uniq.append(dict(
            source_chinh=rep["source"], sources="; ".join(srcs), n_sources=len(srcs),
            n_ban_ghi=len(g), year=year,
            nam_khac=("; ".join(years) if len(years) > 1 else ""),
            era=era, venue=venue, title=title, doi_url=doi_url,
            dataset=dataset, dataset_da_biet="; ".join(kn_show),
            dataset_ung_vien="; ".join(cd), bucket=bucket,
            link_data="; ".join(links), link_host="; ".join(hosts),
            link_dang_ky="; ".join(regs),
            canh_bao_sieu_du_lieu=(" | ".join(title_lech) if title_lech else ""),
            availability=av, therapy="; ".join(ther), abstract=abstract))
        if len(g) > 1:
            dupgroups.append(dict(
                title=title, year=year, n_ban_ghi=len(g), n_sources=len(srcs),
                sources="; ".join(srcs),
                dois="; ".join(sorted({r["_doi"] for r in g if r["_doi"]})),
                canh_bao_khac_doi=("yes" if len({r["_doi"] for r in g if r["_doi"]}) > 1 else ""),
                tieu_de_cac_ban=" || ".join(sorted({r["title"] for r in g}))))

    # --- ASSERT tu kiem ---------------------------------------------------------
    assert len(uniq) + n_in_pool + len(beyond) == len(groups), \
        f"Lech: {len(uniq)}+{n_in_pool}+{len(beyond)} != {len(groups)}"
    # Tieu de DAI phai duy nhat. Tieu de NGAN (<MIN_TITLE_KEY) co the trung nhau vi
    # ta CO Y khong gop chung ('Shop Talk', 'Books Reviewed' la nhung bai khac nhau).
    keyset = [k for k in (strong_key(u["title"]) for u in uniq) if len(k) >= MIN_TITLE_KEY]
    dup_long = len(keyset) - len(set(keyset))
    assert dup_long == 0, f"Con {dup_long} tieu de DAI bi trung trong danh sach duy nhat!"
    n_ngan = sum(1 for u in uniq if len(strong_key(u["title"])) < MIN_TITLE_KEY)
    doiset = [u["doi_url"] for u in uniq if u["doi_url"]]
    assert len(doiset) == len(set(doiset)), "Con DOI trung trong danh sach duy nhat!"
    print(f"ASSERT OK: {len(uniq)} duy nhat + {n_in_pool} trung pool cu + "
          f"{len(beyond)} ngoai cua so = {len(groups)} nhom | khong con trung DOI, "
          f"khong con trung tieu de dai (>={MIN_TITLE_KEY} ky tu)")
    print(f"  ({n_ngan} bai co tieu de rat ngan -> CO Y khong gop theo tieu de)")

    # --- do TRUNG GAN DUNG (tieu de lech vai ky tu -> khoa chat khong bat duoc) ------
    # Chi CANH BAO, KHONG tu gop: chia ro theo 10 ky tu dau cua khoa manh roi so
    # difflib trong tung ro; nguong 0.93. Ghi vao cot 'gan_trung_voi' de Vy tu quyet.
    import difflib
    buckets = defaultdict(list)
    for u in uniq:
        k = strong_key(u["title"])
        u["_k"] = k
        if len(k) >= 12:
            buckets[k[:10]].append(u)
    near = []
    for _, grp in buckets.items():
        if len(grp) < 2 or len(grp) > 60:            # ro qua lon -> bo qua cho nhanh
            continue
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                a, b = grp[i], grp[j]
                if a["_k"] == b["_k"]:
                    continue
                r = difflib.SequenceMatcher(None, a["_k"], b["_k"]).ratio()
                if r >= 0.93:
                    near.append((r, a, b))
    for r, a, b in near:
        a["gan_trung_voi"] = (a.get("gan_trung_voi", "") + f" | [{r:.2f}] {b['title']}").strip(" |")
        b["gan_trung_voi"] = (b.get("gan_trung_voi", "") + f" | [{r:.2f}] {a['title']}").strip(" |")
    print(f"Trung GAN DUNG (canh bao, khong tu gop): {len(near)} cap")

    uniq.sort(key=lambda u: ({"known-dataset": 0, "candidate-new": 1, "mentions-data": 2,
                              "no-data-signal": 3}[u["bucket"]], -u["n_sources"],
                             u["year"] or "0000"))
    cols = ["rec_id", "bucket", "dataset", "link_data", "link_host", "availability",
            "n_sources", "sources", "n_ban_ghi", "source_chinh", "year", "nam_khac", "era",
            "venue", "title", "doi_url", "dataset_da_biet", "dataset_ung_vien",
            "link_dang_ky", "therapy", "gan_trung_voi", "canh_bao_sieu_du_lieu",
            "decision_ta", "decision_ft", "include_group", "notes", "abstract"]
    out_csv = os.path.join(EXPORTS, "wave3_unique_for_screening.csv")
    # GIU QUYET DINH CU: quet TAT CA file sang loc wave 3 (Vy co the dien o file da
    # sap uu tien 'wave3_screening_sorted.csv' hoac o shortlist, khong chi file nay).
    # Dong nao co quyet dinh se duoc uu tien; khoa khop la tieu de chuan hoa manh.
    old = {}
    for fn in ("wave3_unique_for_screening.csv", "wave3_screening_sorted.csv",
               "wave3_shortlist_dataset.csv"):
        for r0 in read_csv_rows(os.path.join(EXPORTS, fn)):
            k = strong_key(r0.get("title", ""))
            if not k:
                continue
            co_qd = (r0.get("decision_ft") or r0.get("decision_ta") or "").strip()
            if co_qd or k not in old:
                if co_qd or not (old.get(k, {}).get("decision_ta")
                                 or old.get(k, {}).get("decision_ft")):
                    old[k] = r0
    n_keep = 0
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, u in enumerate(uniq, 1):
            o = old.get(strong_key(u["title"]), {})
            if (o.get("decision_ft") or o.get("decision_ta") or "").strip():
                n_keep += 1
            row = {c: u.get(c, "") for c in cols}
            row.update(rec_id=f"u3-{i:04d}", decision_ta=o.get("decision_ta", ""),
                       decision_ft=o.get("decision_ft", ""),
                       include_group=o.get("include_group", ""), notes=o.get("notes", ""))
            w.writerow(row)
    dup_csv = os.path.join(EXPORTS, "wave3_duplicate_groups.csv")
    dupgroups.sort(key=lambda d: (-d["n_ban_ghi"], -d["n_sources"]))
    with open(dup_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["n_ban_ghi", "n_sources", "sources", "year",
                                          "canh_bao_khac_doi", "title", "dois",
                                          "tieu_de_cac_ban"])
        w.writeheader()
        w.writerows(dupgroups)

    # --- bao cao ----------------------------------------------------------------
    c_src = Counter(u["n_sources"] for u in uniq)
    c_bucket = Counter(u["bucket"] for u in uniq)
    c_av = Counter(u["availability"] for u in uniq)
    c_host = Counter(h for u in uniq for h in u["link_host"].split("; ") if h)
    c_era = Counter(u["era"] for u in uniq if u["era"])
    n_link = sum(1 for u in uniq if u["link_data"])
    n_ds = sum(1 for u in uniq if u["dataset"])
    khac_doi = [d for d in dupgroups if d["canh_bao_khac_doi"]]

    L = [f"# Wave 3 — Danh sách bài báo DUY NHẤT sau khử trùng mạnh",
         f"\n_Chạy: {date.today()} · `wave3_unique_for_screening.csv` "
         f"({len(uniq)} bài) · nhật ký gộp: `wave3_duplicate_groups.csv`_\n",
         "## 1. Khử trùng: bài nào lặp lại ở nhiều nơi?",
         f"- Đọc vào **{len(recs)} bản ghi thô** từ {len(files)} file "
         f"({', '.join(f'{k}: {v}' for k, v in sorted(per_file.items()))})",
         f"- Gộp thành **{len(groups)} bài báo duy nhất** → loại "
         f"**{len(recs) - len(groups)} bản ghi trùng** ({(len(recs)-len(groups))*100//len(recs)}%)",
         f"- Trong đó trùng với pool cũ (wave 1/2/expert/123 bài đã chốt): **{n_in_pool}**",
         f"- Ngoài cửa sổ thời gian (năm > {CUTOFF_YEAR}): {len(beyond)}",
         f"- **Còn lại để sàng lọc: {len(uniq)} bài**\n",
         "### Mỗi bài xuất hiện ở bao nhiêu CSDL?",
         "| Số CSDL | Số bài | Ý nghĩa |", "|---|---|---|"]
    ynghia = {1: "chỉ 1 nguồn tìm thấy", 2: "2 nguồn cùng có", 3: "3 nguồn", 4: "4 nguồn",
              5: "cả 5 nguồn đều có"}
    for k in sorted(c_src):
        L.append(f"| {k} | {c_src[k]} | {ynghia.get(k, '')} |")
    L.append(f"\n- Số nhóm gộp từ ≥2 bản ghi: **{len(dupgroups)}**")
    L.append(f"- Nhóm có **DOI khác nhau** (cần chị liếc qua để chắc): **{len(khac_doi)}** "
             "— xem cột `canh_bao_khac_doi` trong `wave3_duplicate_groups.csv`")
    L.append(f"- **Trùng gần đúng** (tiêu đề lệch vài ký tự, script **không** tự gộp): "
             f"**{len(near)} cặp** — đánh dấu ở cột `gan_trung_voi` để chị tự quyết.")
    n_lech = sum(1 for u in uniq if u.get("canh_bao_sieu_du_lieu"))
    L.append(f"- **Siêu dữ liệu nguồn bị lệch**: {n_lech} nhóm có một bản ghi mang tiêu đề "
             "hoàn toàn khác các bản còn lại **dù cùng DOI** — đây là lỗi của chính CSDL "
             "(gặp ở OpenAlex: ví dụ bản ghi tên *Hymn Of Consecration* lại đeo DOI của bài "
             "*“Rate My Therapist”*). Script chọn tiêu đề theo **bỏ phiếu đa số** nên bản lệch "
             "không được lấy làm đại diện; tiêu đề lệch vẫn lưu ở cột "
             "`canh_bao_sieu_du_lieu` để chị kiểm tra.")
    L.append("\n### Ví dụ trùng mà bản khử trùng cũ BỎ SÓT (nay đã gộp)")
    L.append("| Số bản ghi | Nguồn | Các biến thể tiêu đề |")
    L.append("|---|---|---|")
    for d in dupgroups[:12]:
        bien = d["tieu_de_cac_ban"]
        L.append(f"| {d['n_ban_ghi']} | {d['sources']} | {bien[:150]} |")

    L.append(f"\n## 2. Cột `dataset` — tên bộ dữ liệu từng bài")
    L.append(f"- **{n_ds}/{len(uniq)} bài** có tên dataset nhận diện được "
             f"({n_ds*100//max(1,len(uniq))}%)")
    L.append("- Tên có hậu tố **`(?)`** = tên bộ dữ liệu trùng với từ tiếng Anh thường "
             "(CARE, PEER, HEART, SPLIT, COMPASS…). Kiểm tra tay cho thấy nhiều trường hợp "
             "viết HOA lại là **thang đo** (CARE Measure), **tên thử nghiệm** (COMPASS trial) "
             "hay **acronym khác** chứ không phải bộ dữ liệu — nên chị cần xác nhận trước khi "
             "dùng. Tên không có `(?)` thì đáng tin hơn nhiều.")
    L.append("\n| Rổ | Số bài |")
    L.append("|---|---|")
    for b in ["known-dataset", "candidate-new", "mentions-data", "no-data-signal"]:
        L.append(f"| {b} | {c_bucket.get(b, 0)} |")
    c_known = Counter(k for u in uniq for k in u["dataset_da_biet"].split("; ") if k)
    L.append(f"\n### Bộ đã biết được nhắc ({len(c_known)} bộ)")
    L.append("| Dataset | Số bài |")
    L.append("|---|---|")
    for k, v in c_known.most_common(30):
        L.append(f"| {k} | {v} |")
    c_cand = Counter(c for u in uniq for c in u["dataset_ung_vien"].split("; ") if c)
    L.append(f"\n### Tên ứng viên MỚI ({len(c_cand)} tên, top 40)")
    L.append("| Tên | Số bài |")
    L.append("|---|---|")
    for k, v in c_cand.most_common(40):
        L.append(f"| {k} | {v} |")

    n_reg = sum(1 for u in uniq if u.get("link_dang_ky"))
    n_host_biet = sum(1 for u in uniq if any(h != "khac" for h in u["link_host"].split("; ") if h))
    L.append(f"\n## 3. Cột `link_data` — link dữ liệu/mã nguồn nhắc trong bài")
    L.append(f"- **{n_link}/{len(uniq)} bài** có ít nhất 1 link "
             f"({n_link*100//max(1,len(uniq))}%), trong đó **{n_host_biet} bài** trỏ tới nơi "
             "lưu dữ liệu/mã nguồn đã biết (GitHub, Hugging Face, Zenodo, OSF…)")
    L.append(f"- Thêm **{n_reg} bài** có link **đăng ký thử nghiệm/đề cương** "
             "(ClinicalTrials, PROSPERO, ISRCTN…) — để ở cột riêng `link_dang_ky`, "
             "không tính là link dữ liệu")
    L.append("\n| Nơi lưu | Số bài |")
    L.append("|---|---|")
    for h, v in c_host.most_common():
        L.append(f"| {h} | {v} |")
    L.append("\n> Đã **loại** link giấy phép (creativecommons), nhà xuất bản "
             "(Springer/Wiley/MDPI…), hạ tầng trích dẫn (doi.org, ORCID, arXiv, ACL) và rác "
             "quảng cáo. `khac` = tên miền lạ, có thể là trang dự án riêng (ví dụ "
             "`sython.org/Corpus/STUDIES`) nên vẫn giữ để chị xem.")
    L.append("> Abstract của WoS/PubMed thường bị cắt URL nên con số này là **cận dưới** — "
             "bài không có link **chưa chắc** là không phát hành dữ liệu.")

    L.append(f"\n## 4. Tính mở/đóng")
    L.append("| Nhãn | Số bài |")
    L.append("|---|---|")
    for k, v in c_av.most_common():
        L.append(f"| {k} | {v} |")
    L.append(f"\n(có link dữ liệu ⇒ tính là `open` ngay cả khi abstract không nói câu "
             "'publicly available')")

    L.append(f"\n## 5. Ưu tiên đọc — bài có TÊN dataset VÀ link dữ liệu "
             f"({sum(1 for u in uniq if u['dataset'] and u['link_data'])} bài)")
    L.append("| Năm | Dataset | Nơi lưu | Nguồn | Tiêu đề |")
    L.append("|---|---|---|---|---|")
    for u in sorted((u for u in uniq if u["dataset"] and u["link_data"]),
                    key=lambda x: x["year"] or "0000"):
        L.append(f"| {u['year']} | {u['dataset'][:38]} | {u['link_host']} | "
                 f"{u['sources']} | {u['title'][:88]} |")

    L.append(f"\n## 6. Phân bố thời kỳ")
    L.append("| Thời kỳ | Số bài |")
    L.append("|---|---|")
    for k, v in sorted(c_era.items()):
        L.append(f"| {k} | {v} |")

    L.append("\n## 7. Cách khử trùng (để tái lập)")
    L.append("- Khóa gộp = hợp của 3 khóa, nối bằng union-find: **DOI** (chuẩn hóa, bỏ hậu tố "
             "version) · **arXiv-id** (bắt cặp preprint ↔ bản xuất bản qua DOI "
             "`10.48550/arXiv.*`) · **tiêu đề chuẩn hóa mạnh**.")
    L.append("- Tiêu đề chuẩn hóa mạnh: bỏ ngoặc nhọn BibTeX (`{PATIENT}`→`PATIENT`) → bỏ "
             "LaTeX (`$\\psi$`, `\\textbf`) → NFKD về ASCII (Ψ, dấu tiếng Việt) → bỏ **tất cả** "
             "ký tự không phải chữ-số **kể cả khoảng trắng** (`Context Word`=`ContextWord`).")
    L.append("- Đây là chỗ bản cũ (`dedup_ris.norm_title`) bỏ sót: nó giữ khoảng trắng nên "
             "`{A}rabic` → `a rabic` ≠ `arabic`, khiến bản ACL và bản OpenAlex của **cùng một "
             "bài** bị đếm thành hai.")
    L.append("- Mỗi nhóm giữ 1 dòng: đại diện là bản có DOI + abstract dài nhất; tiêu đề lấy "
             "bản sạch nhất; **abstract của cả nhóm được hợp lại** khi dò tên dataset và link "
             "(một nguồn cắt URL thì nguồn kia bù).")
    L.append("- Tự kiểm: sau khi gộp, khẳng định không còn trùng khóa tiêu đề và không còn "
             "trùng DOI trong danh sách cuối (assert trong script).")
    L.append("\n## 8. Giới hạn")
    L.append("- Tên dataset là **heuristic trên abstract**, không phải đọc toàn văn. Đã mở rộng "
             "danh sách loại trừ (Seq2Seq, ASR, TTS, CVAE, SAM, PFA… là mô hình/phương pháp, "
             "không phải dataset) nhưng vẫn có thể sót/nhầm — cột `dataset_ung_vien` cần chị "
             "xác nhận trước khi dùng.")
    L.append(f"- Một số bộ dữ liệu có tên **trùng từ tiếng Anh thường** ({', '.join(ambig_dung[:14])}"
             f"{'…' if len(ambig_dung) > 14 else ''}). Nếu tìm thường thì `peer` khớp 441 bài, "
             "`heart` 119, `split` 33 — toàn dương tính giả. Vì vậy các tên này **chỉ được tính "
             "khi viết HOA** trong văn bản. Hệ quả: có thể **bỏ sót** bài viết tên ở dạng "
             "thường; đây là đánh đổi có chủ ý, ưu tiên độ chính xác vì chị còn sàng lọc tay.")
    L.append("- Bài không có link **không** đồng nghĩa dữ liệu đóng: phần lớn abstract không "
             "nói gì về phát hành.")
    L.append("- Nhóm có `canh_bao_khac_doi=yes` là các bản ghi cùng tiêu đề nhưng DOI khác "
             "(thường là preprint ↔ bản xuất bản, hoặc bản hội nghị ↔ bản tạp chí). Script gộp "
             "chúng vì cùng một nghiên cứu; nếu chị muốn tách, lọc cột này trong file nhật ký.")

    out_md = os.path.join(NOTES, "wave3_unique_report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print(f"\n=== KET QUA ===")
    print(f"  Ban ghi tho:            {len(recs)}")
    print(f"  Bai duy nhat:           {len(groups)} (loai {len(recs)-len(groups)} trung)")
    print(f"  Trung pool cu:          {n_in_pool}")
    print(f"  CON LAI de sang loc:    {len(uniq)}")
    print(f"  Phan bo so CSDL/bai:    {dict(sorted(c_src.items()))}")
    print(f"  Co ten dataset:         {n_ds}")
    print(f"  Co link du lieu:        {n_link}  {dict(c_host.most_common(8))}")
    print(f"  Nhom gop >=2 ban ghi:   {len(dupgroups)} (khac DOI: {len(khac_doi)})")
    if n_keep:
        print(f"  (giu quyet dinh cu cho {n_keep} dong)")
    print(f"\n  CSV sang loc: {out_csv}")
    print(f"  Nhat ky gop:  {dup_csv}")
    print(f"  Bao cao:      {out_md}")


if __name__ == "__main__":
    main()
