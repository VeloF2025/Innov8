# 📦 VeloCity Financial Models Archive

**Status:** Historical Reference Only
**Date Archived:** November 3, 2025
**Reason:** Replaced by Realistic OPEX Model (Master Version)

---

## 🗂️ Archive Contents

### **old_models/ Directory**

This archive contains the original financial model iterations that have been superseded by the Realistic OPEX Model.

#### **VELOCITY_COMPLETE_MODEL.md**
**Original Date:** November 2, 2025
**Status:** SUPERSEDED - Archived for reference

**Model Characteristics:**
- Single OPEX assumption: R1.977M/month per 10K door project
- Staffing model: 39 full-time employees per project
- Scaling assumption: Linear (4 projects = 4× OPEX)
- Single project base case yield: 4.4% annual
- Portfolio Year 3 yield: 28.9% annual
- Payback period: 22.8 years

**Key Findings from This Model:**
- Only 1 of 12 scenarios showed positive returns
- Most scenarios lost money regardless of penetration
- Portfolio approach only partially saved the model
- Not investment-ready in this form

#### **VELOCITY_SCENARIO_ANALYSIS.csv**
**Original Date:** November 1, 2025
**Status:** SUPERSEDED - Archived for reference

**Contents:**
- 12 single-project scenarios based on original OPEX
- Portfolio analysis with limited scaling benefits
- Sensitivity analysis for the original cost structure
- All scenarios showed weak returns due to high OPEX

---

## 🔄 Why the Old Model Was Replaced

### **Critical Problems Identified**

1. **Unrealistic OPEX Assumptions**
   - R1.977M/month per project assumed 39 full-time employees per 10K doors
   - For 4 projects: 156 people (unrealistic)
   - For 24 projects: 936 people (completely unrealistic)

2. **Linear Scaling Model**
   - Each additional project duplicated entire cost structure
   - No consideration for shared management, technical, or customer service teams
   - Prevented profitable scaling

3. **Poor Project Economics**
   - Single projects showed only 4.4% yield (not viable alone)
   - Required portfolio of multiple projects to achieve viability
   - Payback period of 22.8 years (unacceptable for infrastructure investment)

4. **Weak Portfolio Performance**
   - Year 3 yield of 28.9% (below infrastructure investment standards)
   - Not compelling for institutional investors
   - Risk/return ratio unfavorable

---

## ✅ The Solution: Realistic OPEX Model

The old models were completely rebuilt with realistic operational assumptions:

### **Key Changes**

| Component | Old Model | New Model | Impact |
|-----------|-----------|-----------|--------|
| **OPEX/Project** | R1.977M | R400K (Y1) | -80% reduction |
| **Staff/Project** | 39 | 4-6/10K homes | -85% reduction |
| **Scaling Model** | Linear | Hub & Spoke | Exponential efficiency |
| **Single Yield** | 4.4% | 60.4% | +1,273% improvement |
| **Portfolio Y3** | 28.9% | 66.7% | +131% improvement |
| **Payback Period** | 22.8 years | 1.7 years | 92% faster |

### **New Operational Model**

**Hub & Spoke Architecture:**
- Regional hub manager oversees 4-5 projects
- Shared technical, financial, and customer service teams
- Contractor field operations (fixed pre-80%, performance-based post-80%)
- Only 15-25 people for Year 1 (4 projects)
- Scales to 65-70 people by Year 3 (24 projects)

**Contractor Field Operations:**
- Pre-80% activation: Fixed R60K/month per project
- Post-80% activation: R10 per activated ONT per month
- Aligns incentives with customer acquisition

---

## 📍 Master Model Location

The new Realistic OPEX Model (Master Version) is located in the parent directory:

**Location:** `/financial-models/`

**Key Files:**
- `VELOCITY_REALISTIC_OPEX_MODEL.md` ⭐ **MAIN OPERATIONAL DOCUMENT**
- `VELOCITY_SCENARIO_ANALYSIS_REALISTIC.csv` ⭐ **SPREADSHEET FORMAT**
- `MODEL_TRANSFORMATION_SUMMARY.md` ⭐ **BEFORE/AFTER ANALYSIS**
- `README.md` ⭐ **MASTER INDEX**

---

## 🔗 References

### **For Understanding the Evolution**
→ See `/financial-models/MODEL_TRANSFORMATION_SUMMARY.md`
- Complete before/after comparison
- Business case for the new model
- Problem identification and solution
- Key business insights

### **For Investor Presentations**
→ See `/investor-materials/VELOCITY_INFRASTRUCTURE_YIELD_INVESTMENT.md`
- Updated with realistic OPEX assumptions
- 60.4% - 77.1% annual yields
- Professional investment presentation format

### **For Operational Planning**
→ See `/financial-models/VELOCITY_REALISTIC_OPEX_MODEL.md`
- Year 1-3 detailed staffing breakdown
- Contractor cost management
- Hub & Spoke implementation roadmap
- Staff growth trajectory

---

## ⚠️ Important Notes

### **These Files Are Archived**
- Use for **historical reference only**
- Do **NOT** use for new investor presentations
- Do **NOT** base operational decisions on these models
- Do **NOT** quote yields from these models (they are outdated)

### **When to Reference Archive**
✅ Understanding how the model evolved
✅ Reviewing previous assumptions and decisions
✅ Historical documentation and records
✅ Validation of transformation impact

### **When NOT to Use Archive**
❌ Investor pitches (use Master Model)
❌ Operational planning (use Master Model)
❌ Financial forecasting (use Master Model)
❌ Public communications (use Master Model)

---

## 📊 Quick Comparison

### **Old Model Results**
```
Single Project (7K @ R10/day):
  Monthly Revenue:  R2.1M
  Monthly OPEX:     R1.977M
  Monthly Profit:   R123K
  Annual Yield:     4.4%
  Status:           ❌ Marginal/Not Viable

Portfolio (24 projects Year 3):
  Portfolio Yield:  28.9%
  Status:           ⚠️ Weak by infrastructure standards
```

### **New Model Results**
```
Single Project (7K @ R10/day):
  Monthly Revenue:  R2.1M
  Monthly OPEX:     R400K
  Monthly Profit:   R1.7M
  Annual Yield:     60.4%
  Status:           ✅ Exceptional

Portfolio (24 projects Year 3):
  Portfolio Yield:  66.7%
  Status:           ✅ Strong infrastructure investment
```

---

## 📁 Archive Structure

```
archive/
├── README.md (this file)
└── old_models/
    ├── VELOCITY_COMPLETE_MODEL.md          (Old comprehensive model)
    └── VELOCITY_SCENARIO_ANALYSIS.csv      (Old scenario analysis)
```

---

**Archive Status:** ✅ Complete and Organized
**Retention Policy:** Keep for historical reference indefinitely
**Last Updated:** November 3, 2025

---

*This archive preserves the evolution of VeloCity's financial modeling. The breakthrough came from questioning the original OPEX assumptions and redesigning the operational structure from linear scaling to Hub & Spoke efficiency.*
