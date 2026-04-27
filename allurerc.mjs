import { defineConfig } from "allure";

export default defineConfig({
  name: "QA Automation Suite",
  output: "./reports/allure-report",
  plugins: {
    awesome: {
      options: {
        // Self-contained single file — easy to attach as CI artifact
        singleFile: true,
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
