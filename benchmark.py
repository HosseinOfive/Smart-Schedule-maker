"""
Mini evaluation harness for Smart Schedule Maker.

Compares, on the same calendar and goal:
  - mode "full":  send the whole calendar (busy events) to the LLM  (the original approach)
  - mode "slots": send only pre-computed free slots, capped at 15   (the current approach)
across one or more models, repeated N times each.

For every call it records tokens, latency and cost, and runs deterministic pass/fail checks:
  parse_ok      - output parsed into the ScheduleResponse Pydantic schema
  count_ok      - number of activities == --expected
  in_free_time  - every activity lies fully inside real free time (no clash with fixed events)
  commute_ok    - no activity flagged "Impossible" by the 15-min commute check
  PASS          - all of the above

Usage (from the repo root):
  python -m benchmark path/to/calendar.ics
  python -m benchmark cal.ics --runs 5 --models gemini-2.5-flash gemini-2.5-flash@think0 --expected 3 \
      --goal "Schedule 3 study sessions for Data Structures and Algorithms this week"

A model name ending in "@think0" runs that model with thinking turned off (thinking_budget=0).

Prices are USD per 1M tokens (Gemini API, standard tier). Check ai.google.dev pricing before quoting.
"""
import argparse, asyncio, csv, json, statistics, time
from datetime import datetime
from dotenv import load_dotenv
from dateutil import parser as dtp
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser

from backend.ics_core.CONSTANTS import TARGET_TZ
from backend.ics_core.schemas import ScheduleResponse
from backend.ics_core.time_engine import TimeEngine
from backend.services.parser_service import parse_ics_file
from backend.services.geo_mock import merge_and_validate_mock

PRICES = {  # (input, output) USD per 1M tokens; thinking tokens bill as output
    "gemini-2.5-flash": (0.30, 2.50),
}
SLOT_CAP = 15

load_dotenv("backend/.env")
load_dotenv()


def build_prompt(mode, events, slots, goal, fmt, today):
    if mode == "slots":
        context = "AVAILABLE FREE TIME SLOTS (JSON):\n" + json.dumps(
            [s.model_dump(mode="json") for s in slots])
        rule = "Do not invent time slots. Use ONLY the start/end times provided."
    else:
        context = ("THE USER'S CALENDAR (JSON). These are busy times; the user is free otherwise "
                   "between 08:00 and 22:00 (America/Toronto):\n"
                   + json.dumps([e.model_dump(mode="json") for e in events]))
        rule = "Do not overlap any existing event. Only schedule between 08:00 and 22:00."
    return f"""You are an expert AI Scheduler.

TODAY'S DATE: {today} (timezone America/Toronto)
USER GOAL: "{goal}"

{context}

INSTRUCTIONS:
1. Analyze the user's goal (e.g., frequency, preferred times).
2. Select the BEST times for the requested activities.
3. CRITICAL: {rule}
4. Return the output strictly as a JSON object.

{fmt}"""


def to_tz(s):
    dt = dtp.isoparse(s)
    return TARGET_TZ.localize(dt) if dt.tzinfo is None else dt.astimezone(TARGET_TZ)


def text_of(msg):
    c = msg.content
    if isinstance(c, list):
        return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c)
    return c


def check(result, fixed_events, all_free, expected):
    acts = result.scheduled_activities
    count_ok = len(acts) == expected
    in_free = True
    for a in acts:
        s, e = to_tz(a.start_time), to_tz(a.end_time)
        if not (s < e and any(f.start_time <= s and e <= f.end_time for f in all_free)):
            in_free = False
    merged = merge_and_validate_mock(fixed_events, result)
    commute_ok = not any(m.type == "suggested" and m.validation_status == "Impossible" for m in merged)
    return count_ok, in_free, commute_ok


async def one_call(llm, prompt, parser):
    t0 = time.perf_counter()
    msg = await llm.ainvoke(prompt)
    latency = time.perf_counter() - t0
    u = msg.usage_metadata or {}
    inp = u.get("input_tokens", 0)
    out = u.get("total_tokens", inp) - inp  # includes thinking tokens (billed as output)
    try:
        result = parser.parse(text_of(msg))
    except Exception:
        result = None
    return result, inp, out, latency


