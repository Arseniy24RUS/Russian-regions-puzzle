const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 60000,
  expect: {
    timeout: 15000
  },
  use: {
    baseURL: "http://127.0.0.1:4185",
    trace: "retain-on-failure",
    screenshot: "only-on-failure"
  },
  webServer: {
    command: "npx http-server . -a 127.0.0.1 -p 4185 -c-1 --silent",
    url: "http://127.0.0.1:4185",
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  }
});
