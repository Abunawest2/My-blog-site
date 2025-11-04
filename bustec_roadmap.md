# BUSTEC - Business & Technology Platform Roadmap

This document outlines the future vision and planned features for the blog platform to establish it as a premier destination for Business and Technology content.

## 1. Core Identity: BUSTEC

The platform's core identity will be **BUSTEC**, a portmanteau of Business and Technology. All branding, content, and features should align with this focus. The goal is to create a high-quality repository of articles, analyses, and case studies related to these two fields.

## 2. Hierarchical Content Categorization

To improve content discovery and organization, the current single-level category system will be evolved into a three-tiered hierarchical structure.

### 2.1. Structure Definition

1.  **Super Category:** The highest level of classification. There will be only two Super Categories:
    *   `BUSINESS`
    *   `TECHNOLOGY`

2.  **Sub Category:** A more specific area of focus within a Super Category.
    *   *Examples under BUSINESS:* Finance, Procurement, Human Resources, Banking, Marketing, Logistics.
    *   *Examples under TECHNOLOGY:* AI & Machine Learning, Software Development, Cybersecurity, Cloud Computing, Data Science.

3.  **Topic:** A specific, niche subject within a Sub Category.
    *   *Example under Finance:* "Corporate-Valuation-Models", "Algorithmic-Trading-Strategies".
    *   *Example under Software Development:* "CI-CD-Pipelines", "Microservices-Architecture".

### 2.2. Implementation Plan

*   **Model Changes:** The `Category` model will need to be refactored to support self-referencing foreign keys to create the parent-child relationships (Super -> Sub -> Topic).
*   **Admin Interface:** The Django admin panel will need to be updated to allow for easy management of this hierarchical structure.
*   **Frontend Display:** The UI will be redesigned to feature this new categorization, possibly with nested menus or breadcrumbs to show the user's location in the hierarchy.

## 3. Author Application & Onboarding

The author application process will be refactored to align with the new BUSTEC identity and content structure.

### 3.1. Genre Selection

*   During the application process (`/apply-to-write/`), prospective authors will be required to select a "Primary Genre" they wish to write for: **BUSINESS** or **TECHNOLOGY**.
*   This choice will help in vetting authors and aligning them with the appropriate content stream from the beginning.

### 3.2. Future Enhancements

*   The author's chosen genre could be displayed on their profile.
*   The system could recommend content or collaboration opportunities based on an author's genre.
