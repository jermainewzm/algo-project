# IS115 Project: Last-Mile Delivery Planning (G1T1)

Dispatch policies for a last-mile delivery simulator, evaluated on 20 days of historical data.

## Requirements
- Python 3.9+
- Standard library only (no installs needed)
- Run all commands from the project root
- On Windows, use `python` instead of `python3`

## Policies

| Policy | Module | Description |
|---|---|---|
| Baseline | `solution.policies.baseline` | FIFO (provided, unchanged) |
| EDF 1-pass (variant) | `solution.policies.window_priority_1pass` | Earliest deadline first, single pass, no arrival-time check |
| Policy 1: EDF | `solution.policies.window_priority_2pass` | Earliest deadline first using a min-heap; pass 1 = on-time parcels, pass 2 = fill spare capacity |
| Policy 2: NN | `solution.policies.nearest_neighbour` | Nearest Neighbour (Greedy 1) routing; ignores delivery windows |
| Policy 3: WA-NN (recommended) | `solution.policies.nearest_neighbour_window` | Nearest Neighbour with per-parcel window check; pass 1 = on-time, pass 2 = late; early parcels held back |

## 1. Run one policy for one day

```
python3 -m simulator --policy solution.policies.nearest_neighbour_window --data data --day day_001 --output results/nearest_neighbour_window/day_001
python3 -m solution.performance_monitor --data data --day day_001 --log results/nearest_neighbour_window/day_001/log.txt
```

The simulator writes `log.txt`; the performance monitor writes `metrics.json` next to it.
Replace `nearest_neighbour_window` with any module name from the table above.

## 2. Reproduce all results (all policies, all 20 days)

Mac/Linux:
```
for policy in baseline window_priority_1pass window_priority_2pass nearest_neighbour nearest_neighbour_window; do
  for i in $(seq -f "%03g" 1 20); do
    python3 -m simulator --policy solution.policies.$policy --data data --day day_$i --output results/$policy/day_$i
    python3 -m solution.performance_monitor --data data --day day_$i --log results/$policy/day_$i/log.txt
  done
done
```

Windows (PowerShell):
```
foreach ($policy in "baseline","window_priority_1pass","window_priority_2pass","nearest_neighbour","nearest_neighbour_window") {
  foreach ($i in 1..20) {
    $day = "day_{0:D3}" -f $i
    python -m simulator --policy solution.policies.$policy --data data --day $day --output results/$policy/$day
    python -m solution.performance_monitor --data data --day $day --log results/$policy/$day/log.txt
  }
}
```

## 3. Average results over 20 days

```
python3 solution/summarise_results.py nearest_neighbour_window
```

Replace `nearest_neighbour_window` with any policy folder name in `results/`.

### Expected results (mean over 20 days)

| Policy | On-time rate | Delivery rate | Avg lateness | Early | Late | Undelivered | Trips |
|---|---|---|---|---|---|---|---|
| baseline | 27.4% | 40.5% | 214 min | 0 | 104 | 472 | 20.7 |
| window_priority_1pass | 18.0% | 52.3% | 136 min | 0 | 272 | 378 | 21.3 |
| window_priority_2pass | 40.3% | 46.1% | 271 min | 0 | 46 | 428 | 20.8 |
| nearest_neighbour | 64.0% | 95.9% | 49 min | 145 | 108 | 32 | 33.9 |
| nearest_neighbour_window | 80.0% | 96.0% | 83 min | 0 | 127 | 31 | 34.3 |

Early, Late and Undelivered are parcels per day. Trips are per day across the fleet.

All policies are deterministic (ties are broken by parcel ID / location ID), so re-running produces identical results.

## 4. Compare all policies day by day

```
python3 solution/daily_on_time_rates.py
```

Prints the on-time rate (%) of every policy for each of the 20 days.
The ranking of the policies is the same on every day.

## Metrics (`solution/performance_monitor.py`)
- `on_time_rate` (primary): parcels delivered within their window ÷ all parcels
- `delivery_rate`: parcels delivered ÷ all parcels
- `avg_lateness`: average minutes past window end, over late parcels only
- Also reported: `on_time`, `late`, `early`, `undelivered`, `number_of_trips`

## Project structure
```
solution/
├── performance_monitor.py             # metric implementation
├── summarise_results.py               # 20-day averages for a policy
├── daily_on_time_rates.py             # on-time rate of every policy, day by day
└── policies/
    ├── baseline.py                    # provided, unchanged
    ├── helpers.py                     # shared helper: group waiting parcels by location
    ├── window_priority_1pass.py       # EDF 1-pass (variant)
    ├── window_priority_2pass.py       # Policy 1: EDF (2-pass)
    ├── nearest_neighbour.py           # Policy 2: NN
    └── nearest_neighbour_window.py    # Policy 3: WA-NN (recommended)
results/
└── <policy>/day_001 ... day_020/      # log.txt and metrics.json for each day
```