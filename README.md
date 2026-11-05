# GreenLCC India: course project submission

**GreenLCC India** finds the cheapest way, over a building's whole life, to reach an IGBC green rating, and measures how safe that answer is.
Course project for CM 617 / CE 725, Topic 6: Life Cycle Cost Analysis (LCCA) decision tool.

## Run the tool on your own PC

1. Install **Python 3.10 or newer** (tick "Add python.exe to PATH" on Windows).
2. Download this repository (green **Code** button, then **Download ZIP**) and unzip it to a **short folder**, for example `C:\GreenLCC`.
3. Open the `GreenLCC_Tool` folder and double-click **`Start_GreenLCC.bat`**. The first run sets up its own environment (3 to 5 minutes, internet needed); later runs start in seconds.
4. The tool opens in your browser at `http://localhost:8501`. On the Home page click **Try the Pune demo**, then follow the **Next** buttons.

Mac or Linux: run `sh start_greenlcc.sh` inside `GreenLCC_Tool`. Full instructions and troubleshooting are in [`GreenLCC_Tool/START_HERE.txt`](GreenLCC_Tool/START_HERE.txt).
The same tool is also in `GreenLCC_Tool_Source.zip`.

## What is in this repository

| File | What it is |
|---|---|
| [`GreenLCC_Tool/`](GreenLCC_Tool) | The working tool: source code, demo input workbook, tests and start scripts |
| [`GreenLCC_Tool_Source.zip`](GreenLCC_Tool_Source.zip) | The same tool as one zip file for reviewers |
| [`1_About_the_Tool.pdf`](1_About_the_Tool.pdf) | What the tool is about: problem, users, demo result, course links |
| [`2_User_Guide.pdf`](2_User_Guide.pdf) | How to start it, each screen with screenshots, reading the results, troubleshooting |
| [`3_How_the_Tool_Works.pdf`](3_How_the_Tool_Works.pdf) | The method, a worked example, the checks and the limits |
| [`4_AI_Log.pdf`](4_AI_Log.pdf) | Log of the 35 changes made to the tool, with category and rationale |
| [`5_AI_Usage_Log_Annexure_A.pdf`](5_AI_Usage_Log_Annexure_A.pdf) | AI usage log: prompts, outputs, accept / modify / reject, verification |
| [`6_Validation_Report.pdf`](6_Validation_Report.pdf) | Hand benchmark versus the tool, discrepancies and how each was resolved |
| [`Validation_Benchmark.xlsx`](Validation_Benchmark.xlsx) | The independent Excel benchmark (live formulas) behind the validation report |
| [`Documents/GreenLCC_Glossary.pdf`](Documents/GreenLCC_Glossary.pdf) | Every term the tool uses, with its meaning and course link |

## Data status

The demo is a 12,000 m² Pune office. Prices and tariffs are sourced estimates and the IGBC point tables are illustrative. Replace them with real project data before relying on the results.
