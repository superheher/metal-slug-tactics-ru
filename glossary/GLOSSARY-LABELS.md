# Canon for labels inside placeholders (second pass)

## The problem

Strings contain placeholders of the form `{Path:Text}`. The text **after the colon is what the
player actually sees** (SmartFormat substitutes it as a link caption). It MUST be translated.

```
{Move:Moves} a unit to a tile.        ->  {Move:Перемещает} бойца на клетку.
The range of {BonusMovement:bonus moves}  ->  Дальность {BonusMovement:бонусных перемещений}
```

**The path before the colon (`Move`, `BonusMovement`) is copied CHARACTER FOR CHARACTER — it is not for the eyes, it is for the engine.**

## ⛔ THREE EXCEPTIONS — DO NOT TOUCH

These are number formats, not text. Translating them will break them:
```
{Delay:0.#}     {FPS:0.##}     {RemainingTime:0}
```

## Inflection

A label is part of a sentence, so it **inflects by context**, like an ordinary word:
- `{ActionPoint:action}` → «...получает {ActionPoint:действие}»
- `{ActionPoint:actions}` → «...тратит все {ActionPoint:действия}»
- `{BonusMovement:bonus moves}` → «Дальность {BonusMovement:бонусных перемещений}»
- `{BonusMovement:bonus move}` → «Даёт {BonusMovement:бонусное перемещение}»

The base form is taken from the table below, and from there — by the rules of Russian grammar.

## Table of base forms

| path | English label | Russian base |
|---|---|---|
| `Move` | Moves / moves | перемещает / перемещение |
| `MovementPoint` | move / movement / movements / moves | перемещение |
| `BonusMovement` | bonus move / bonus moves / bonus movements | бонусное перемещение |
| `ActionPoint` | Action / action / actions | действие |
| `ActionPoint` | bonus action / bonus actions | бонусное действие |
| `Keywords.ActionPoint` | action | действие |
| `SpecialAction` | Special Actions / special action(s) | особое действие |
| `Keywords.SpecialAction` | special actions | особые действия |
| `Keywords.Charge` | Charges | совершает рывок |
| `Keywords.Cover` | covers | укрытия |
| `Keywords.Passive` | Passives | пассивные способности |
| `Keywords.BaseWeapon` / `BaseWeapon` | primary weapon(s) | основное оружие |
| `Keywords.SpecialWeapon` | special weapon(s) | особое оружие |
| `Abilities.Synchronization` | sync / syncs / sync attacks / synchronize | синхроудар / синхронизировать |
| `Abilities.Bot` | bots | боты |
| `Abilities.ElectricMine` | Electric Mines / mines | электрические мины / мины |
| `Abilities.Flame` | flames | пламя |
| `Abilities.Mummy` | Mummies | мумии |
| `Abilities.Vehicle` | vehicles | техника |
| `Abilities.AfterImage` / `AfterImage` / `Keywords.AfterImage` | Afterimages | остаточные образы |
| `Enemies.Mummy` | mummies | мумии |
| `Enemies.DogMummy` | mummified dogs | мумифицированные псы |
| `Enemies.Rifleman` | Deadeyes | меткие стрелки |
| `Props.Geyser` | geysers | гейзеры |
| `Characteristics.HitsPerAttack` | hit | попадание |

## Labels with markup inside

There are `{HasAnyPointerDevice:by <style="Highlight">clicking</style> ...|...}` — the tags
are copied character for character, only the text between them is translated:
`{HasAnyPointerDevice:<style="Highlight">щелчком</style> ...|...}`.

## Conditions and choice

- `{RangeMax:cond:<1?Self|...}` — `Self` is an output → «На себя». The service `cond:<1?` — do not touch.
- `{Leader.Gender:choose(F|M):chick|guy}` — `chick|guy` is an output → `{Leader.Gender:choose(F|M):деваха|мужик}`.
  The service `choose(F|M):` — do not touch. Keep the order of options (F first, then M).

## Squad names — CANON

| EN | RU |
|---|---|
| Peregrine Falcons / Falcons / Falcon | **«Сапсаны» / «Сапсан»** (inflected) |
| SPARROWS | **«Воробьи»** (inflected; do NOT leave in Latin) |
| World Government | **Всемирное правительство** |
| Regular Army | Регулярная армия |
| Rebel Army / Rebels | Армия повстанцев / повстанцы |
| Ptolemaic Army | Птолемейская армия |
