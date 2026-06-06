# Research Methodology / Методология исследования

## English

### Purpose and learning design

`Russian-regions-puzzle` is a geography learning game for practicing recognition of the federal subjects of the Russian Federation. Its primary educational value is not the production of a single grade, but repeated, feedback-rich practice with regional outlines, relative location, spatial adjacency and names. The game is suitable for courses in geography, public administration, regional studies, civic education and spatial literacy.

The activity is built around four learning mechanisms:

- **Shape recognition:** each region is presented as a draggable geometry rather than as a text-only quiz item.
- **Spatial anchoring:** learners must connect the outline with its approximate position on a projected national map.
- **Progressive retrieval:** regions appear one at a time in randomized order, which reduces answer-by-neighbor copying and encourages active recall.
- **Immediate feedback:** a piece locks only when it is close enough to the correct anchor. The learner can return the active piece to the tray, pan, zoom and try again.

For classroom use, the game works best as a short active task followed by discussion. A typical sequence is: brief orientation to the map and interface, individual or pair play, CSV export or leaderboard review, and debriefing on which regions were difficult and why. Instructors can compare completion patterns across groups, but should interpret the data as evidence of spatial practice rather than as a comprehensive assessment of regional knowledge.

### Map geometry and TopoJSON assumptions

The current app loads `Russian_regions_TopoJSON.topojson` in the browser and converts one TopoJSON object to GeoJSON features with `topojson.feature`. The file currently contains one object named `collection` with 89 geometries: 4 `Polygon` geometries and 85 `MultiPolygon` geometries. Region properties include at least `name`, `name:en` and `timezone` for the inspected records.

The app assumes:

- The intended region set is represented by one TopoJSON object whose feature count is close to 89.
- Each feature corresponds to one playable federal subject.
- Geometry coordinates are usable with `d3.geoMercator()`.
- Region names can be read from a string property, with preference emerging from property frequency and name-like keys.
- Translation keys in `locales/en.json` and `locales/ru.json` cover the region labels used by the data file.

Projection and rendering are deliberately pragmatic. The app uses a Mercator projection rotated by `[-105, 0]`, fits the full GeoJSON collection to the canvas, draws a simplified `Path2D` for regular rendering and keeps high-resolution paths for tray rendering. A seam-break threshold is used when building paths so that long projected jumps do not draw accidental connecting lines. These choices support an interactive classroom puzzle; they should not be treated as a general-purpose cartographic standard.

For research reporting, record the exact commit, data file name, feature count, projection settings and any changes to region names or boundaries. If the geometry source is replaced, document the upstream data provider, license, date, coordinate reference assumptions, simplification method and any manual edits.

### Scoring, timer, difficulty and leaderboard logic

The current implementation uses completion time as the main performance metric. There is no separate numeric score beyond completion status, number of placed pieces and elapsed time.

The timer starts when the first piece is successfully placed. It updates continuously until all pieces are placed, then the final time is displayed and stored. The display is capped at `59:59`, while persisted `time_ms` is computed from browser `performance.now()`.

Difficulty changes the snap radius:

| Difficulty | Snap radius |
| --- | ---: |
| Easy | 60 px |
| Medium | 30 px |
| Hard | 12 px |

After the first successful placement, the difficulty selector is locked for that run. This prevents a learner from beginning on an easier setting and switching to a harder category before submission. The last remaining piece auto-snaps when dropped, which prevents an otherwise complete puzzle from stalling on a final tiny placement issue.

The leaderboard reads raw result records from Firebase Realtime Database under `results`. It normalizes difficulty names, optionally filters by group, and shows the best result for each `full name + group + difficulty` combination. Ranking is by ascending `time_ms`. CSV export downloads raw records, not only filtered or deduplicated leaderboard rows.

Current persisted fields are:

- `fio`
- `group`
- `difficulty`
- `time_ms`
- `placed`
- `total`
- `timestamp`
- `user_agent`

Although some older README wording mentions error counts, the current code does not persist a separate error or attempt counter. If an error metric is added later, define it before data collection begins. For example, decide whether an error means any failed drop, a drop outside the snap radius, use of return-to-tray, excessive hinting, or a region-level correction.

### Firebase and export considerations

