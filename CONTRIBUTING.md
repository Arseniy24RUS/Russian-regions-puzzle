# Contributing / Участие

Thank you for helping improve `Russian-regions-puzzle`. Please keep contributions focused on this repository and avoid touching sibling projects or unrelated worktrees.

Спасибо за вклад в `Russian-regions-puzzle`. Пожалуйста, работайте только в этом репозитории и не изменяйте соседние проекты.

## What Helps

- Clear bug reports with browser, language, viewport and reproduction steps.
- Small UI or accessibility fixes that preserve the classroom workflow.
- Methodology improvements grounded in teaching or research practice.
- Verified map-data, naming or translation updates with documented sources.
- Tests for i18n, leaderboard behavior, export behavior and mobile interaction.

## Workflow

1. Start from the current `main` branch unless maintainers ask otherwise.
2. Use a focused branch name such as `codex/fix-mobile-tray` or `docs/methodology-update`.
3. Keep changes scoped. Do not rewrite README, data files or licensing text unless the issue asks for it.
4. Run the available local checks before opening a pull request.
5. Explain data, naming, privacy or assessment implications in the pull request when relevant.

## Local Checks

```bash
npm ci
npm test
npm run test:i18n
```

For a manual local run:

```bash
python -m http.server 8000
```

Open <http://localhost:8000/> and verify both English and Russian language flows when your change affects UI text.

## Data And Research Standards

- Document the source, license, date and modifications for any new map data.
- Do not add personal classroom data to the repository.
- Prefer pseudonymous examples in docs and screenshots.
- Keep methodology claims proportional to what the game measures.
- If you add telemetry, define the metric before collecting results.

## Licensing

By contributing, you agree that code contributions are provided under the repository MIT License and documentation, data and non-code content contributions are provided under CC BY 4.0, unless a separate license is clearly documented. Third-party materials must keep their original notices and terms.

## Русская краткая версия

- Описывайте шаги воспроизведения, браузер, язык и размер экрана.
- Для данных карты указывайте источник, лицензию, дату и правки.
- Не добавляйте реальные персональные данные студентов.
- Запускайте `npm test` и `npm run test:i18n`, если изменение затрагивает интерфейс.
- В pull request объясняйте влияние на методику, приватность или интерпретацию результатов.
