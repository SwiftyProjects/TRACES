# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Operational Guide**

## Cell Dependencies and Execution Flows

### Initial Setup/Modification

**Full Sequential Execution (1-6) Required When:**
- Performing first-time setup
- Modifying any functions
- Adjusting core parameters
- Implementing new methods
- Updating visualization components

### *Standard Analysis Workflows*

#### Minimum Required Flow
1. **Cell 1** (Setup & Environment) - *Always Required*
2. **Cell 6** (Full Analysis) - *Primary Execution*

#### Targeted Analysis Options

**Visualization Focus:**
- Cell 1 → Cell 5
- Enables all visualization capabilities
- Requires relationship matrix parameter alignment (even number of top pairs)

**Method Comparison:**
- Cell 1 → Cell 4
- Focuses on correlation method analysis

### Use Case Scenarios

#### A. Complete Dataset Analysis
1. Sequential execution: Cells 1 → 2 → 3 → 4 → 5 → 6
2. Provides:
   - Comprehensive correlation analysis
   - Full visualization suite
   - Detailed statistical insights
   - Relationship classifications

#### B. Visualization Exploration
1. Execute: Cell 1 → Cell 4 → Cell 5
2. Delivers:
   - Correlation comparisons
   - Relationship matrix (top N pairs)
   - Method performance analysis
   - CCF pattern visualization

#### C. Methodology Validation
1. Required: Cells 1-4
2. Useful for:
   - Testing correlation methods
   - Validating classifications
   - Assessing confidence metrics

### _Important Notes_

**State Management:**
- Notebook maintains state until kernel reset
- Cell 6 contains consolidated function calls
- Parent-child relationships persist through session

**Performance Considerations:**
- Clear outputs between analysis runs
- Restart kernel when modifying parent-child mappings
- Consider batch processing for large datasets
- Relationship matrix visualization optimized for even number of top pairs

**Best Practices:**
- Validate data structure before full analysis
- Monitor memory usage with large datasets
- Review visualization parameters for optimal display
- Ensure correlation pair count aligns with visualization requirements