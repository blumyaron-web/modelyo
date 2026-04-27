import { defineConfig } from "allure";

export default defineConfig({
  name: "QA Automation Suite",
  output: "./reports/allure-report",
  plugins: {
    awesome: {
      options: {
        // singleFile is great for email/Slack sharing but breaks GitHub Pages navigation.
        // Disabled here so gh-pages gets a full interactive report.
        // To produce a portable single file locally: npx allure generate --single-file
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
