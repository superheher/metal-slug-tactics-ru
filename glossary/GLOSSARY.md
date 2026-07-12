# Metal Slug Tactics translation glossary and rules (EN → RU)

This is **law**. No deviations allowed: the same term must sound identical across all tables.

## 0. INVIOLABLE TECHNICAL RULES

1. **Placeholders in curly braces are copied CHARACTER FOR CHARACTER; not translated, not inflected.**
   `{Characteristics.Damage}`, `{Fuel}`, `{CharacteristicValue}`, `{Loc.Data/Keywords.Armor/DisplayName}`,
   `{0}`, `{Character.Name}` — never reach inside the braces at all.
   Build the phrase so the placeholder stands in the nominative case: not «наносит {X} урона врагу»,
   but «Урон: {X}» or «наносит урон в размере {X}».
2. **Markup tags are copied character for character**: `<style=Characteristic>`, `<nobr>`, `<link=HealthPoints.characteristic>`,
   `</link>`, `</nobr>`, `</style>`, `<b>`, `<i>`, `<sprite=...>`, `<color=...>`.
   Only the visible text **between** the tags is translated. The attributes inside `<...>` — never.
3. **Escape sequences are preserved**: `\n`, `\r\n`, `\"`. The count and order — as in the original.
4. Leading and trailing spaces are preserved.
5. If a string is empty, a service one (`Keyword 1`, `Test`, `F`, `M`, `Pa`, `Pe`) or pure code/number —
   leave it **as is**, do not translate.

## 1. TONE

Metal Slug is an arcade shooter: brisk, soldierly, comic in places. The texts are short and punchy.
- UI — dry and short (space on buttons is limited).
- Dialogue — living speech, no bureaucratese. The characters joke and bicker.
- Ability descriptions — telegraphic, like a reference: «Наносит X урона. Накладывает Y на 2 хода.»

### Formal or informal — a table, not «as is usual»

Previously there was a vague «in dialogue — as between comrades-in-arms» here, and translators
understood it differently: the commander was addressed sometimes with «ты», sometimes with «вы».
Now unambiguously:

| who to whom | how |
|---|---|
| UI, tutorials → player | **вы** |
| soldiers → the commander (placeholders `{Leader.Title}`, `{Leader.FirstName}`, `{Leader.LastName}`) | **вы** |
| soldiers → Margaret Southwood (Commander Southwood, senior in rank) | **вы** |
| soldiers among themselves | **ты** |
| to enemies (Morden, Abbas, Paqar) | **ты** |

`{Leader.*}` is the **player**. Margaret Southwood is a **separate character**, Trevor's mentor;
do not confuse them, even though both are called «командир».

**«командир» as a form of address is written lowercase** — in Russian it is a word, not a title.
`Commander` capitalized in the original is a norm of English, not a reason to copy it.

## 2. HEROES (Metal Slug canon, transliteration)

| EN | RU |
|---|---|
| Marco Rossi / Marco | Марко Росси / Марко |
| Tarma Roving / Tarma | Тарма Ровинг / Тарма |
| Eri Kasamoto / Eri | Эри Касамото / Эри |
| Fio Germi / Fio | Фио Джерми / Фио |
| Leona Heidern / Leona | Леона Хайдерн / Леона |
| Ralf Jones / Ralf | Ральф Джонс / Ральф |
| Clark Still / Clark | Кларк Стилл / Кларк |
| Nadia Cassel / Nadia | Надя Кассель / Надя |
| Trevor Spacey / Trevor | Тревор Спейси / Тревор |
| Rumi Aikawa / Rumi | Руми Айкава / Руми |
| Alice | Элис |
| Margaret | Маргарет |
| Heidern | Хайдерн |
| Kasamoto / Germi / Jones / Cassel / Still | Касамото / Джерми / Джонс / Кассель / Стилл |

Ranks: Captain — Капитан, Colonel — Полковник, Major — Майор, Private — Рядовой,
Master Sergeant — Старший сержант, General — Генерал.

## 3. ENEMIES AND VEHICLES

| EN | RU |
|---|---|
| General Morden / Morden | Генерал Морден / Морден |
| Allen O'Neil | Аллен О'Нил |
| Abul Abbas | Абул Аббас |
| Aeshi Nero | Аэши Неро |
| Paqar | Пакар |
| Hatchetman | Топорник |
| Minelayer | Минёр |
| Acolyte | Послушник |
| Berserker | Берсерк |
| Deadeye | Меткий стрелок |
| Grenadier | Гренадёр |
| Spearman | Копейщик |
| Torchbearer | Факельщик |
| Sabre Thrower | Метатель сабель |
| Scout | Разведчик |
| Bazooka Soldier | Солдат с базукой |
| Gatling Soldier | Солдат с гатлингом |
| Shielded Soldier | Солдат со щитом |
| Mutated Soldier | Мутировавший солдат |
| Mummy / Mummified Dog | Мумия / Мумифицированный пёс |
| Idol | Идол |
| Drone | Дрон |
| Pod | Капсула |
| Mortar | Миномёт |
| Truck | Грузовик |
| Rebel Tower | Башня повстанцев |
| Blue / Red Supporter | Синий / Красный помощник |

