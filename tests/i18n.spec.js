const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");

const repoRoot = path.resolve(__dirname, "..");
const screenshotDir = path.join(repoRoot, "qa-screenshots", "Russian-regions-puzzle");

const firebaseStub = `
(function(){
  if (window.firebase) return;
  var emptySnap = { val: function(){ return {}; } };
  var ref = {
    on: function(eventName, callback){
      if (eventName === "value") setTimeout(function(){ callback(emptySnap); }, 0);
    },
    push: function(){ return Promise.resolve({ key: "stubbed-result" }); }
  };
  window.firebase = {
    initializeApp: function(){ return {}; },
    database: function(){
      return { ref: function(){ return ref; } };
    }
  };
})();
`;

test.setTimeout(90000);

async function routeThirdPartyScripts(page){
  await page.route("https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js", route => {
    route.fulfill({
      path: path.join(repoRoot, "node_modules", "d3", "dist", "d3.min.js"),
      contentType: "application/javascript"
    });
  });
  await page.route("https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js", route => {
    route.fulfill({
      path: path.join(repoRoot, "node_modules", "topojson-client", "dist", "topojson-client.min.js"),
      contentType: "application/javascript"
    });
  });
  await page.route(/https:\/\/www\.gstatic\.com\/firebasejs\/9\.23\.0\/firebase-(app|database)-compat\.js/, route => {
    route.fulfill({
      body: firebaseStub,
      contentType: "application/javascript"
    });
  });
}

async function openPuzzle(page, errors){
  await routeThirdPartyScripts(page);
  page.on("console", msg => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  page.on("pageerror", err => errors.push(err.message));
  await page.goto("/");
  await page.waitForFunction(() => {
    var status = document.querySelector("#status");
    return window.AppI18n &&
      window.AppI18n.ready &&
      status &&
      ["Map loaded", "Карта загружена"].indexOf(status.textContent.trim()) >= 0;
  });
}

function screenshotPath(name){
  fs.mkdirSync(screenshotDir, { recursive: true });
  return path.join(screenshotDir, name + ".png");
}

async function assertSingleToggle(page, expectedText){
  const toggle = page.getByTestId("language-toggle");
  await expect(toggle).toHaveCount(1);
  await expect(toggle).toHaveText(expectedText);
}

async function assertEnglish(page){
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page).toHaveTitle("Online Puzzle \"Map of Federal Subjects of Russia\" - Canvas, Leaderboard, Firebase");
  await expect(page.getByRole("heading", { name: "Online Puzzle \"Map of Federal Subjects of Russia\"" })).toBeVisible();
  await expect(page.locator("[data-i18n='form.fullNameLabel']")).toHaveText("Full name");
  await expect(page.getByPlaceholder("Ivanov Ivan Ivanovich")).toBeVisible();
  await expect(page.locator("#difficulty option[value='easy']")).toHaveText("Easy");
  await expect(page.locator("[data-i18n='stats.placed']")).toHaveText("Placed");
  await expect(page.locator("[data-i18n='leaderboard.title']")).toHaveText("Leaderboard");
  await expect(page.locator("[data-i18n='leaderboard.subtitle']")).toHaveText("Best result within each difficulty");
  await expect(page.getByPlaceholder("Filter by group")).toBeVisible();
  await expect(page.locator("#status")).toHaveText("Map loaded");
  await expect(page.locator("#leader_easy tbody")).toContainText("No data");
  await assertSingleToggle(page, "RU");
  await expect(page.locator("canvas#cv")).toBeVisible();
  expect(await page.evaluate(() => window.AppI18n.translateRegion("Москва"))).toBe("Moscow");
  expect(await page.evaluate(() => window.AppI18n.translateFederalDistrict("Центральный федеральный округ"))).toBe("Central Federal District");
}

async function assertRussian(page){
  await expect(page.locator("html")).toHaveAttribute("lang", "ru");
  await expect(page).toHaveTitle("Онлайн-пазл «Карта субъектов Российской Федерации» — Canvas, лидеры, Firebase");
  await expect(page.getByRole("heading", { name: "Онлайн-пазл «Карта субъектов Российской Федерации»" })).toBeVisible();
  await expect(page.locator("[data-i18n='form.fullNameLabel']")).toHaveText("ФИО");
  await expect(page.getByPlaceholder("Иванов Иван Иванович")).toBeVisible();
  await expect(page.locator("#difficulty option[value='easy']")).toHaveText("Лёгкая");
  await expect(page.locator("[data-i18n='stats.placed']")).toHaveText("Поставлено");
  await expect(page.locator("[data-i18n='leaderboard.title']")).toHaveText("Таблица лидеров");
  await expect(page.locator("[data-i18n='leaderboard.subtitle']")).toHaveText("Лучший результат в пределах своей сложности");
  await expect(page.getByPlaceholder("Фильтр по группе")).toBeVisible();
  await expect(page.locator("#status")).toHaveText("Карта загружена");
  await expect(page.locator("#leader_easy tbody")).toContainText("Нет данных");
  await assertSingleToggle(page, "EN");
  await expect(page.locator("canvas#cv")).toBeVisible();
  expect(await page.evaluate(() => window.AppI18n.translateRegion("Москва"))).toBe("Москва");
  expect(await page.evaluate(() => window.AppI18n.translateFederalDistrict("Центральный федеральный округ"))).toBe("Центральный федеральный округ");
}

test("en-US desktop defaults to English and toggles to Russian", async ({ browser }) => {
  const context = await browser.newContext({
    locale: "en-US",
    viewport: { width: 1280, height: 900 }
  });
  const page = await context.newPage();
  const errors = [];

  try {
    await openPuzzle(page, errors);
    await assertEnglish(page);
    await page.screenshot({ path: screenshotPath("desktop-en"), fullPage: true });

    await page.getByTestId("language-toggle").click();
    await assertRussian(page);
    await page.screenshot({ path: screenshotPath("desktop-ru"), fullPage: true });

    expect(errors).toEqual([]);
  } finally {
    await context.close();
  }
});

test("ru-RU mobile defaults to Russian and toggles to English", async ({ browser }) => {
  const context = await browser.newContext({
    locale: "ru-RU",
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const page = await context.newPage();
  const errors = [];

  try {
    await openPuzzle(page, errors);
    await assertRussian(page);
    await page.screenshot({ path: screenshotPath("mobile-ru"), fullPage: true });

    await page.getByTestId("language-toggle").click();
    await assertEnglish(page);
    await page.screenshot({ path: screenshotPath("mobile-en"), fullPage: true });

    expect(errors).toEqual([]);
  } finally {
    await context.close();
  }
});
