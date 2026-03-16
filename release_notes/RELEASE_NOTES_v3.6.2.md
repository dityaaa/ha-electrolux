# Release Notes v3.6.2

## WM Catalog Improvements (AEG L7FENQ96 / ProSteam 7000 washer-dryer & beyond)

### New entities
- **`miscellaneous/defaultSoftPlus`** — switch entity for the "Default Soft Plus" softener setting (AEG L7FENQ96 and compatible washer-dryers).
- **Maintenance items 2–10** — binary sensor + threshold sensor entries for `applianceCareAndMaintenance0/maint2_*` through `maint5_*` and `applianceCareAndMaintenance1/maint6_*` through `maint10_*`. Previously only item 1 was exposed; these cover the full maintenance schedule advertised by the appliance.

### Fixes & improvements
- **`totalWashingTime`** — unit corrected from `MINUTES` to `SECONDS`. The raw value (e.g. 5 202 000) represents seconds, not minutes; the old unit resulted in absurdly large durations (~10 years for a normal machine).
- **`applianceTotalWorkingTime`** (core catalog) — same unit fix: `MINUTES` → `SECONDS`.
- **`fCMiscellaneousState/tankAReserve`** and **`fCMiscellaneousState/tankBReserve`** — changed from generic boolean sensor to `BinarySensorDeviceClass.PROBLEM`. A "reserve" flag means the tank level is critically low, which is a problem/warning condition. This enables the correct icon and HA home dashboard colouring.
- **`fCMiscellaneousState/waterUsage`** — added `SensorDeviceClass.WATER` and `UnitOfVolume.LITERS`. Previously the sensor had no unit; it now participates in HA's unit-conversion and energy dashboard.
- **`userSelections/analogTemperature`** — added `95_CELSIUS` to the catalog fallback values list (alongside the existing `90_CELSIUS`) to cover appliances that top out at 95 °C. Appliances whose API returns their own values list are unaffected.
- **Maintenance item 1 `maint1_occured`** — changed from generic `device_class=None` to `BinarySensorDeviceClass.PROBLEM`, consistent with the newly added items 2–10.

### Translations
- **Spanish (es.json)** — fixed exception message placeholders to match English template variable names:
  - `appliance_offline`: `{estado}` → `{state}`
  - `not_supported_by_program`: `{programa}` → `{program}`
  - `food_probe_not_supported_by_program`: `{programa}` → `{program}`
  - `food_probe_locked_by_program`: `{valor}`, `{programa}` → `{value}`, `{program}`
  - `invalid_preset_mode`: `{modo}`, `{modos}` → `{mode}`, `{modes}`
- **All other language files** — fixed placeholder mismatches to align with English template:
  - Czech, Danish, Dutch, Finnish, German, Hungarian, Luxembourg, Norwegian, Polish, Romanian, Russian, Slovak, Swedish — corrected placeholder names in exception messages to use English identifiers (`{state}`, `{program}`, `{value}`, `{mode}`, `{modes}`) instead of translated names
  - Italian — fixed `invalid_preset_mode` to use `{modes}` instead of duplicate `{mode}`
- **`translate.py` script** — enhanced to preserve placeholder names during translation. All placeholders (e.g. `{state}`, `{program}`) are now extracted before translation and restored afterward, preventing future placeholder translation errors.
