import csv
for fp in ['output/board_basler_fg_hub.csv', 'output/board_euresys_frame_grabbers.csv']:
    with open(fp, encoding='utf-8-sig', errors='ignore') as f:
        rows = list(csv.DictReader(f))
    print(f'\n=== {fp} (총 {len(rows)}행) ===')
    r = rows[0]
    for k, v in r.items():
        if v and v.strip():
            print(f'  {k}: {v[:80]}')