def pct(values, q):
    if len(values) < 2:
        return values[0] if values else 0.0
    return statistics.quantiles(values, n=100, method="inclusive")[q - 1]


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ics")
    ap.add_argument("--goal", default="Schedule 3 study sessions for Data Structures and Algorithms this week")
    ap.add_argument("--expected", type=int, default=3)
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--models", nargs="+", default=["gemini-2.5-flash", "gemini-2.5-flash@think0"])
    ap.add_argument("--modes", nargs="+", default=["full", "slots"])
    ap.add_argument("--pause", type=float, default=4.0, help="seconds between calls (free-tier rate limits)")
    args = ap.parse_args()

    events = parse_ics_file(open(args.ics, encoding="utf-8").read())
    all_free = TimeEngine.calc_free_time(events)
    slots = all_free[:SLOT_CAP]
    if not slots:
        raise SystemExit("No free slots found - check the .ics file and its dates.")
    # Fair comparison: give "full" mode the same days the capped slots cover.
    lo, hi = slots[0].start_time.date(), slots[-1].end_time.date()
    window_events = [e for e in events if lo <= e.start_time.date() <= hi]

    parser = PydanticOutputParser(pydantic_object=ScheduleResponse)
    fmt = parser.get_format_instructions()
    today = datetime.now(TARGET_TZ).date().isoformat()
    rows = []

    for model in args.models:
        base, _, variant = model.partition("@")
        extra = {"thinking_budget": 0} if variant == "think0" else {}
        llm = ChatGoogleGenerativeAI(model=base, temperature=0.2, **extra)
        p_in, p_out = PRICES.get(base, (0.0, 0.0))
        for mode in args.modes:
            prompt = build_prompt(mode, window_events, slots, args.goal, fmt, today)
            for i in range(args.runs):
                try:
                    result, inp, out, lat = await one_call(llm, prompt, parser)
                except Exception as e:
                    print(f"  {model} {mode} run {i+1}: API error {e}")
                    continue
                parse_ok = result is not None
                count_ok = in_free = commute_ok = False
                if parse_ok:
                    count_ok, in_free, commute_ok = check(result, events, all_free, args.expected)
                cost = inp / 1e6 * p_in + out / 1e6 * p_out
                rows.append(dict(model=model, mode=mode, run=i + 1, input_tokens=inp, output_tokens=out,
                                 latency_s=round(lat, 2), cost_usd=cost, parse_ok=parse_ok, count_ok=count_ok,
                                 in_free_time=in_free, commute_ok=commute_ok,
                                 PASS=parse_ok and count_ok and in_free and commute_ok))
                print(f"  {model:22} {mode:5} run {i+1}: in={inp} out={out} {lat:.1f}s "
                      f"{'PASS' if rows[-1]['PASS'] else 'FAIL'}")
                await asyncio.sleep(args.pause)

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"benchmark_{stamp}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())) if rows else None
        if w:
            w.writeheader(); w.writerows(rows)

    print(f"\nCalendar: {len(events)} events | free slots: {len(all_free)} (sent {len(slots)}) | "
          f"'full' mode sends {len(window_events)} events from {lo} to {hi}\n")
    hdr = (f"{'model':22} {'mode':5} {'n':>2} {'pass':>6} {'in tok':>7} {'out tok':>7} {'p50 s':>6} {'p95 s':>6} "
           f"{'$/call':>9} {'$/1k calls':>10}  failures")
    print(hdr); print("-" * len(hdr))
    for model in args.models:
        for mode in args.modes:
            r = [x for x in rows if x["model"] == model and x["mode"] == mode]
            if not r:
                continue
            lat = [x["latency_s"] for x in r]
            cpc = statistics.mean(x["cost_usd"] for x in r)
            # how many runs failed each check, e.g. "in_free_time:2 commute_ok:1"
            fails = " ".join(f"{k}:{n}" for k in ("parse_ok", "count_ok", "in_free_time", "commute_ok")
                             if (n := sum(not x[k] for x in r))) or "-"
            print(f"{model:22} {mode:5} {len(r):>2} {sum(x['PASS'] for x in r)/len(r):>6.0%} "
                  f"{statistics.mean(x['input_tokens'] for x in r):>7.0f} {statistics.mean(x['output_tokens'] for x in r):>7.0f} "
                  f"{pct(lat, 50):>6.1f} {pct(lat, 95):>6.1f} {cpc:>9.5f} {cpc*1000:>10.2f}  {fails}")
    print(f"\nRaw results saved to benchmark_{stamp}.csv")


if __name__ == "__main__":
    asyncio.run(main())