# 📋 Innov8 Workflow Instructions

**Complete Guide for Using the Innov8 Business Planning Workspace**

---

## 🎯 Overview

This document provides step-by-step instructions for using the Innov8 workspace effectively. Whether you're creating a new company, starting a new project, or managing existing business planning activities, this guide will help you navigate the system efficiently.

---

## 🚀 Quick Start Guide

### For New Users

1. **Understand the Structure**: Review the main README.md to understand the workspace organization
2. **Identify Your Need**: Determine if you're setting up a company, project, or working with templates
3. **Follow Relevant Section**: Jump to the appropriate section in this guide
4. **Ask for Help**: Contact the system administrator if you need assistance

### Emergency Quick Start
If you need to start immediately:
1. Go to `companies/` folder
2. Create your company folder if it doesn't exist
3. Copy templates from `embryo/` that match your needs
4. Start customizing the templates for your business

---

## 🏢 Setting Up a New Company

### Step 1: Create Company Structure

1. **Navigate to Companies Directory**:
   ```bash
   cd companies/
   ```

2. **Create Company Folder**:
   ```bash
   mkdir [company-name]
   cd [company-name]
   ```

3. **Create Basic Company Documents**:
   ```bash
   # Copy from a reference company or create from scratch
   touch company-overview.md
   touch leadership.md
   mkdir projects/
   ```

### Step 2: Set Up Company Overview

1. **Create Company Overview**:
   - Use `companies/velocity/company-overview.md` as a template
   - Include company mission, vision, and business segments
   - Add contact information and leadership details

2. **Key Sections to Complete**:
   - Company Information
   - Business Segments
   - Mission & Vision
   - Leadership Team (even if preliminary)
   - Contact Information

### Step 3: Set Up Leadership Document

1. **Create Leadership Profile**:
   - Use `companies/velocity/leadership.md` as a template
   - Document current and planned leadership roles
   - Include advisory board information

2. **Include**:
   - Current team members
   - Planned hires
   - Advisory board members
   - Compensation philosophy

### Step 4: Create Projects Directory Structure

1. **Set Up Projects Folder**:
   ```bash
   mkdir projects/
   ```

2. **Ready for Projects**: Your company structure is now ready for individual projects

---

## 🚀 Starting a New Project

### Step 1: Create Project Structure

1. **Navigate to Company Projects**:
   ```bash
   cd companies/[company-name]/projects/
   ```

2. **Create Project Folder**:
   ```bash
   mkdir [project-name]
   cd [project-name]
   ```

3. **Create Workspace Structure**:
   ```bash
   mkdir workspace/
   cd workspace/
   mkdir business-planning/ funding-docs/ market-research/ technical-documents/ operations/
   ```

### Step 2: Select Appropriate Templates

1. **Determine Business Stage**:
   - **Seed Stage**: Early stage, seeking first funding
   - **Series A**: Have traction, seeking growth capital
   - **Growth Stage**: Scaling business, later-stage funding

2. **Determine Business Type**:
   - **Infrastructure/Telco**: Telecom, utilities, heavy infrastructure
   - **SaaS/Software**: Software products and services
   - **Service Business**: Professional services, consulting
   - **Manufacturing**: Production and manufacturing

3. **Select Frameworks**:
   - **Business Model Canvas**: Overall business model design
   - **Lean Canvas**: Startup validation focus
   - **Financial Projections**: Detailed financial planning

### Step 3: Copy Templates to Workspace

1. **Copy Business Stage Template**:
   ```bash
   cp embryo/business-stages/[stage]-template.md workspace/business-planning/
   ```

2. **Copy Business Type Template**:
   ```bash
   cp embryo/business-types/[type]-template.md workspace/business-planning/
   ```

3. **Copy Framework Templates**:
   ```bash
   cp embryo/frameworks/business-model-canvas-template.md workspace/business-planning/
   cp embryo/resources/financial-projections-template.md workspace/business-planning/
   ```

### Step 4: Create Project Overview

1. **Create Project Overview Document**:
   - Use existing project overviews as templates
   - Include project scope, objectives, and timeline
   - Document current status and next steps

2. **Key Sections**:
   - Project Summary
   - Project Scope
   - Current Status
   - Key Milestones
   - Team & Organization
   - Contact Information

---

## 📝 Working with Templates

### Template Selection Guide

| Business Stage | Business Type | Recommended Templates |
|----------------|---------------|----------------------|
| Seed | Infrastructure/Telco | seed-stage + infrastructure-telco + business-model-canvas + financial-projections |
| Seed | SaaS | seed-stage + saas-template + lean-canvas + financial-projections |
| Series A | Infrastructure/Telco | series-a + infrastructure-telco + business-model-canvas + financial-projections |
| Growth | Any Type | growth-stage + [type-specific] + okr-planning + financial-projections |

### Customization Process

1. **Review Template Structure**: Understand all sections and requirements
2. **Gather Information**: Collect all necessary business information
3. **Fill in Brackets**: Replace all `[text]` placeholders with specific information
4. **Add Company Details**: Customize for your specific business context
5. **Review and Refine**: Ensure consistency and completeness

### Template Customization Best Practices

1. **Be Specific and Realistic**:
   - Use actual numbers rather than vague estimates
   - Provide evidence for market size and growth claims
   - Include realistic timelines and resource requirements

2. **Maintain Professional Tone**:
   - Use business-appropriate language
   - Avoid overly casual or unprofessional phrasing
   - Ensure consistency across all documents

3. **Focus on Differentiators**:
   - Highlight what makes your business unique
   - Emphasize competitive advantages
   - Clearly articulate your value proposition

