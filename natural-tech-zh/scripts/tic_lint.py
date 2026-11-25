#!/usr/bin/env python3
import sys, os, re, math, zlib, json, argparse
from collections import Counter

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, 'model_params.json'), 'r', encoding='utf-8') as f:
    MODEL = json.load(f)

CODE_BLOCK_RE = re.compile(r'```[\s\S]*?```')
INLINE_CODE_RE = re.compile(r'`[^`\n]+`')
ZH_RE = re.compile(r'[\u4e00-\u9fff]')
CLAUSE_SPLIT_RE = re.compile(r'[，,。！？!?；;：\n]+')
SENT_SPLIT_RE = re.compile(r'[。！？!?\n]+')
PUNCT_RE = re.compile(r'[，。；：、！？—（）“”「」\n]')
LIGHT_VERB_RE = re.compile(r'进行|实现|提供|支持|确保|保持|完成|处理|避免|通过|基于|针对|用于|需要')

# Non-spatial "-side" calques (excludes spatial 左/右/两/内/外/上/下/单/双/同/对/哪/各/东/南/西/北 and on-device 端侧)
NON_SPATIAL_SIDE_RE = re.compile(
    r'(?:调用|消费|生产|代码|实现|浏览器|渲染|宿主|运行时|编译|构建|服务端|前端|客户端|'
    r'业务|用户|模型|数据|系统|存储|接口|产物|入口|出口|网关|网络|数据库|缓存|代理|容器|节点|集群|上游|下游|真机)侧|'
    r'(?:主动|被动|发送|接收|发起|关闭|读取|写入|请求|响应)[^，。]{0,6}的一侧'
)

# Tier 1: High-precision Agent calques, melodrama, generic CYA boilerplate & chatbait
TIER1_SLOP_RE = re.compile(
    r'最小闭环|完整闭环|已闭环|闭环验证|逻辑收口|权限收口|入口收口|一起收口|已收口|'
    r'已落盘|技术底座|数字化底座|建基线|建立基线|记录基线|保留[^，。]{0,6}基线|'
    r'(?:数据|接口|返回|参数|产物|目标|代码)形态|'
    r'静默吞掉|静默吞错|静默失败|静默降级|外科手术式|最小侵入|零侵入|'
    r'爆炸半径|自伤陷阱|承重逻辑|承重墙|一等公民|'
    r'破案了|罪魁祸首|水落石出|你说得对|非常敏锐|'
    r'如果你愿意|要是你愿意|需要我顺手|我可以顺手帮|如需复测[，,]?可以补一套|后续可补一套|'
    r'尚未全面验证|尚未覆盖全量|不能保证(?:全量|完全)?无误|不能据此宣称|全量[^，。]{0,6}仍需[^，。]{0,8}(?:观察|确认)|仍需在线上(?:进一步)?观察确认|'
    r'全程(?:保持)?只读|保持外部调用代码只读|只读查看了|不污染工作区|不污染项目|把猜测当根因|'
    r'不是简单的|不是单纯的|赋能|抓手|组合拳|心智|颗粒度|打平|抹平'
)

# Tier 2: Compensatory drift words (alert only when stacked densely)
TIER2_DRIFT_RE = re.compile(
    r'收敛到|收敛成|收敛为|收敛突发|口径|基线|已对齐|已经对齐|对齐到|语义对齐|字段对齐|'
    r'兜底|优雅降级|主链路|全链路|完整链路|核心链路|'
    r'收紧|放宽|显式[传设标保使委调]|单一事实源|唯一真值|'
    r'职责边界|语义边界|能力边界|打通|贯通'
)

# GPT English-AST Translationese syntactic markers
TRANSLATIONESE_PATTERNS = [
    ('句首无生命“它”主语', re.compile(r'(?:^|[。！？\n]\s*)它(?:限制|决定|允许|表示|说明|意味|会让|可能|用于|负责|提供|支持|把|将)')),
    ('西式使役/直译量词(“这会让/这会导致/保留零条”)', re.compile(r'这会让|这会导致|保留零[条个项次]')),
    ('句首“也+动词”/无生命“它们的”直译', re.compile(r'(?:^|[。！？\n]\s*)也(?:检查|核对|查看|确认|排查)|，以及它们的')),
    ('英文介词/被动直译(“来自…/就会被…/由…导致”) ', re.compile(r'(?:延迟|耗时|尖峰|毛刺|报错|压力|故障|开销)来自|(?:一旦|空闲|用完|超时)[^，。]{0,8}就会被(?:关闭|丢弃|回收|清理|释放)|(?:异常|报错|错误|问题)由[^，。]{1,24}(?:吞掉|导致|引起)')),
    ('动宾名词化臃肿(“承担…的读写/增加…的负担”)', re.compile(r'(?:承担|负责)[^，。]{1,12}的(?:存储|读取|读写|解析|校验|转发|分发|调度)|增加[^，。]{1,16}的(?:工作|负担|复杂度)')),
    ('列表粗体句号头/全角空格头(“- **标题**。”/“- **标题**　”)', re.compile(r'(?:^|\n)[ \t]*(?:[-*+]|\d+\.)[ \t]+(?:\*\*[^*\n]{2,24}[。.]\*\*|\*\*[^*\n]{2,24}\*\*(?:。|\u3000))')),
]

