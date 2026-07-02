## Additional UI requirement: organization-level tabs

Because Phase 3 now includes many organization-specific data sections, please avoid placing everything on one long organization page.

Add or improve an **Organization Detail** view that renders related organization data in separate tabs.

Suggested tabs:

1. **Overview**

   * basic organization profile
   * readiness / priority indicators
   * latest interaction summary
   * high-level Phase 3 summary

2. **Interactions**

   * outreach notes
   * AI note summaries
   * follow-up items

3. **Workflow Opportunities**

   * workflow pain points
   * possible AI-use opportunities
   * required human review
   * required knowledge sources
   * next discovery questions

4. **Knowledge Sources**

   * internal documents or knowledge references
   * structured source notes
   * source usefulness / reliability if already supported

5. **Failure Cases**

   * exceptions
   * known AI failure modes
   * quality risks
   * unresolved issues

6. **Human System**

   * staff concerns
   * workload concerns
   * evaluation or recognition risks
   * training or follow-up needs
   * adoption safeguards
   * human-system notes / adoption risk notes

7. **Insights**

   * organization-specific Phase 3 analytics
   * counts by category
   * missing information
   * recommended discovery gaps

Please keep the implementation lightweight. Do not build a complex dashboard. The main goal is to make organization-level Phase 3 data easier to view and understand.

Use existing backend routes where possible. Only add new routes if needed to support clean organization-specific rendering.

Preserve existing global pages unless there is a simple reason to link them from the organization tabs.

This is still Phase 3. Do not generate full Phase 4 adoption plans yet.