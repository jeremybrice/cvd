# **Jira Story Format Guide**

## **Overview**

This guide outlines the preferred format for Jira stories. Each story should include five structured sections in the exact order shown below.

## **Story Structure**

### **1\. Story Title**

* **Format**: Brief, action-oriented description  
* **Length**: Keep it concise \- typically 5-10 words  
* **Style**: Can use "As a \[user\]..." format OR simple directive format  
* **Examples**:  
  * "Enable Managers to Start Unstarted Routes"  
  * "Fix Static Schedule Disruption from Off-Schedule Services"  
  * "Add Email Statement Functionality to Account Summary"

### **2\. Background / Context**

* **Purpose**: Explain why this story exists  
* **Content**: Include:  
  * Current system behavior  
  * Problem or limitation being addressed  
  * Business impact or user pain points  
  * Any relevant meeting references or strategic goals  
* **Length**: 1-2 paragraphs  
* **Example**: "Currently, the Stock App prevents managers and supervisors from starting any route once a single route within their branch has been started by any driver. This creates operational challenges when a driver calls in sick or is unavailable..."

### **3\. Feature Requirements / Functional Behavior**

Split into two distinct subsections:

#### **UI Behavior**

* **Content**: Detail how the feature appears and behaves on-screen  
* **Include**:  
  * New UI elements and their placement  
  * User interactions and workflows  
  * Visual feedback and states  
  * Modal behaviors, tooltips, and messages  
* **Format**: Use bullet points for clarity

#### **System Logic**

* **Content**: Describe backend handling and business rules  
* **Include**:  
  * Data processing and validation  
  * Integration points and API behavior  
  * State management and triggers  
  * Edge case handling  
  * Permission and security considerations  
* **Format**: Use bullet points for clarity

### **4\. Acceptance Tests**

* **Format**: Each test should include:  
  * **Test name**: Descriptive title  
  * **Steps**: Numbered list of actions  
  * **Expected Result**: Clear outcome  
* **Quantity**: Include 4-6 tests covering:  
  * Happy path scenarios  
  * Edge cases  
  * Error conditions  
  * Permission/validation checks  
* **Style**: Write in imperative mood, be specific about values  
* **Example Structure**:

\*\*Test 1: Setting Toggle and Default State\*\*  
\* \*\*Steps\*\*:  
  1\. Navigate to Company Settings → OCS tab  
  2\. Verify "Auto-Delete Zero Value Invoices" setting appears  
  3\. Check default state  
\* \*\*Expected Result\*\*: Setting is present and toggled OFF by default

### **5\. Technical Notes / Considerations**

* **Content**: Implementation guidance and technical details  
* **Include**:  
  * Database changes needed  
  * API modifications  
  * Performance considerations  
  * Migration requirements  
  * Integration dependencies  
  * Future enhancement ideas  
* **Format**: Use bullet points  
* **Tone**: Written for engineering team

## **Best Practices**

### **General Guidelines**

1. **Be Specific**: Use real examples, actual field names, and specific values  
2. **Avoid Ambiguity**: Don't leave implementation details to interpretation unless explicitly intended  
3. **Consider Edge Cases**: Think about what could go wrong and address it  
4. **Include Validation**: Specify min/max values, required fields, and error handling

### **Common Patterns**

1. **Settings/Toggles**: Always specify default state (usually OFF)  
2. **Bulk Operations**: Include both single and bulk operation tests  
3. **Date/Time Features**: Consider timezone implications  
4. **Permissions**: Clarify role-based access when relevant  
5. **UI Elements**: Specify exact placement (e.g., "between X and Y buttons")

### **Writing Style**

* Use present tense for current behavior  
* Use future tense or imperative for desired behavior  
* Be concise but thorough  
* Include specific examples with real data  
* Avoid technical jargon in Background section

## **Examples of Well-Written Sections**

### **Clear UI Behavior Example:**

\* Add "Previous" and "Next" buttons centered at the bottom of the modal  
  \- Previous button: disabled when viewing oldest files  
  \- Next button: disabled when viewing most recent files (initial state)  
\* Add "Jump to Date" feature on bottom left with calendar icon  
  \- Clicking opens date picker calendar  
  \- Calendar shows current month with ability to navigate months/years

### **Clear System Logic Example:**

\* Delete invoice only when ALL of the following conditions are met:  
  \- Every line item has quantity \= 0  
  \- Invoice total \= $0.00  
  \- Company has "Auto-Delete Zero Value Invoices" enabled  
\* Invoices with service fees, partial deliveries, or free products are preserved

### **Clear Test Example:**

\*\*Test 3: Jump to Date \- Files Found\*\*  
\* \*\*Steps\*\*:  
  1\. Open modal and click "Jump to Date"  
  2\. Select June 1, 2025 from calendar  
  3\. Click "Today" button  
\* \*\*Expected Result\*\*:   
  \- Modal displays 3 files starting from June 1  
  \- "Today" button returns to 3 most recent files

## **Template**

\*\*Story Title\*\*    
\*\*\[Concise Action-Oriented Title\]\*\*

\---

\*\*Background / Context\*\*    
\[1-2 paragraphs explaining current state, problem, and why this change is needed\]

\---

\*\*Feature Requirements / Functional Behavior\*\*

\*\*UI Behavior\*\*  
\* \[Bullet points describing user interface changes and interactions\]  
\* \[Include all visual elements, their placement, and behavior\]

\*\*System Logic\*\*  
\* \[Bullet points describing backend processing and business rules\]  
\* \[Include validation, calculations, and data handling\]

\---

\*\*Acceptance Tests\*\*

\*\*Test 1: \[Descriptive Test Name\]\*\*  
\* \*\*Steps\*\*:  
  1\. \[First action\]  
  2\. \[Second action\]  
  3\. \[Third action\]  
\* \*\*Expected Result\*\*: \[Clear description of expected outcome\]

\[Include 4-6 tests total\]

\---

\*\*Technical Notes / Considerations\*\*  
\* \[Technical implementation details\]  
\* \[Database or API changes\]  
\* \[Performance considerations\]  
\* \[Edge cases to handle\]

## **When to Ask Clarifying Questions**

Before writing a story, clarify:

* Specific behavior for edge cases  
* Default values and states  
* Permission/access requirements  
* Integration with existing features  
* Performance requirements or constraints  
* Audit/logging requirements

Don't assume implementation details \- if the requirement doesn't specify, ask\!