Firebase is optional infrastructure for class-wide leaderboards and result collection. The client configuration values in the static app are public identifiers, not server secrets. Real protection depends on Firebase Realtime Database rules, project ownership, retention policy and classroom operating practice.

Before collecting classroom data, instructors or maintainers should decide:

- Whether full names are necessary, or whether pseudonymous IDs are preferable.
- How long records will be retained.
- Who can read and export results.
- Whether consent, notice or institutional review is required.
- Whether user-agent strings are needed for debugging or should be removed.
- Whether group labels could identify a small cohort.

CSV export is useful for reproducible analysis, but the exported file may contain personal data. Treat exports as classroom records. When publishing research or examples, aggregate or anonymize results and avoid quoting identifiable names, groups or device information.

### Limits of assessment

The game measures a narrow and useful construct: speed and success in matching region shapes to their approximate map positions through this interface. It does not, by itself, measure conceptual understanding of federalism, regional economies, demography, political geography, historical change, legal status, cartographic projections or the ability to interpret unfamiliar maps.

Observed completion time can be affected by prior exposure, motor control, screen size, network performance, map familiarity, language setting, anxiety under timed conditions and collaboration outside the interface. Leaderboard data should therefore be used as a diagnostic prompt and engagement record, not as a standalone high-stakes grade.

For research use, pair game telemetry with at least one additional evidence source: pre/post quiz, short reflection, think-aloud observation, region-cluster analysis, instructor rubric or follow-up discussion. Report missing data, repeated attempts, device differences and whether students played individually or in teams.

### Adaptation for another course or region set

To adapt the game for another geography course, first define the pedagogical target: administrative units, physical regions, electoral districts, historical territories or thematic zones. Then prepare a TopoJSON file where each playable unit is one feature with stable names and optional translated labels.

Recommended adaptation checklist:

- Replace `Russian_regions_TopoJSON.topojson` or update the `TOPO` constant in `index.html`.
- Verify that the object-selection logic chooses the intended TopoJSON object, especially if the new set does not contain 89 features.
- Update region labels in `locales/en.json` and `locales/ru.json`.
- Update the hardcoded initial placed label in the HTML if the feature count is no longer 89.
- Reconsider the projection, rotation and `fitSize` behavior for the new geography.
- Recalibrate snap radii after testing on desktop and mobile screens.
- Update README, methodology, citation and third-party notices with the new data source and course purpose.
- Decide whether the leaderboard should compare all learners together or separate cohorts, modules and difficulty rules.

For a smaller region set, tighter snap radii may be appropriate. For dense urban districts or small islands, the game may need hints, inset maps, grouped rounds or scale-aware snap thresholds. For politically sensitive or historically changing boundaries, document the data date and naming convention explicitly.

### Reproducible local commands

Install dependencies from the lockfile:

```bash
npm ci
```

Run the full local Playwright test suite:

```bash
npm test
```

Run the i18n-focused tests:

```bash
npm run test:i18n
```

Launch a local static server:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/>. Runtime CDN access may be needed outside the Playwright test stubs.

Check the current TopoJSON object and feature count:

```bash
node -e "const fs=require('fs'); const topo=JSON.parse(fs.readFileSync('Russian_regions_TopoJSON.topojson','utf8')); for (const [k,o] of Object.entries(topo.objects)) console.log(k, (o.geometries||[]).length);"
```

For research artifacts, record the command outputs, commit hash, browser version and whether Firebase was connected or stubbed.

## Русский

### Цель и учебный дизайн

`Russian-regions-puzzle` - учебная географическая игра для тренировки распознавания субъектов Российской Федерации. Ее основная ценность состоит не в выставлении одной итоговой оценки, а в повторяемой практике с обратной связью: контуры регионов, взаимное положение, соседство и названия.

Игра подходит для курсов по географии, государственному управлению, регионоведению, гражданскому образованию и пространственной грамотности.

В основе активности лежат четыре механизма:

- **Распознавание формы:** регион предъявляется как геометрическая фигура, а не только как текстовый вопрос.
- **Пространственная привязка:** учащийся соотносит контур с примерным местом на проецированной карте страны.
- **Извлечение из памяти:** регионы появляются по одному в случайном порядке, что снижает угадывание по соседним ответам.
- **Немедленная обратная связь:** деталь фиксируется только при достаточно близком размещении. Учащийся может вернуть деталь в лоток, переместить карту, изменить масштаб и попробовать снова.

