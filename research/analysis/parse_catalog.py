"""Parse VinUni curriculum framework text (pypdf output) -> course records.
Usage: python -I parse_catalog.py <text_file> <out.json>
Heuristic parser; output MUST be human-reviewed (see prereq_raw)."""
import re, sys, json
HDR = re.compile(r'^([A-Z]{3,4}\d{4}(?:/\d+)?)\s+(.*\S)\s*$')
CRED = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*credits?\b', re.I)
PRE  = re.compile(r'^\s*Pre-?requisites?\s*(?:/\s*\w+)?\s*:?\s*(.*)$', re.I)

def parse(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    start = max(i for i, l in enumerate(lines) if re.match(r'\s*3\.4\.?\s+Course Descriptions', l))
    out, i = [], start + 1
    while i < len(lines):
        m = HDR.match(lines[i])
        if m:
            # lookahead window to confirm header (a "N credits" line within 3 lines)
            win = lines[i+1:i+4]
            ci = next((k for k, l in enumerate(win) if CRED.match(l)), None)
            if ci is not None:
                code, name = m.group(1), m.group(2)
                name = (name + ' ' + ' '.join(w.strip() for w in win[:ci])).strip()
                cr = float(CRED.match(win[ci]).group(1))
                j = i + 2 + ci
                pre = None
                for k in range(j, min(j + 4, len(lines))):
                    pm = PRE.match(lines[k])
                    if pm:
                        txt = pm.group(1).strip()
                        # continuation lines until blank or sentence-ish end
                        n = k + 1
                        while n < len(lines) and txt and not re.search(r'[.]\s*$', txt) and lines[n].strip() and not lines[n].startswith('==='):
                            if len(txt) > 160: break
                            txt += ' ' + lines[n].strip(); n += 1
                        if not txt and k + 1 < len(lines):
                            txt = lines[k+1].strip()
                        pre = re.sub(r'\s+', ' ', txt); break
                out.append({'code': code, 'name': re.sub(r'\s+', ' ', name), 'credits': cr, 'prereq_raw': pre})
        i += 1
    return out

if __name__ == '__main__':
    d = parse(sys.argv[1]); json.dump(d, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(d), 'courses;', sum(1 for v in d if v['prereq_raw'] is None), 'without prereq line;', len(d)-len({v['code'] for v in d}), 'duplicate codes')
