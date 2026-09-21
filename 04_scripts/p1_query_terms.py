# -*- coding: utf-8 -*-
"""P1 — nguon su that DUY NHAT cho tu khoa (khop Supplementary S1 / P1_search_strings.md).
Ca harvest_arxiv.py va harvest_acl.py deu import tu day de arXiv/ACL nhat quan voi nhau
va voi cac chuoi truy van chay tay tren Scopus/WoS/... Ba khoi khai niem:
  A = mien tham van / SKTT ; B = hoi thoai / dataset ; C = NLP / LLM.
Vi arXiv API va regex KHONG ho tro wildcard '*', o day khai trien san cac bien the than tu."""

BLOCK_A = [
    "counseling", "counselling", "counselor", "counsellor",
    "psychotherapy", "psychotherapeutic", "psychotherapist",
    "mental health", "emotional support",
    "motivational interviewing",
    "cognitive behavioral therapy", "cognitive behavioural therapy", "CBT",
    "therapeutic alliance", "working alliance",
    "empathy", "empathetic", "empathic",
]

BLOCK_B = [
    "dialogue", "dialog", "dialogues", "dialogs",
    "conversation", "conversational", "conversations",
    "chatbot", "chatbots",
    "dialogue system", "dialog system",
    "multi-turn", "multiturn",
    "corpus", "dataset", "benchmark",
]

BLOCK_C = [
    "natural language processing", "NLP",
    "large language model", "large language models", "LLM", "LLMs",
    "language model", "language models",
    "text generation",
]

# ---- WAVE 2 (2026-07-09): mo rong dan boi hoc thuyet tri lieu ------------------
# Block A1 = ten 8 hoc thuyet + bien the (lap khoang trong DBT/ACT/IPT/MBCT/EMDR/
# tam dong hoc/than chu trong tam). Block A2 = ten thang do chuan. Wave 2 = tim
# (A1 U A2) AND B AND C, GIU B/C nhu wave 1 de dedup nhat quan. KHONG dung "ACT"/
# "WAI" tran (trung tu thuong) — chi dung cum day du.
BLOCK_A1_MODALITY = [
    "dialectical behavior therapy", "dialectical behaviour therapy", "DBT",
    "acceptance and commitment therapy",
    "interpersonal psychotherapy", "interpersonal therapy", "IPT",
    "mindfulness-based cognitive therapy", "mindfulness based cognitive therapy", "MBCT",
    "eye movement desensitization", "EMDR",
    "psychodynamic", "psychoanalytic", "psychoanalysis",
    "person-centered therapy", "person-centred therapy",
    "client-centered", "client-centred", "Rogerian",
    "behavioral activation", "behavioural activation",
    "problem-solving therapy", "solution-focused",
    "schema therapy", "compassion-focused therapy",
]
BLOCK_A2_SCALE = [
    "working alliance inventory", "Barrett-Lennard", "BLRI",
    "PHQ-9", "GAD-7", "PCL-5",
    "cognitive therapy rating scale",
    "motivational interviewing treatment integrity", "MITI",
    "motivational interviewing skill code",
]
# Cac tu viet tat de nhieu -> khi sang loc phai spot-check tieu de
NOISY_ACRONYMS = {"IPT", "DBT", "EMDR", "MITI", "BLRI"}

# arXiv categories han pham vi
ARXIV_CATS = ["cs.CL", "cs.AI", "cs.HC"]

# Cua so thoi gian (sua tai day neu doi ngay chot tim kiem)
YEAR_MIN = 2021
CUTOFF_DATE = "2026-07-09"   # ngay chot wave 2; sua cho khop last_search_date trong INPUTS
# Wave 1 da chay 2026-07-08 (BLOCK_A tong quat). Wave 2 dung BLOCK_A1_MODALITY +
# BLOCK_A2_SCALE. Xem PROMPT_survey_Q1_theory_driven.md muc 4.

# ---- WAVE 3 (2026-07-31): NLP x tham van - tri lieu, KHONG rang buoc nam ---------
# Muc tieu: bat TAT CA bai nganh NLP nghien cuu mien tham van/tri lieu tam ly,
# ke ca bai truoc 2021 (Althoff 2016, Xiao 2015, EmpatheticDialogues 2019, EPITOME
# 2020...) va bai bi wave 1 bo sot vi abstract khong chua cum khoi C hep (bai hoc tu
# citation_expert.csv: SMILE chi noi 'ChatGPT', PsyQA 2021 truoc ky nguyen LLM).
# Thiet ke: (A3 mien tham van-tri lieu) AND (C3 NLP mo rong); BO khoi B (khong doi
# hoi bai phai la dataset/hoi thoai); BO san nam (YEAR_MIN_W3=None). Rieng ACL
# Anthology: venue da la NLP -> chi can khop A3, ghi co c3_hit de doi chieu.
BLOCK_A3_THERAPY = [
    "counseling", "counselling", "counselor", "counsellor", "counselors", "counsellors",
    "psychotherapy", "psychotherapies", "psychotherapeutic",
    "psychotherapist", "psychotherapists",
    "therapist", "therapists", "therapy session", "therapy sessions",
    "talk therapy", "talking therapy",
    "motivational interviewing",
    "cognitive behavioral therapy", "cognitive behavioural therapy", "CBT",
    "dialectical behavior therapy", "dialectical behaviour therapy",
    "acceptance and commitment therapy",
    "psychodynamic", "psychoanalytic", "psychoanalysis",
    "person-centered therapy", "person-centred therapy",
    "client-centered", "client-centred", "Rogerian",
    "therapeutic alliance", "working alliance",
    "crisis intervention", "crisis line", "crisis text line",
    "emotional support", "peer support", "mental health support",
    "empathy", "empathetic", "empathic",
]
# C3 = C wave 1 + ten mo hinh/cong nghe (ChatGPT/GPT/BERT...), chatbot/agent/dialogue
# system (truoc o khoi B), va thuat ngu NLP co dien cho bai truoc-2021. KHONG dua
# "machine learning"/"neural network" tran (dinh fMRI 'neural network', ML ngoai van ban).
BLOCK_C3_NLP = [
    "natural language processing", "NLP", "computational linguistics",
    "large language model", "large language models", "LLM", "LLMs",
    "language model", "language models",
    "text generation", "text mining", "text classification",
    "sentiment analysis", "topic model", "topic modeling", "topic modelling",
    "word embedding", "word embeddings",
    "transformer", "transformers", "BERT", "GPT", "ChatGPT",
    "chatbot", "chatbots",
    "conversational agent", "conversational agents", "conversational AI",
    "dialogue system", "dialogue systems", "dialog system", "dialog systems",
    "natural language understanding", "natural language generation",
    "automatic speech recognition", "speech and language processing",
    "sequence-to-sequence", "seq2seq", "deep learning",
]
YEAR_MIN_W3 = None              # None = khong gioi han san nam (tim tu dau lich su)
CUTOFF_DATE_W3 = "2026-07-31"   # ngay chot wave 3