STUB_STEP_PERIOD_RE = re.compile(r'(?:^|\n)[ \t]*\d+\.[ \t]+[^*\n，。：:；;]{3,11}。[ \t]*\S')

SCARE_QUOTE_RE = re.compile(r'(?:“[\u4e00-\u9fff]{2,8}”|「[\u4e00-\u9fff]{2,8}」)')
ENUM_CHAIN_RE = re.compile(r'[\u4e00-\u9fffA-Za-z0-9_]+、[\u4e00-\u9fffA-Za-z0-9_]+、[\u4e00-\u9fffA-Za-z0-9_]+、')
SEMI_TAIL_RE = re.compile(r'；\s*(?:但|不过|目前|尚未|需要注意|仍需)')
BULLET_LINE_RE = re.compile(r'^[ \t]*(?:[-*+]|\d+\.)[ \t]+(.+)$', re.MULTILINE)
BOLD_SHELL_RE = re.compile(r'^\*\*[^*]{2,16}\*\*[：:]')
INLINE_ENG_TIC_RE = re.compile(r'[\u4e00-\u9fff]\s*`?(?:smoke(?:\s+test)?|fallback|guard|sanity\s+check|no-op|footgun|blast\s+radius)`?\s*[\u4e00-\u9fff]', re.IGNORECASE)

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

def detect_genre(raw_text, n_zh):
    has_headings = bool(re.search(r'^#{1,4}\s+\S', raw_text, re.MULTILINE))
    has_table = bool(re.search(r'^\|.+\|\s*$', raw_text, re.MULTILINE))
    if has_headings or has_table or n_zh >= 450:
        return 'doc'
    return 'chat'

