**Process Summary**

* Fetches the latest SSD product updates from the TechPowerUp SSD Database by crawling the 'Recent Database Updates' section.
* Identifies new or recently edited products by reading update rows and filtering them based on a defined date window (e.g., last 7–10 days).
* Extracts product details, including brand, model name, and the URL for each updated SSD.
* Visits each product’s specification page to retrieve detailed hardware specs across different categories (controller, memory, performance, etc.).
* Parses and organizes the extracted specifications into structured data suitable for analysis and reporting.

Generates multiple CSV files for each product specification, including:
* A master list of all updated products
* Category-wise specification tables
* A root-object (brand-to-product) mapping
* Cleans, normalizes, and formats the data to ensure consistency across all outputs.
* Handles duplicates, missing values, and invalid rows to maintain accuracy in the generated datasets.
* Provides a fully automated weekly extraction pipeline, suitable for reporting, analytics, or integration into a larger data platform.
