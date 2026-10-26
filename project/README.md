# IS115 Project README (JUST PLACEHOLDER FOR NOW SUBJECT TO REFINEMENTS)

## 1. Run a simulation (one day)
```
python3 -m simulator --policy solution.policies.baseline --data data --day day_001 --output results/baseline/day_001
```
Replace `baseline` with any policy in `solution/policies/`.


## 2. Calculate metrics (one day)
```
python3 -m solution.performance_monitor --data data --day day_001 --log results/baseline/day_001/log.txt
```
Writes `metrics.json` next to the log.


## 3. Run all 20 days

Mac/Linux:
```
for i in $(seq -f "%03g" 1 20); do
  python3 -m simulator --policy solution.policies.baseline --data data --day day_$i --output results/baseline/day_$i
  python3 -m solution.performance_monitor --data data --day day_$i --log results/baseline/day_$i/log.txt
done
```

Windows (PowerShell):
```
foreach ($i in 1..20) {
  $day = "day_{0:D3}" -f $i
  python -m simulator --policy solution.policies.baseline --data data --day $day --output results/baseline/$day
  python -m solution.performance_monitor --data data --day $day --log results/baseline/$day/log.txt
}
```

## 4. Average results over 20 days
```
python3 solution/summarise_results.py baseline
```

## Metrics
- `on_time_rate` (primary): parcels delivered within window ÷ all parcels
- `delivery_rate`: parcels delivered ÷ all parcels
- `avg_lateness`: average minutes late, over late parcels only