Vehicles are proper names, transliterated:
Di-Cokka — **Ди-Кокка** · Big Shiee — **Биг Ши** · Jupiter King — **Юпитер Кинг** ·
Dragon Nosuke — **Дракон Носукэ** · Sarubia — **Сарубия** · Bradley — **Брэдли** ·
Iron Lizard — **Железный Ящер** · Gunbot — **Ганбот** · Slugnoid — **Слагноид** ·
Metal Slug — **Metal Slug** (not translated, it is the vehicle's brand name).

## 4. MECHANICS (keywords)

| EN | RU |
|---|---|
| Sync / Sync attack | Синхроудар |
| Adrenaline | Адреналин |
| Ammo | Патроны |
| Armor | Броня |
| Cover | Укрытие |
| Fuel | Топливо |
| Overheat | Перегрев |
| Momentum | Импульс |
| Charge | Заряд |
| Perk | Перк |
| Medal | Медаль |
| Coins | Монеты |
| Experience / XP | Опыт / XP |
| Prestige | Престиж |
| Arsenal | Арсенал |
| Turn | Ход |
| Move / Movement | Перемещение |
| Action | Действие |
| Bonus Move | Бонусное перемещение |
| Delayed Projectile | Снаряд с задержкой |
| Enemy Reinforcements | Вражеское подкрепление |
| Interactive Element | Интерактивный элемент |
| Passive | Пассивная способность |
| Primary Weapon | Основное оружие |
| Special Weapon | Особое оружие |
| Special Action | Особое действие |
| Strategic Asset | Стратегический ресурс |
| Destructible | Разрушаемый |
| Area of Effect | Зона поражения |
| Initiative | Инициатива |
| Dodge | Уклонение |
| Range | Дальность |
| Damage | Урон |
| Health Points | Очки здоровья |

## 5. SHORT ABBREVIATIONS — DO NOT TOUCH

`HP`, `DMG`, `ADR`, `MR`, `AoE`, `Init`, `XP`, `LV1/LV2/LV3` stay in **Latin**:
these are labels in cramped UI spots, and translating them would break the layout. The full names,
however, are translated (Health Points → Очки здоровья).

## 6. STATUSES (effects)

Bleeding — Кровотечение · Haste — Ускорение · Fatigue — Усталость · Fragile — Хрупкость ·
Flashbang — Ослепление · Anticipation — Предвкушение · Expertise — Мастерство ·
Focused Fire — Сосредоточенный огонь · Mind Control — Контроль разума · Escape — Побег ·
Counter LV1/LV2/LV3 — Контратака LV1/LV2/LV3 · Afterimage — Остаточный образ ·
Hidden Bomb — Скрытая бомба · Guard Mark / Dash Mark — Метка защиты / Метка рывка.

Named statuses such as `Abbas Damage`, `Germi Style`, `Marco Salvo`, `Moon Slasher`
are translated by meaning, keeping the name: «Урон Аббаса», «Стиль Джерми», «Залп Марко», «Лунный клинок».

## 7. WHAT NOT TO DO

- Do not translate keys. `WASD` stays `WASD`. (The old fan translation had «Ц/Ф/Ы/В» — that is a mistake,
  the keys are physically the same.)
- Do not translate proper names inside `{}` and `<>`.
- Do not «improve» the markup: the number of tags in and out must match.
- Do not add a period at the end if there is none in the original (and vice versa).
- Do not turn short UI labels into long phrases — space is limited.

## 8. TRAPS: identical English ≠ identical Russian

There are strings where **one English word means different things**, and unifying them into a
single translation is a mistake. The automatic «one EN → one RU» check complains about them, and
complains in vain.

| EN | where | RU | why |
|---|---|---|---|
| `Credits` | Keywords | **Кредиты** | a between-runs currency («Credits are a currency gained at the end of each campaign») |
| `Credits` | UI | **Авторы** | the credits screen |

There are **two** currencies in the game: `Coins` — Монеты (spent at the outpost within a run) and
`Credits` — Кредиты (given at the end of a campaign). Do not confuse or merge them.

**Rule:** before unifying two translations of one English word into one — look at which tables they
come from and what text is next to them. Matching words do not mean matching meaning.

### The flip side: inflection is not inconsistency

`{Abilities.Bot:боты}` / `{Abilities.Bot:ботов}` / `{Abilities.Bot:ботами}` — this is **correct**.
English makes do with the single form `bots`, Russian must inflect by phrase. Labels inside
placeholders inflect freely; what must stay unchanged is the **stem**, not the ending.
