#!/usr/bin/env python3
import sys, os, re, math, zlib, json
from collections import Counter

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, 'model_params.json'), 'r', encoding='utf-8') as f:
    MODEL = json.load(f)

ZH_RE = re.compile(r'[\u4e00-\u9fff]')
CLAUSE_SPLIT_RE = re.compile(r'[，,。！？!?；;：\n]+')
SENT_SPLIT_RE = re.compile(r'[。！？!?\n]+')
PUNCT_RE = re.compile(r'[，。；：、！？—（）“”「」\n]')
LIGHT_VERB_RE = re.compile(r'进行|实现|提供|支持|确保|保持|完成|处理|避免|通过|基于|针对|用于|需要')
JARGON_RE = re.compile(r'对齐|口径|收敛|链路|闭环|兜底|边界|基线|维度|颗粒度|范式|治理|落地|打通|拉通|沉淀|赋能|抓手|心智|体系|一致性|鲁棒|契约|显式|隐式|形态|可观测|侧')

def burstiness(vals):
    if len(vals) < 3: return 0.0
    m = sum(vals) / len(vals)
    if m <= 0: return 0.0
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))
    return (sd - m) / (sd + m)

def shannon_entropy(counter):
    tot = sum(counter.values())
    if tot == 0: return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counter.values())

def yules_k(chars):
    N = len(chars)
    if N < 10: return 0.0
    freq = Counter(chars)
    return 10000.0 * (sum(v * v for v in freq.values()) - N) / (N * N)

def evaluate(prose):
    zh_chars = ZH_RE.findall(prose)
    n_zh = max(1, len(zh_chars))
    k_zh = n_zh / 1000.0
    clauses = [len(ZH_RE.findall(c)) for c in CLAUSE_SPLIT_RE.split(prose) if len(ZH_RE.findall(c)) >= 2]
    sents = [len(ZH_RE.findall(s)) for s in SENT_SPLIT_RE.split(prose) if len(ZH_RE.findall(s)) >= 3]
    clause_mean = sum(clauses) / max(1, len(clauses))
    clause_burst = burstiness(clauses)
    sent_burst = burstiness(sents)
    slice_txt = prose[:300].encode('utf-8')
    comp_ratio = len(zlib.compress(slice_txt, level=6)) / max(1, len(slice_txt))
    sub_zh = zh_chars[:200]
    char_ent = shannon_entropy(Counter(sub_zh))
    yk = yules_k(sub_zh)
    de_d = prose.count('的') / k_zh
    lv_d = len(LIGHT_VERB_RE.findall(prose)) / k_zh
    comma_d = (prose.count('，') + prose.count(',')) / k_zh
    period_d = prose.count('。') / k_zh
    semi_d = prose.count('；') / k_zh
    colon_d = (prose.count('：') + prose.count(':')) / k_zh
    enum_d = prose.count('、') / k_zh
    punct_ent = shannon_entropy(Counter(PUNCT_RE.findall(prose)))
    md_d = (prose.count('**') + prose.count('\n-') + prose.count('\n1.') + prose.count('\n#')) / k_zh
    expr_d = (prose.count('？') + prose.count('?') + prose.count('！') + prose.count('!')) / k_zh

    vec = [clause_mean, clause_burst, sent_burst, comp_ratio, char_ent, yk, de_d, lv_d,
           comma_d, period_d, semi_d, colon_d, enum_d, punct_ent, md_d, expr_d]
    means, stds, w, b = MODEL['means'], MODEL['stds'], MODEL['w'], MODEL['b']
    z = max(-20.0, min(20.0, b + sum(w[d] * ((vec[d] - means[d]) / stds[d]) for d in range(len(w)))))
    p_ai = 1.0 / (1.0 + math.exp(-z))

    cp_ratio = comma_d / max(1.0, period_d)
    jargon = JARGON_RE.findall(prose)
    alerts = []
    if md_d > 10: alerts.append(f"Markdown排版过重(md={md_d:.1f}，请去掉加粗/列表改自然段)")
    if enum_d > 8: alerts.append(f"顿号连珠(、={enum_d:.1f}/千字，请拆成逗号或用和/跟连接)")
    if punct_ent > 1.65: alerts.append(f"标点高熵割裂(H={punct_ent:.2f}，减少冒号/分号/换行)")
    if cp_ratio < 2.2: alerts.append(f"句号过密像点射(逗句比={cp_ratio:.2f}，多用逗号连贯说完)")
    if jargon: alerts.append(f"伪专业词({len(jargon)}处: {','.join(set(jargon))})")
    if lv_d > 12: alerts.append(f"虚化动词偏多({lv_d:.1f}/千字)")
    if p_ai >= 0.45: alerts.append(f"综合统计学AI味过高(P_AI={p_ai:.3f} >= 0.45)")

    return {
        'pass': len(alerts) == 0,
        'p_ai': round(p_ai, 4),
        'comma_period_ratio': round(cp_ratio, 2),
        'enum_density': round(enum_d, 1),
        'punct_entropy': round(punct_ent, 3),
        'md_density': round(md_d, 1),
        'jargon_count': len(jargon),
        'alerts': alerts
    }

if __name__ == '__main__':
    txt = sys.stdin.read().strip() if len(sys.argv) < 2 else open(sys.argv[1], 'r', encoding='utf-8').read().strip()
    res = evaluate(txt)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res['pass'] else 1)