В аудитории игра лучше всего работает как короткая активная задача с последующим обсуждением. Типовая последовательность: краткое объяснение карты и интерфейса, индивидуальная или парная игра, экспорт CSV или просмотр таблицы лидеров, обсуждение того, какие регионы оказались трудными и почему. Преподаватель может сравнивать результаты групп, но эти данные следует понимать как показатель пространственной тренировки, а не как полную оценку знания регионов.

### Геометрия карты и предположения TopoJSON

Текущая версия загружает `Russian_regions_TopoJSON.topojson` в браузере и преобразует один объект TopoJSON в GeoJSON-features через `topojson.feature`. Сейчас файл содержит один объект `collection` с 89 геометриями: 4 геометрии `Polygon` и 85 геометрий `MultiPolygon`. В проверенных записях свойства региона включают как минимум `name`, `name:en` и `timezone`.

Приложение предполагает:

- нужный набор регионов представлен одним объектом TopoJSON, число features близко к 89;
- каждая feature соответствует одному игровому субъекту;
- координаты геометрии совместимы с `d3.geoMercator()`;
- название региона можно извлечь из строкового свойства, предпочтительно из ключей, похожих на name;
- переводы в `locales/en.json` и `locales/ru.json` покрывают подписи, которые приходят из файла данных.

Проекция и отрисовка выбраны прагматично. Приложение использует Mercator-проекцию с поворотом `[-105, 0]`, вписывает всю коллекцию GeoJSON в canvas, строит упрощенный `Path2D` для обычной отрисовки и сохраняет более детальные пути для детали в лотке. Порог разрыва при построении пути нужен, чтобы длинные проектированные скачки не превращались в случайные соединительные линии. Эти решения полезны для интерактивного учебного пазла, но не являются универсальным картографическим стандартом.

Для исследовательского отчета фиксируйте точный commit, имя файла данных, число features, настройки проекции и любые изменения названий или границ. Если геометрия заменяется, нужно документировать поставщика исходных данных, лицензию, дату, координатные предположения, метод упрощения и ручные правки.

### Подсчет, таймер, сложность и таблица лидеров

В текущей реализации главным показателем является время завершения. Отдельного числового балла нет: сохраняются факт завершения, число размещенных деталей и прошедшее время.

Таймер запускается после первой успешно установленной детали. Он обновляется до тех пор, пока все детали не размещены, затем итоговое время показывается и сохраняется. Отображение ограничено `59:59`, а сохраняемое `time_ms` считается через браузерный `performance.now()`.

Сложность меняет радиус автопривязки:

| Сложность | Радиус привязки |
| --- | ---: |
| Легкая | 60 px |
| Средняя | 30 px |
| Высокая | 12 px |

После первой успешной установки выбор сложности блокируется для текущей попытки. Это не позволяет начать на легком уровне и переключиться на более сложную категорию перед сохранением результата. Последняя оставшаяся деталь привязывается автоматически при сбросе, чтобы почти завершенный пазл не застревал из-за мелкой технической погрешности.

Таблица лидеров читает сырые записи из Firebase Realtime Database в узле `results`. Она нормализует названия сложностей, при необходимости фильтрует по группе и показывает лучший результат для каждой комбинации `ФИО + группа + сложность`. Ранжирование идет по возрастанию `time_ms`. Экспорт CSV скачивает сырые записи, а не только отфильтрованные или дедуплицированные строки таблицы лидеров.

Текущие сохраняемые поля:

- `fio`
- `group`
- `difficulty`
- `time_ms`
- `placed`
- `total`
- `timestamp`
- `user_agent`

В некоторых старых формулировках README упоминалось число ошибок, но текущий код не сохраняет отдельный счетчик ошибок или попыток. Если такая метрика будет добавлена, ее нужно определить до начала сбора данных. Например, заранее решить, считается ли ошибкой любой неудачный сброс, сброс вне радиуса привязки, возврат детали в лоток, подсказка или исправление на уровне региона.

### Firebase и экспорт

