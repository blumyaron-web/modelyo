import { defineConfig } from "allure";

export default defineConfig({
  name: "QA Automation Suite",
  output: "./reports/allure-report",
  plugins: {
    awesome: {
      options: {
        // Note: singleFile must be passed as --single-file CLI flag to `allure awesome`
        // It is NOT respected as a plugin config key. See workflow for usage.
        reportLanguage: "en",
      },
    },
  },
  categories: [
    {
      name: "Flaky tests",
      matchers: { flaky: true },
      groupBy: ["flaky"],
    },
    {
      name: "Product failures",
      matchers: { statuses: ["failed"] },
      groupBy: ["severity", "owner"],
      groupByMessage: true,
      expand: true,
    },
    {
      name: "Broken tests (infra/setup errors)",
      matchers: { statuses: ["broken"] },
      groupBy: ["layer"],
      expand: false,
    },
  ],
});