def evaluate(raw_prose, genre='auto'):
    prose = CODE_BLOCK_RE.sub(' ', raw_prose)
    prose_no_code = INLINE_CODE_RE.sub(' ', prose)
    zh_chars = ZH_RE.findall(prose_no_code)
    n_zh = max(1, len(zh_chars))
    k_zh = n_zh / 1000.0
    resolved_genre = detect_genre(raw_prose, n_zh) if genre == 'auto' else genre

    clauses = [len(ZH_RE.findall(c)) for c in CLAUSE_SPLIT_RE.split(prose_no_code) if len(ZH_RE.findall(c)) >= 2]
    sents = [len(ZH_RE.findall(s)) for s in SENT_SPLIT_RE.split(prose_no_code) if len(ZH_RE.findall(s)) >= 3]
    clause_mean = sum(clauses) / max(1, len(clauses))
    clause_burst = burstiness(clauses)
    sent_burst = burstiness(sents)
    slice_txt = prose_no_code[:300].encode('utf-8')
    comp_ratio = len(zlib.compress(slice_txt, level=6)) / max(1, len(slice_txt))
    sub_zh = zh_chars[:200]
    char_ent = shannon_entropy(Counter(sub_zh))
    yk = yules_k(sub_zh)
    de_d = prose_no_code.count('的') / k_zh
    lv_d = len(LIGHT_VERB_RE.findall(prose_no_code)) / k_zh
    comma_d = (prose_no_code.count('，') + prose_no_code.count(',')) / k_zh
    period_d = prose_no_code.count('。') / k_zh
    semi_d = prose_no_code.count('；') / k_zh
    colon_d = (prose_no_code.count('：') + prose_no_code.count(':')) / k_zh
    enum_d = prose_no_code.count('、') / k_zh
    punct_ent = shannon_entropy(Counter(PUNCT_RE.findall(prose_no_code)))
    md_d = (prose.count('**') + prose.count('\n-') + prose.count('\n1.') + prose.count('\n#')) / k_zh
    expr_d = (prose_no_code.count('？') + prose_no_code.count('?') + prose.count('！') + prose.count('!')) / k_zh

    vec = [clause_mean, clause_burst, sent_burst, comp_ratio, char_ent, yk, de_d, lv_d,
           comma_d, period_d, semi_d, colon_d, enum_d, punct_ent, md_d, expr_d]
    means, stds, w, b = MODEL['means'], MODEL['stds'], MODEL['w'], MODEL['b']
    z = max(-20.0, min(20.0, b + sum(w[d] * ((vec[d] - means[d]) / stds[d]) for d in range(len(w)))))
    chat_p_ai = 1.0 / (1.0 + math.exp(-z))

    cp_ratio = comma_d / max(1.0, period_d)
    tier1_hits = TIER1_SLOP_RE.findall(prose_no_code) + NON_SPATIAL_SIDE_RE.findall(prose_no_code) + INLINE_ENG_TIC_RE.findall(prose)
    tier2_hits = TIER2_DRIFT_RE.findall(prose_no_code)
    tier2_d = len(tier2_hits) / k_zh

    trans_hits = []
    for label, rx in TRANSLATIONESE_PATTERNS:
        found = rx.findall(prose if '粗体' in label else prose_no_code)
        if found:
            trans_hits.extend(f"{label}:{m.strip()}" for m in found)
    stub_steps = STUB_STEP_PERIOD_RE.findall(prose_no_code)
    if len(stub_steps) >= 3:
        trans_hits.extend(f"步骤开头短促句号头:{s.strip()[:-1].strip()}" for s in stub_steps)

    scare_quotes = SCARE_QUOTE_RE.findall(prose_no_code)
    quote_d = len(scare_quotes) / k_zh
    enum_chains = len(ENUM_CHAIN_RE.findall(prose_no_code))
    semi_tails = len(SEMI_TAIL_RE.findall(prose_no_code))

    bullets = BULLET_LINE_RE.findall(prose)
    bold_shells = sum(1 for item in bullets if BOLD_SHELL_RE.search(item.strip()))
    bold_shell_ratio = (bold_shells / len(bullets)) if bullets else 0.0

    paras = [p.strip() for p in re.split(r'\n\s*\n', prose_no_code) if len(ZH_RE.findall(p)) >= 12]
    openers = [''.join(ZH_RE.findall(p)[:3]) for p in paras if len(ZH_RE.findall(p)) >= 3]
    opener_counts = Counter(openers)
    rep_opener = opener_counts.most_common(1)[0] if opener_counts else ('', 0)

    n_periods = prose_no_code.count('。')
    alerts = []
    if tier1_hits:
        uniq_t1 = sorted(set(h.strip() for h in tier1_hits))
        alerts.append(f"命中AI口癖或生硬黑话({len(tier1_hits)}处: {', '.join(uniq_t1[:8])})")
    if trans_hits:
        alerts.append(f"命中英文句法直译痕迹({len(trans_hits)}处: {', '.join(trans_hits[:5])})")
    if n_periods >= 5 and cp_ratio < 1.35:
        alerts.append(f"短句切分过碎(逗句比={cp_ratio:.2f} < 1.35，同一因果或动作链建议用逗号顺接)")
    if len(tier2_hits) >= 3 and tier2_d > 6.5:
        uniq_t2 = sorted(set(tier2_hits))
        alerts.append(f"空泛套话密度偏高({tier2_d:.1f}/千字: {', '.join(uniq_t2[:6])})")
    if len(scare_quotes) >= 3 and quote_d > 12.0:
        alerts.append(f"普通词双引号偏密({len(scare_quotes)}处, {quote_d:.1f}/千字)")
    if (len(bullets) >= 5 and bold_shell_ratio >= 0.8) or (resolved_genre == 'chat' and n_zh < 240 and len(bullets) >= 3 and bold_shell_ratio >= 0.75):
        alerts.append(f"列表普遍套用加粗小标题({bold_shells}/{len(bullets)}项以 **标签**： 开头)")
    if len(paras) >= 4 and rep_opener[1] >= 3 and rep_opener[1] / len(paras) >= 0.6:
        alerts.append(f"段落开头句式重复({rep_opener[1]}/{len(paras)}段均以「{rep_opener[0]}…」开头)")
    if enum_chains >= 2:
        alerts.append(f"单句四项以上顿号并列({enum_chains}处)")
    if semi_tails >= 2:
        alerts.append(f"段尾分号接转折或免责({semi_tails}处)")

    if resolved_genre == 'chat':
        if prose_no_code.count('，') >= 12 and cp_ratio > 12.0:
            alerts.append(f"单句逗号过长缺少断句(逗句比={cp_ratio:.2f})")
        if n_zh < 220 and md_d > 28:
            alerts.append(f"短回复排版过重(md={md_d:.1f}/千字)")

    return {
        'pass': len(alerts) == 0,
        'genre': resolved_genre,
        'zh_chars': n_zh,
        'tier1_slop_count': len(tier1_hits),
        'translationese_count': len(trans_hits),
        'tier2_drift_density': round(tier2_d, 2),
        'scare_quote_density': round(quote_d, 2),
        'bold_shell_ratio': round(bold_shell_ratio, 2),
        'comma_period_ratio': round(cp_ratio, 2),
        'enum_density': round(enum_d, 1),
        'md_density': round(md_d, 1),
        'chat_register_p_ai': round(chat_p_ai, 4),
        'alerts': alerts
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Offline diagnostic linter for Chinese AI-Agent slop & GPT translationese.')
    parser.add_argument('file', nargs='?', help='Markdown or text file to audit (reads stdin if omitted)')
    parser.add_argument('--genre', choices=['auto', 'chat', 'doc'], default='auto', help='Document genre')
    args = parser.parse_args()
    txt = sys.stdin.read().strip() if not args.file else open(args.file, 'r', encoding='utf-8').read().strip()
    res = evaluate(txt, genre=args.genre)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res['pass'] else 1)