Firebase используется как опциональная инфраструктура для общей таблицы лидеров и сбора результатов. Значения client config в статическом приложении являются публичными идентификаторами, а не серверными секретами. Реальная защита зависит от правил Firebase Realtime Database, владельца проекта, политики хранения и практики работы в аудитории.

Перед сбором учебных данных следует решить:

- нужны ли полные ФИО или лучше использовать псевдонимные ID;
- как долго будут храниться записи;
- кто может читать и экспортировать результаты;
- нужны ли согласие, уведомление или институциональное согласование;
- нужен ли `user_agent` для отладки или его лучше убрать;
- может ли номер группы идентифицировать малую когорту.

CSV-экспорт удобен для воспроизводимого анализа, но выгрузка может содержать персональные данные. Обращайтесь с ней как с учебными записями. При публикации исследования или примеров агрегируйте или анонимизируйте результаты и не раскрывайте ФИО, малые группы и сведения об устройствах.

### Ограничения оценки

Игра измеряет узкий, но полезный конструкт: скорость и успешность сопоставления формы региона с примерным положением на карте в данном интерфейсе. Сама по себе она не измеряет понимание федерализма, региональной экономики, демографии, политической географии, исторических изменений, юридического статуса, картографических проекций или умение интерпретировать незнакомые карты.

Время прохождения может зависеть от предварительной подготовки, моторики, размера экрана, производительности сети, привычки к карте, выбранного языка, волнения из-за таймера и помощи вне интерфейса. Поэтому таблицу лидеров лучше использовать как диагностический и мотивационный материал, а не как единственный источник итоговой оценки.

Для исследования стоит сочетать телеметрию игры хотя бы с одним дополнительным источником: входным и выходным тестом, короткой рефлексией, наблюдением think-aloud, анализом групп регионов, преподавательской рубрикой или последующим обсуждением. В отчете указывайте пропущенные данные, повторные попытки, различия устройств и формат работы - индивидуальный или командный.

### Адаптация для другого курса или набора регионов

Для адаптации сначала определите учебную цель: административные единицы, физико-географические районы, избирательные округа, исторические территории или тематические зоны. Затем подготовьте TopoJSON, где каждая игровая единица является одной feature со стабильным названием и, при необходимости, переводом.

Рекомендуемый чек-лист адаптации:

- заменить `Russian_regions_TopoJSON.topojson` или обновить константу `TOPO` в `index.html`;
- проверить, что логика выбора объекта TopoJSON берет нужный объект, особенно если новый набор не содержит 89 features;
- обновить подписи регионов в `locales/en.json` и `locales/ru.json`;
- обновить начальную подпись `0 / 89` в HTML, если число регионов изменилось;
- пересмотреть проекцию, поворот и поведение `fitSize` для новой географии;
- заново подобрать радиусы привязки после тестов на desktop и mobile;
- обновить README, методологию, цитирование и уведомления о третьих сторонах;
- решить, должна ли таблица лидеров сравнивать всех учащихся вместе или разделять когорты, модули и правила сложности.

Для меньшего набора регионов могут подойти более строгие радиусы. Для плотных городских округов или малых островов могут понадобиться подсказки, inset-карты, раунды по группам или радиусы привязки, зависящие от масштаба. Для политически чувствительных или исторически меняющихся границ явно указывайте дату данных и принцип именования.

### Воспроизводимые локальные команды

Установить зависимости из lockfile:

```bash
npm ci
```

Запустить полный локальный набор Playwright-тестов:

```bash
npm test
```

Запустить i18n-тесты:

```bash
npm run test:i18n
```

Запустить локальный статический сервер:

```bash
python -m http.server 8000
```

Затем открыть <http://localhost:8000/>. Вне Playwright-заглушек может потребоваться доступ к CDN.

Проверить текущий объект TopoJSON и число features:

```bash
node -e "const fs=require('fs'); const topo=JSON.parse(fs.readFileSync('Russian_regions_TopoJSON.topojson','utf8')); for (const [k,o] of Object.entries(topo.objects)) console.log(k, (o.geometries||[]).length);"
```

Для исследовательских артефактов фиксируйте вывод команд, hash commit, версию браузера и то, был ли Firebase подключен или заменен тестовой заглушкой.