4. **Include Supporting Data**:
   - Provide sources for market research
   - Include financial assumptions and methodologies
   - Document key metrics and their calculation methods

---

## 🔄 Document Management

### File Organization

1. **Naming Conventions**:
   - Use lowercase with hyphens: `business-plan.md`
   - Include dates for version control: `pitch-deck-2025-11-02.md`
   - Be descriptive: `market-analysis-q1-2025.md`

2. **Folder Structure**:
   - Keep related documents together
   - Use standard workspace folders consistently
   - Archive old versions when updating

3. **Version Control**:
   - Maintain document history
   - Use dates or version numbers in filenames
   - Keep change logs for important documents

### Cross-Referencing

1. **Internal Links**:
   ```markdown
   See [Financial Projections](financial-projections.md) for detailed forecasts.
   Refer to [Market Analysis](../market-research/competitive-analysis.md) for competitor details.
   ```

2. **Template References**:
   ```markdown
   Based on [Infrastructure/Telco Template](../../../embryo/business-types/infrastructure-telco-template.md)
   Customized from [Seed Stage Template](../../../embryo/business-stages/seed-stage-template.md)
   ```

3. **Company-Level References**:
   ```markdown
   See [Company Overview](../../company-overview.md) for company details.
   Refer to [Leadership Team](../../leadership.md) for team information.
   ```

---

## 👥 Collaboration Workflow

### Team Access Management

1. **Determine Access Needs**:
   - Who needs read access?
   - Who needs edit access?
   - Who needs administrative access?

2. **Set Up Permissions**:
   - Use appropriate file sharing tools
   - Set folder-level permissions where possible
   - Document access decisions

3. **Access Review**:
   - Regularly review who has access
   - Remove access when team members leave
   - Update permissions as roles change

### Review and Approval Process

1. **Document Review**:
   - Assign reviewers for each document type
   - Set review timelines
   - Use review checklists

2. **Approval Workflow**:
   - Define approval requirements
   - Document approval decisions
   - Maintain approval records

3. **Feedback Integration**:
   - Collect feedback systematically
   - Track suggested changes
   - Document final decisions

### Communication Protocols

1. **Document Status Updates**:
   - Regular status meetings
   - Progress reports
   - Blocker identification and resolution

2. **Change Notifications**:
   - Notify team of document updates
   - Explain reasons for changes
   - Provide implementation timelines

---

## 📊 Quality Assurance

### Document Review Checklist

1. **Completeness**:
   - [ ] All sections filled out
   - [ ] No placeholder text remaining
   - [ ] All required documents created

2. **Accuracy**:
   - [ ] Financial calculations correct
   - [ ] Market data current and sourced
   - [ ] Team information accurate

3. **Consistency**:
   - [ ] Numbers consistent across documents
   - [ ] Terminology consistent
   - [ ] Formatting consistent

4. **Professionalism**:
   - [ ] Grammar and spelling checked
   - [ ] Professional tone maintained
   - [ ] Appropriate for investor audience

### Validation Process

1. **Internal Review**:
   - Team members review documents
   - Cross-check calculations and data
   - Validate assumptions and methodology

2. **External Review**:
   - Advisors review key documents
   - Mentors provide feedback
   - Legal/financial professional review where appropriate

3. **Final Validation**:
   - CEO/final approver review
   - Board approval if required
   - Investor feedback incorporation

---

## 🚨 Troubleshooting

### Common Issues

1. **Template Not Found**:
   - Check embryo directory structure
   - Verify template filename
   - Contact system administrator

2. **Permission Issues**:
   - Check folder permissions
   - Verify user access rights
   - Contact IT support

3. **Document Link Errors**:
   - Verify file paths
   - Check file existence
   - Update broken links

4. **Version Conflicts**:
   - Use clear version naming
   - Document change history
   - Resolve conflicts systematically

### Getting Help

1. **Documentation**:
   - Review this workflow guide
   - Check template documentation
   - Review README.md files

2. **Team Support**:
   - Ask team members for help
   - Consult with document owners
   - Schedule review meetings

3. **System Administrator**:
   - Contact for technical issues
   - Report system problems
   - Request feature enhancements

---

## 📅 Maintenance Schedule

### Regular Tasks

**Weekly**:
- Review document status updates
- Check for new template needs
- Update project progress

**Monthly**:
- Review template usage
- Update financial projections
- Check document consistency

**Quarterly**:
- Comprehensive system review
- Template updates and improvements
- User feedback collection

**Annually**:
- Major template updates
- System structure review
- Best practices documentation

### Template Maintenance

1. **Review Templates**:
   - Assess relevance and completeness
   - Update industry benchmarks
   - Incorporate user feedback

2. **Create New Templates**:
   - Identify new business types
   - Develop additional frameworks
   - Expand resource library

3. **Version Management**:
   - Maintain template version history
   - Document changes and improvements
   - Communicate updates to users

---

## 📚 Additional Resources

### Training Materials
- **Template Guides**: Individual template instructions
- **Best Practices**: Industry-specific guidance
- **Examples**: Sample completed documents
- **Videos**: Walkthrough tutorials (if available)

### External Resources
- **Business Planning Tools**: Recommended software and platforms
- **Industry Reports**: Market research sources
- **Professional Services**: Legal, financial, and consulting contacts
- **Funding Resources**: Investor networks and platforms

### Community
- **User Groups**: Internal user communities
- **Best Practice Sharing**: Success stories and lessons learned
- **Feedback Channels**: How to provide input and suggestions
- **Support Network**: Who to contact for different types of help

---

*This workflow guide is designed to help you navigate the Innov8 system effectively. Regular updates and improvements will be made based on user feedback and system evolution.*

*Last Updated: November 2025*
*Next Review: Monthly*