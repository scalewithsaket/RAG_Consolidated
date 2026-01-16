# QA Automation Knowledge Transfer (KT) - 2024

## 1. Technical Stack

- **Framework:** Playwright (Version 1.40+)
- **Language:** TypeScript
- **Runtime:** NodeJS 20.x
- **Test Runner:** Playwright Built-in Runner

## 2. Testing Scope

- **Primary Focus:** End-to-End (E2E) testing for the 'Alpha' Web Portal.
- **Integration Testing:** Covered via API request context in Playwright.
- **Unit Testing:** **NOT** covered in this document. Refer to the 'Jest Framework Guidelines' for unit testing.

## 3. Prohibited Tools & Practices

- **Selenium:** Strictly prohibited. All legacy Selenium scripts must be migrated to Playwright by Q3.
- **Hardcoding:** No hardcoded credentials. Use the `GlobalSetup.ts` for environment variables.

## 4. Reporting

- **Tools:** Allure Reports
- **Retention:** Reports are stored in the S3 bucket 'qa-reports-prod' for 30 days.
