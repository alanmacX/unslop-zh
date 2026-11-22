---
name: natural-tech-zh
description: Write natural, concise technical Chinese for status updates, PR descriptions, architecture notes, and reports without degrading reasoning accuracy or forcing a rigid new style. Use when drafting human-facing Chinese technical prose, summaries, release notes, or when asked to remove AI tone (de-AI) or audit Codex/LLM writing habits offline. Do not trigger during routine code editing or debugging turns.
---
# Natural Technical Chinese

Produce clear, grounded technical Chinese that adapts to each genre without hurting reasoning accuracy or trading one rigid template for another.

## When to Use

- Drafting human-facing status updates, team summaries, PR descriptions, design docs, or feature introductions in Chinese
- Rewriting stiff, jargon-heavy, or formulaic Chinese drafts into natural engineering prose
- Running an offline statistical audit on historical Codex sessions or long documents using the bundled linter script

Do not activate this skill during routine coding, shell execution, or debugging turns where speed and raw technical precision matter most.

## Core Principles

1. **Reasoning and facts always win**: Never soften a real bug, drop a number, skip a discrepancy, or hide an engineering risk just to sound casual.
2. **Adapt format to the content**: Pick the layout that fits the information instead of forcing every answer into plain paragraphs or into bullet lists.
3. **Zero online script overhead**: Generate the response in a single pass during live chat. Reserve `scripts/tic_lint.py` for offline audits of long documents or historical logs, never as a mandatory loop on every chat reply.

## Genre-Adaptive Writing Steps

### 1. Short Status Updates and Feature Intros (Under 250 Chinese Characters)

- Lead with the single most concrete outcome or change in plain text (no bold verdict line at the top).
- Group related facts into 1 to 2 natural paragraphs. Split distinct topics into separate paragraphs (for example, test results in paragraph 1 and remaining batch progress in paragraph 2, or user workflow in paragraph 1 and backend validation in paragraph 2).
- Use concrete verbs and objects instead of product-brochure framing (describe what a person actually does rather than listing abstract capabilities).

### 2. Multi-Dimensional Comparisons, Debug Steps, and Long Checklists

- Use a Markdown table or clean numbered/bulleted list whenever comparing 3+ dimensions or walking through ordered steps.
- State the concrete point directly in each item. Avoid wrapping every bullet in a uniform `**Four-Char Label**: ...` shell or padding lists to hit 3 or 4 items.

### 3. Technical Disagreements and Pushback

- State the contradiction, evidence, and next check plainly.
- Skip flattery, performative apologies, and artificial warmth.

### 4. Replace Pseudo-Professional Jargon and Rhythm Tells

- Replace abstract corporate-engineering buzzwords with the actual code object or action (see `references/jargon-map.md` for common mappings).
- Avoid chaining 3+ items with `、` in a single clause or stuffing trailing caveats after a semicolon at the end of a paragraph.
- Vary sentence length naturally instead of forcing either clipped one-clause periods or run-on comma chains.

## Offline Regression Audit (Optional)

To audit a saved document or sample historical Codex replies offline without slowing down live turns, run:

```bash
python3 scripts/tic_lint.py path/to/draft.md
```

Use the output metrics (blind `p_ai`, comma-to-period ratio, `、` density, punctuation entropy, Markdown density, and jargon hits) as a diagnostic compass to spot drift over time, not as a score to game by replacing every period with a comma.

## Gotchas

- **Do not over-correct into comma chains**: Removing bullets and `、` should produce readable sentences, not a single run-on paragraph glued together with commas.
- **Do not fake enthusiasm**: Avoid stock casual openers or forced exclamations; aim for a calm, sharp engineering peer.
- **Keep tables when tables help**: If a prompt asks to compare multiple systems across multiple dimensions, a concise table is clearer than prose.
