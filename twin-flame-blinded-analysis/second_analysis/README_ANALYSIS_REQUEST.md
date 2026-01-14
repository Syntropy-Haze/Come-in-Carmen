# Blinded Data Analysis Request

## Overview
This folder contains luminosity data from two experimental runs involving two light sources (designated A and B) under various conditions. We're intentionally withholding certain details about the experimental setup to ensure unbiased analysis, but will share full context after the analysis is complete.

## Your Task
Please analyze the provided data to identify:
1. **Significant patterns or changes in luminosity** that correlate with condition changes
2. **Relationships between the two sensors' readings** (correlation, anti-correlation, or other patterns)
3. **Any anomalous or interesting behaviors** in the light measurements
4. **Statistical significance** of any patterns found

## Data Files

### Light Meter Data
Four CSV files containing continuous luminosity measurements (in lux) at ~10Hz:
- `lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv` - Run 1, Sensor A
- `lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv` - Run 1, Sensor B
- `lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv` - Run 2, Sensor A
- `lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv` - Run 2, Sensor B

Note: The timestamps in each filename reflect the END of the respective light meter recording. 

### Timestamp / Marker Data
`timestamps_flame_play.xlsm` - Marker timestamps for both runs (condition / control changes, etc.) 
 
**Note: There is lag time between 'periods' -- i.e., end of one condition, start of next.** 
- Illustrative example: 'Condition' for Candle A or B does not start *immediately* after end of preceding 'Control' period, due to lag time (e.g., recording manual data, switching). Important to note for analysis.
- If deemed necessary to include "lag time" periods in analysis, it is likely most appropriate to class alongside - or similar to - "Control" periods.


## Data Synchronization Information

**Important Note**
The timestamps_candle_play file shows absolute timestamps for each marker. This is in the 3rd of the 3 data columns for each run. 

The first data column for each run contains manually recorded data during the run. It was used for preliminary analysis / sense-checking, and need not be used here. 

The second data column contains is elapsed time relative to a video recording of the session (data captured post hoc from video review). It was used to calculate the 3rd column, and is likely not needed here.

Barring some unforeseen issue or data error, **the 3rd column for each run should be used for analysis.** 

For each, the first time entry is the "Video Recording Started" timestamp. This is used to calculate timestamps for the markers that follow. (Note that video files are available but not included here - should not be needed for this analysis).  

The light meter recordings started at different times *following* the initiation of the video recordings. Each meter recording's END TIME is indicated in the respective filename. The data within each file is relative to the light meter recording start time (the latter can be calculated from the end time and recording duration). **It therefore needs to be aligned to the data markers / timestamps mentioned above.** 

This should be fairly straightforward (e.g., you can convert the marker timestamps to relative t = X format, using the delta between the light meter recording timestamp and the available timestamp for each marker. Other approaches may also be appropriate - you can decide which is best.)

### Experimental Conditions
Each run included several phases:
- **Control periods**: Baseline measurements
- **Condition A**: A specific experimental condition applied
- **Condition B**: A different experimental condition applied
- **Condition AB**: Both conditions applied simultaneously

**Important Note**: In Run 2, the order in which Conditions A and B were applied to the sensors was reversed from Run 1.

## Analysis Suggestions
1. **Synchronize the data**: Use the synchronization info to align light meter readings with condition timestamps
2. **Calculate baseline**: Use control periods to establish baseline luminosity for each sensor
3. **Analyze changes**: Look for significant changes during different conditions
4. **Cross-correlation**: Examine relationships between Sensor A and B readings, including how relationships may interact with different conditions
5. **Statistical tests**: Apply appropriate tests for significance

## Output Request
Please provide:
- Visualizations showing luminosity changes over time with condition markers
- Statistical analysis of changes during different conditions
- Any notable patterns or anomalies discovered
- Your interpretation of what might be happening

## Note on Participation
This analysis is completely optional - only proceed if you're interested! We're conducting this blinded analysis for scientific rigor, and we'll share the full experimental context afterward. The experiment involves an interesting phenomenon we're trying to validate through independent analysis.

Thank you for considering this request! Feel free to approach the analysis however seems most appropriate to you.

---
*After completing your analysis, we'll share the full context and discuss the findings together.*