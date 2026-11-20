// pages_part1.js: Cover, TOC, Executive Summary, Research Methodology & Evidence Log

module.exports = [
  // PAGE 1: COVER
  {
    num: 1,
    header: 'COVER PAGE',
    isCover: true,
    content: `
      <div class="cover-wrapper">
        <div class="cover-top-bar">
          <span class="cover-org">TEXAS PROPERTY INTELLIGENCE INITIATIVE</span>
          <span class="cover-doc-id">DOC-TX-PROP-2026-V1</span>
        </div>
        <div class="cover-hero">
          <div class="cover-pill">STRATEGIC PRODUCT SPECIFICATION &amp; SYSTEM BLUEPRINT</div>
          <h1 class="cover-main-title">Texas Property Search and Management Platform</h1>
          <h2 class="cover-sub-title">A Unified Ecosystem for Cadastral Parcel Intelligence, Residential Discovery, and Rental Portfolio Automation</h2>
          <div class="cover-line"></div>
          <p class="cover-intro">
            A comprehensive, plain-language product proposal and operational delivery roadmap designed from first principles 
            for the State of Texas. Integrates 254-county land boundary mapping, MLS residential search, digital tenant screening, 
            e-signature lease management, and automated rent collection into an all-in-one property ecosystem.
          </p>
        </div>

        <div class="cover-meta-grid">
          <div class="meta-box">
            <span class="meta-label">TARGET JURISDICTION</span>
            <span class="meta-val">State of Texas (254 Counties &amp; 253 Appraisal Districts)</span>
          </div>
          <div class="meta-box">
            <span class="meta-label">DOCUMENT AUDIENCE</span>
            <span class="meta-val">Executive Leadership, Strategic Clients &amp; Operations</span>
          </div>
          <div class="meta-box">
            <span class="meta-label">PREPARED BY</span>
            <span class="meta-val">Senior Product Analyst &amp; Software System Designer</span>
          </div>
          <div class="meta-box">
            <span class="meta-label">PUBLICATION DATE</span>
            <span class="meta-val">November 2026 | Version 1.0 Final</span>
          </div>
        </div>

        <div class="cover-callout">
          <div class="callout-title">Executive Briefing &amp; Strategic Purpose</div>
          <p>
            Texas real estate operates under unique legal, geographic, and institutional conditions—including strict non-disclosure 
            statutes, decentralized county appraisal districts, overlapping special taxing jurisdictions (MUDs), dominant mineral estates, 
            and extensive agricultural valuations. This document outlines how a modern, independent technology platform can address 
            these realities by fusing deep land mapping intelligence with consumer marketplace discovery and full-cycle property management.
          </p>
        </div>

        <div class="cover-bottom-bar">
          <span>Confidential &amp; Proprietary</span>
          <span>Prepared for Executive Planning</span>
          <span>Texas Real Estate Innovation</span>
        </div>
      </div>
    `
  },

  // PAGE 2: TABLE OF CONTENTS & DOCUMENT GUIDE
  {
    num: 2,
    header: 'TABLE OF CONTENTS & DOCUMENT ARCHITECTURE',
    content: `
      <div class="section-title-group">
        <div class="section-badge">NAVIGATION</div>
        <h2 class="section-heading">Table of Contents &amp; Executive Reading Guide</h2>
      </div>

      <div class="toc-grid">
        <div class="toc-column">
          <div class="toc-item">
            <span class="toc-num">01</span>
            <div class="toc-text">
              <span class="toc-title">Executive Summary &amp; Product Purpose</span>
              <span class="toc-desc">Market opportunity, dual-paradigm problem, unified vision, and high-level value proposition.</span>
            </div>
            <span class="toc-page">Page 3</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">02</span>
            <div class="toc-text">
              <span class="toc-title">Research Methodology &amp; Evidence Log</span>
              <span class="toc-desc">Evaluation of public platforms, evidence classification (Confirmed, Inferred, Unknown), and findings log.</span>
            </div>
            <span class="toc-page">Page 4</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">03</span>
            <div class="toc-text">
              <span class="toc-title">User Types, Personas &amp; Operational Goals</span>
              <span class="toc-desc">Profiles, permissions, and goals for buyers, renters, land seekers, landlords, agents, field teams, and admins.</span>
            </div>
            <span class="toc-page">Pages 5–6</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">04</span>
            <div class="toc-text">
              <span class="toc-title">End-to-End Step-by-Step User Journeys</span>
              <span class="toc-desc">Six complete workflows covering urban search, rural parcel inspection, tenant screening, leasing, and team tools.</span>
            </div>
            <span class="toc-page">Pages 7–9</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">05</span>
            <div class="toc-text">
              <span class="toc-title">Comprehensive Feature Inventory by Product Area</span>
              <span class="toc-desc">Nine core capability suites: mapping, search, listing showcase, valuations, screening, payments, and compliance.</span>
            </div>
            <span class="toc-page">Pages 10–14</span>
          </div>
        </div>

        <div class="toc-column">
          <div class="toc-item">
            <span class="toc-num">06</span>
            <div class="toc-text">
              <span class="toc-title">Business Rules, Permissions &amp; Edge Cases</span>
              <span class="toc-desc">Status lifecycles, role-based permission matrix, system validations, and critical operational failure states.</span>
            </div>
            <span class="toc-page">Pages 15–16</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">07</span>
            <div class="toc-text">
              <span class="toc-title">Texas-Specific Data &amp; Regulatory Landscape</span>
              <span class="toc-desc">Non-disclosure rules, 254-county appraisal aggregation, ag valuations, mineral rights, MUDs, and coastal hazards.</span>
            </div>
            <span class="toc-page">Pages 17–18</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">08</span>
            <div class="toc-text">
              <span class="toc-title">Build vs. Buy / Outside Service Provider Matrix</span>
              <span class="toc-desc">Assessment of internal development versus licensed external service provider categories.</span>
            </div>
            <span class="toc-page">Page 19</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">09</span>
            <div class="toc-text">
              <span class="toc-title">Phased Implementation &amp; Delivery Roadmap</span>
              <span class="toc-desc">Four execution phases ordered by user value, operational dependencies, milestones, and risk mitigations.</span>
            </div>
            <span class="toc-page">Page 20</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">10</span>
            <div class="toc-text">
              <span class="toc-title">Key Assumptions, Research Gaps &amp; Confirmation Items</span>
              <span class="toc-desc">Commercial, legal, and operational assumptions, public research limitations, and decisions for kickoff.</span>
            </div>
            <span class="toc-page">Page 21</span>
          </div>

          <div class="toc-item">
            <span class="toc-num">11</span>
            <div class="toc-text">
              <span class="toc-title">Plain-Language Product Glossary &amp; Assessment</span>
              <span class="toc-desc">Definitions of essential real estate, legal, and cadastral concepts, followed by concluding strategic guidance.</span>
            </div>
            <span class="toc-page">Page 22</span>
          </div>
        </div>
      </div>

      <div class="guide-box">
        <div class="guide-header">
          <span class="guide-badge">HOW TO USE THIS PROPOSAL</span>
          <span class="guide-title">Executive &amp; Operational Reader Orientation</span>
        </div>
        <p class="guide-text">
          <strong>Non-Technical Product Orientation:</strong> This document is intentionally authored in plain business and product management 
          language. It defines <em>what</em> the platform must do, <em>who</em> uses each capability, <em>how</em> data records progress through 
          operational lifecycles, and <em>what</em> legal and commercial partnerships are necessary. Technical implementation details—such as code, 
          underlying databases, and specific engineering protocols—are purposefully omitted so that executive sponsors, business leaders, 
          and operations teams can focus entirely on customer value, market fit, and delivery sequencing.
        </p>
      </div>
    `
  },

  // PAGE 3: SECTION 1: EXECUTIVE SUMMARY & PRODUCT PURPOSE
  {
    num: 3,
    header: 'SECTION 1: EXECUTIVE SUMMARY & PRODUCT PURPOSE',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 01</div>
        <h2 class="section-heading">Executive Summary &amp; Strategic Product Purpose</h2>
      </div>

      <div class="callout-banner">
        <strong>The Strategic Vision:</strong> To create Texas's definitive all-in-one property intelligence and transaction ecosystem, 
        bridging the historical divide between specialized land-boundary GIS tools and consumer-focused residential marketplaces.
      </div>

      <div class="three-col-cards">
        <div class="feature-card">
          <div class="card-tag">THE MARKET OPPORTUNITY</div>
          <h4 class="card-head">A Vast, Diverse Territory</h4>
          <p class="card-body">
            Spanning 268,597 square miles and 254 counties, Texas is a fast-growing economic powerhouse. Rapidly expanding urban centres 
            (Dallas-Fort Worth, Houston, Austin, San Antonio) sit alongside expansive rural ranchlands, timber acreage, and energy-producing properties. 
            Property transactions range from suburban tract homes to multi-thousand-acre working cattle ranches.
          </p>
        </div>

        <div class="feature-card">
          <div class="card-tag">THE STRUCTURAL PROBLEM</div>
          <h4 class="card-head">The Fragmented Tool Silo</h4>
          <p class="card-body">
            Consumers and professionals currently juggle two disjointed software types: residential search portals that offer slick home listings 
            but lack parcel boundary data, ownership records, or rural tax details; and niche parcel viewers built for field surveyors that offer 
            boundary polygons but lack active listings, tenant screening, leasing tools, or rent processing.
          </p>
        </div>

        <div class="feature-card">
          <div class="card-tag">THE UNIFIED SOLUTION</div>
          <h4 class="card-head">An Integrated Platform</h4>
          <p class="card-body">
            Our proposed platform combines cadastral parcel intelligence (boundaries, owners, appraisal values, agricultural valuations) with 
            an active residential marketplace, tenant screening, digital leasing, automated rent collection, and corporate team collaboration—built 
            expressly to navigate Texas's unique statutory environment.
          </p>
        </div>
      </div>

      <div class="sub-section">
        <h3 class="sub-heading">Core Product Value Proposition: The Four Pillars</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 22%;">Product Pillar</th>
              <th style="width: 38%;">Target User Capabilities</th>
              <th style="width: 40%;">Texas Operational Advantage</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>1. Cadastral Parcel Intelligence</strong></td>
              <td>Interactive map overlays displaying exact legal property boundaries, County Appraisal District (CAD) property identification numbers, deed book and page references, acreage calculations, and recorded owner details.</td>
              <td>Aggregates standardized parcel boundaries across 254 independent Texas counties, linking appraisal roll records to parcel geometries for urban subdivisions and rural acreage.</td>
            </tr>
            <tr>
              <td><strong>2. Unified Property Marketplace</strong></td>
              <td>Multi-channel search for residential sales, rental vacancies, off-market acreage, and recently deeded transfers. Granular filters for price, bedrooms, square footage, acreage, and specialized land uses.</td>
              <td>Navigates Texas's strict non-disclosure status by providing transparent County Appraisal District assessed valuations and active MLS asking prices without misrepresenting confidential closed sales data.</td>
            </tr>
            <tr>
              <td><strong>3. Independent Landlord Suite</strong></td>
              <td>End-to-end self-service tools for small-to-midsize property owners: vacancy syndication, standardized digital rental applications, credit and criminal screening, state-compliant digital leases, and online rent payments.</td>
              <td>Implements Texas Property Code Chapter 92 requirements, including 30-day security deposit accounting workflows, statutory repair notices, and standard Texas residential lease terms.</td>
            </tr>
            <tr>
              <td><strong>4. Enterprise Field &amp; Team Collaboration</strong></td>
              <td>Multi-seat corporate accounts, centralized billing, role-based user management, live mobile GPS location tracking, map annotation sharing, and bulk export of parcel records (KML, CSV, GeoJSON).</td>
              <td>Empowers Texas land agents, energy rights-of-way specialists, agricultural appraisers, and municipal teams to inspect rural boundaries live in the field and collaborate securely across offices.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="summary-stat-bar">
        <div class="stat-item"><span class="stat-number">254</span><span class="stat-label">Texas Counties Covered</span></div>
        <div class="stat-item"><span class="stat-number">100%</span><span class="stat-label">Non-Disclosure Compliance</span></div>
        <div class="stat-item"><span class="stat-number">1-Click</span><span class="stat-label">Reusable Tenant Screening</span></div>
        <div class="stat-item"><span class="stat-number">Zero-Fee</span><span class="stat-label">Automated ACH Rent Rail</span></div>
      </div>
    `
  },

  // PAGE 4: SECTION 2: RESEARCH METHODOLOGY & COMPREHENSIVE EVIDENCE LOG
  {
    num: 4,
    header: 'SECTION 2: RESEARCH METHODOLOGY & EVIDENCE LOG',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 02</div>
        <h2 class="section-heading">Research Methodology &amp; Public Evidence Log</h2>
      </div>

      <p class="section-intro">
        To design a competitive, robust platform, we conducted an exhaustive public review of two prevailing market archetypes:
        <strong>Archetype A (Cadastral Parcel &amp; Field Intelligence Tool)</strong> and <strong>Archetype B (Residential Marketplace &amp; Rental Management Suite)</strong>.
        The investigation strictly utilized publicly accessible browser interfaces, published pricing schedules, user documentation, 
        and visible operational workflows without circumventing access controls, paywalls, or private credentials.
      </p>

      <div class="evidence-legend">
        <span class="legend-badge conf-badge">CONFIRMED: Observed directly on public web/mobile screens, help docs, or published pricing.</span>
        <span class="legend-badge inf-badge">INFERRED: Operational deduction based on visible inputs, state transitions, and business logic.</span>
        <span class="legend-badge unk-badge">UNKNOWN / UNVERIFIED: Private backend systems, closed algorithms, or undisclosed terms.</span>
      </div>

      <table class="data-table evidence-table">
        <thead>
          <tr>
            <th style="width: 20%;">Functional Area</th>
            <th style="width: 35%;">Observed Public Behavior &amp; Feature Mechanics</th>
            <th style="width: 15%;">Evidence Status</th>
            <th style="width: 30%;">Operational Translation for Texas Build</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Cadastral Map &amp; Parcels</strong></td>
            <td>Vector polygon boundaries overlaid on satellite, street, and topo imagery. Tapping parcel reveals owner name, APN, acreage, and assessed tax values.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Build vector parcel tile pipeline integrating Texas Geographic Information Office (TxGIO) and county CAD files.</td>
          </tr>
          <tr>
            <td><strong>Live GPS Field Tracking</strong></td>
            <td>Mobile GPS crosshairs locate user relative to property boundary lines in real time; drive mode centers map dynamically during transit.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Implement native browser/mobile geolocation with orientation compass for on-site Texas acreage and ranch evaluations.</td>
          </tr>
          <tr>
            <td><strong>Multi-User Corporate Tier</strong></td>
            <td>Centralized admin dashboard with volume pricing tiers (10% off for 2–5 seats scaling to 50% for 101+ seats); seat invitation workflows.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Create self-service team management console with multi-seat volume billing and shared parcel folder workspaces.</td>
          </tr>
          <tr>
            <td><strong>Residential Listing Discovery</strong></td>
            <td>Omni-search supporting city, zip, address, or custom-drawn polygon boundaries. Granular filters for beds, baths, price, home type, and amenities.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Integrate regional Texas MLS feeds with cadastral polygon boundaries to allow cross-filtering of acreage and residential specs.</td>
          </tr>
          <tr>
            <td><strong>Valuation Modeling</strong></td>
            <td>Automated market value estimates and rental yield estimates with confidence bands and historical trend charts.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>In Texas's non-disclosure environment, valuation estimates must derive from CAD records, active listings, and macroeconomic indicators.</td>
          </tr>
          <tr>
            <td><strong>Tenant Screening Workflow</strong></td>
            <td>Applicant completes single reusable profile ($35 fee range) granting landlord access to soft-pull credit check, criminal history, and eviction record.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Integrate FCRA-compliant screening bureau; ensure soft inquiries do not depress applicant credit scores.</td>
          </tr>
          <tr>
            <td><strong>Digital Lease Execution</strong></td>
            <td>Online lease builder using standardized state templates, custom rules, automated signature routing, and PDF storage.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Incorporate Texas-promulgated lease forms with Texas Property Code Chapter 92 statutory tenant and landlord disclosures.</td>
          </tr>
          <tr>
            <td><strong>Automated Rent Collection</strong></td>
            <td>Zero-fee ACH bank transfers for landlords and tenants; convenience fee for card payments; recurring auto-pay and late fee automation.</td>
            <td><span class="status-pill status-conf">CONFIRMED</span></td>
            <td>Partner with banking-as-a-service provider to handle Automated Clearing House (ACH) transfers, tenant ledgering, and split payments.</td>
          </tr>
          <tr>
            <td><strong>Backend Fraud Moderation</strong></td>
            <td>Automated algorithms flag suspicious listings, duplicate photos, and discriminatory phrasing; manual review queues for escalated disputes.</td>
            <td><span class="status-pill status-inf">INFERRED</span></td>
            <td>Deploy automated Fair Housing text scanners and CAD deed cross-referencing to prevent fraudulent listing creation.</td>
          </tr>
          <tr>
            <td><strong>Cadastral Data Latency</strong></td>
            <td>County tax records reflect varying update cadences depending on local county appraisal district cycles (typically quarterly to annual).</td>
            <td><span class="status-pill status-inf">INFERRED</span></td>
            <td>Establish automated monthly ETL pipelines for large urban Texas CADs and quarterly/annual cycles for rural counties.</td>
          </tr>
          <tr>
            <td><strong>Proprietary Search Ranking</strong></td>
            <td>Internal algorithms determine sort order for featured listings, agent advertising distribution, and search result relevance.</td>
            <td><span class="status-pill status-unk">UNKNOWN</span></td>
            <td>Establish an open, merit-based relevance algorithm based strictly on geographic proximity, listing completeness, and user filter match.</td>
          </tr>
        </tbody>
      </table>
    `
  }
];

console.log('Part 1 defined: Pages 1 to 4.');
