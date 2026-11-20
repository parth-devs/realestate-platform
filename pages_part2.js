// pages_part2.js: Personas and User Journeys (Pages 5 through 9)

module.exports = [
  // PAGE 5: SECTION 3: USER PERSONAS (PART 1: CONSUMERS, SEEKERS & TENANTS)
  {
    num: 5,
    header: 'SECTION 3: USER PERSONAS & OPERATIONAL GOALS (PART 1)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 03</div>
        <h2 class="section-heading">User Types, Personas &amp; Operational Goals (Part 1)</h2>
      </div>

      <p class="section-intro">
        The platform serves a broad spectrum of real estate stakeholders across Texas. To ensure operational excellence, 
        system features are mapped directly to defined user personas, their primary goals, pain points, and required permissions.
      </p>

      <div class="persona-card">
        <div class="persona-header">
          <div class="persona-title-group">
            <span class="persona-role">PERSONA 01: RESIDENTIAL HOMEBUYER</span>
            <h3 class="persona-name">Elena Rodriguez — Suburban Home Seeker</h3>
          </div>
          <span class="persona-badge">CONSUMER TIER — FREE ACCESS</span>
        </div>
        <div class="persona-grid">
          <div class="persona-col">
            <div class="persona-subhead">PROFILE &amp; CONTEXT</div>
            <p class="persona-text">First-time or move-up buyer exploring suburban homes in major Texas metros (e.g., Katy, Frisco, Round Rock). Balances home prices against property taxes, school quality, commute times, and flood risks.</p>
            <div class="persona-subhead">CORE OPERATIONAL GOALS</div>
            <ul class="persona-list">
              <li>Discover active homes for sale matching granular criteria (price, bedrooms, garage, lot size).</li>
              <li>Simulate all-in monthly payments including local Texas property taxes, HOA fees, and MUD assessments.</li>
              <li>Save favorite properties, draw custom search polygons, and receive instant alerts on new listings.</li>
              <li>Schedule physical tours directly with licensed Texas real estate agents.</li>
            </ul>
          </div>
          <div class="persona-col">
            <div class="persona-subhead">CRITICAL PAIN POINTS IN TEXAS</div>
            <p class="persona-text">Stickershock from high Texas ad valorem property taxes and undisclosed MUD bond rates; confusion over flood zones and hurricane risk in coastal and low-lying river areas.</p>
            <div class="persona-subhead">SYSTEM PERMISSIONS &amp; ACCESS</div>
            <ul class="persona-list">
              <li>Read access to public listing details, CAD assessment rolls, school ratings, and hazard overlays.</li>
              <li>Write access to personal saved homes, custom search collections, private notes, and tour inquiries.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="persona-card">
        <div class="persona-header">
          <div class="persona-title-group">
            <span class="persona-role">PERSONA 02: RESIDENTIAL RENTER</span>
            <h3 class="persona-name">Marcus Vance — Metro Apartment &amp; Single-Family Renter</h3>
          </div>
          <span class="persona-badge">CONSUMER TIER — FREE BROWSING / PAID SCREENING</span>
        </div>
        <div class="persona-grid">
          <div class="persona-col">
            <div class="persona-subhead">PROFILE &amp; CONTEXT</div>
            <p class="persona-text">Relocating professional or young family seeking single-family rental homes, townhomes, or apartments in Austin, Dallas, or Houston. Values quick screening and transparent fee structures.</p>
            <div class="persona-subhead">CORE OPERATIONAL GOALS</div>
            <ul class="persona-list">
              <li>Search verified rental vacancies with transparent monthly rent and pet fee disclosures.</li>
              <li>Complete a single, reusable digital rental application including credit, criminal, and eviction reports.</li>
              <li>Submit applications to multiple participating Texas landlords without paying repetitive $50+ fees.</li>
              <li>Electronically sign residential leases and set up automated, zero-fee monthly ACH rent payments.</li>
            </ul>
          </div>
          <div class="persona-col">
            <div class="persona-subhead">CRITICAL PAIN POINTS IN TEXAS</div>
            <p class="persona-text">High application fees wasted on unavailable rentals; slow background checks; opaque lease terms regarding Texas statutory repair notice requirements and deposit deductions.</p>
            <div class="persona-subhead">SYSTEM PERMISSIONS &amp; ACCESS</div>
            <ul class="persona-list">
              <li>Read access to rental listings, neighborhood data, and personal application status.</li>
              <li>Write access to personal profile, uploaded identity documents, rental history, and banking info.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="persona-card">
        <div class="persona-header">
          <div class="persona-title-group">
            <span class="persona-role">PERSONA 03: RURAL LAND &amp; ACREAGE SEEKER</span>
            <h3 class="persona-name">Caleb Sterling — Hill Country Ranch &amp; Recreational Land Buyer</h3>
          </div>
          <span class="persona-badge">CONSUMER / PRO TIER — FREEMIUM &amp; FIELD TOOLS</span>
        </div>
        <div class="persona-grid">
          <div class="persona-col">
            <div class="persona-subhead">PROFILE &amp; CONTEXT</div>
            <p class="persona-text">Investor, hunter, or retiree looking for unimproved acreage, hunting tracts, or working cattle ranches across Central and West Texas. Focused heavily on boundaries, topography, and property tax exemptions.</p>
            <div class="persona-subhead">CORE OPERATIONAL GOALS</div>
            <ul class="persona-list">
              <li>Inspect legal cadastral boundaries, acreage calculations, and access easements across rural counties.</li>
              <li>Verify existing 1-d-1 Agricultural or Wildlife property tax valuations to gauge ongoing tax carrying costs.</li>
              <li>Use live mobile GPS in the field to walk fence lines and identify parcel corners in remote areas.</li>
              <li>Export parcel boundary files (KML/CSV) for use with GPS devices, GIS tools, and fence contractors.</li>
            </ul>
          </div>
          <div class="persona-col">
            <div class="persona-subhead">CRITICAL PAIN POINTS IN TEXAS</div>
            <p class="persona-text">Severe lack of boundary clarity on rural properties; surprise rollback taxes when changing agricultural land use; split-estate risks where surface owner does not own subsurface mineral/oil rights.</p>
            <div class="persona-subhead">SYSTEM PERMISSIONS &amp; ACCESS</div>
            <ul class="persona-list">
              <li>Read access to 254-county parcel geometries, CAD valuation histories, topography, and RRC well overlays.</li>
              <li>Write access to field pins, distance and area measurements, parcel folders, and GPS track logs.</li>
            </ul>
          </div>
        </div>
      </div>
    `
  },

  // PAGE 6: SECTION 3: USER PERSONAS (PART 2: LANDLORDS, AGENTS, TEAMS & ADMINS)
  {
    num: 6,
    header: 'SECTION 3: USER PERSONAS & OPERATIONAL GOALS (PART 2)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 03 CONTINUED</div>
        <h2 class="section-heading">User Types, Personas &amp; Operational Goals (Part 2)</h2>
      </div>

      <div class="persona-card">
        <div class="persona-header">
          <div class="persona-title-group">
            <span class="persona-role">PERSONA 04: INDEPENDENT LANDLORD</span>
            <h3 class="persona-name">David &amp; Sarah Chen — Small-Scale Residential Investors (1–10 Units)</h3>
          </div>
          <span class="persona-badge">LANDLORD TIER — FREE LISTINGS &amp; RENT RAILS</span>
        </div>
        <div class="persona-grid">
          <div class="persona-col">
            <div class="persona-subhead">PROFILE &amp; CONTEXT</div>
            <p class="persona-text">Self-managing owners of residential rental properties in Texas suburban hubs (e.g., Plano, Pearland, New Braunfels). Seek professional vacancy marketing and compliant tenant screening without hiring property managers.</p>
            <div class="persona-subhead">CORE OPERATIONAL GOALS</div>
            <ul class="persona-list">
              <li>Publish verified rental listings with automated syndication to major consumer search channels.</li>
              <li>Review complete applicant screening packages (credit score, criminal background, eviction record).</li>
              <li>Draft and execute Texas-specific residential lease agreements with compliant digital signatures.</li>
              <li>Collect monthly rent via automated ACH direct deposit with automated late fee calculation.</li>
            </ul>
          </div>
          <div class="persona-col">
            <div class="persona-subhead">CRITICAL PAIN POINTS &amp; TEXAS RISKS</div>
            <p class="persona-text">Tenant defaults and non-payment; non-compliance with Texas Property Code Chapter 92 (strict 30-day security deposit accounting and statutory repair response deadlines).</p>
            <div class="persona-subhead">SYSTEM PERMISSIONS &amp; ACCESS</div>
            <ul class="persona-list">
              <li>Read/Write access to owned property listings, tenant applications, credit reports, lease agreements, and payment ledgers.</li>
              <li>Administrative ability to invite tenants, adjust rent schedules, and log manual maintenance entries.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="persona-card">
        <div class="persona-header">
          <div class="persona-title-group">
            <span class="persona-role">PERSONA 05: REAL ESTATE AGENT &amp; LAND BROKER</span>
            <h3 class="persona-name">Javier Morales — Residential &amp; Acreage Specialist</h3>
          </div>
          <span class="persona-badge">PROFESSIONAL / AGENT TIER — PAID PROMOTIONS</span>
        </div>
        <div class="persona-grid">
          <div class="persona-col">
            <div class="persona-subhead">PROFILE &amp; CONTEXT</div>
            <p class="persona-text">Licensed Texas broker or sales agent representing residential buyers, home sellers, and rural acreage clients. Operates between suburban subdivisions and rural ranches.</p>
            <div class="persona-subhead">CORE OPERATIONAL GOALS</div>
            <ul class="persona-list">
              <li>Promote active MLS listings with high-visibility badges and agent contact cards.</li>
              <li>Verify boundary lines, ownership history, and CAD assessments during client field tours.</li>
              <li>Receive qualified buyer inquiries and tour scheduling requests directly into a dedicated inbox.</li>
              <li>Share curated property collections with clients, complete with private agent notes.</li>
            </ul>
          </div>
          <div class="persona-col">
            <div class="persona-subhead">CRITICAL PAIN POINTS &amp; TEXAS RISKS</div>
            <p class="persona-text">Unqualified leads; outdated county tax data during client negotiations; compliance with Texas Real Estate Commission (TREC) mandatory consumer notice postings (IABS and Consumer Protection Notice).</p>
            <div class="persona-subhead">SYSTEM PERMISSIONS &amp; ACCESS</div>
            <ul class="persona-list">
              <li>Read/Write access to professional profile, claimed listings, lead management inbox, and client collaboration folders.</li>
              <li>Enhanced cadastral mapping tools with high-resolution aerial and topographical layers.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="two-col-cards" style="margin-top: 6px;">
        <div class="persona-mini-card">
          <div class="mini-header">
            <span class="persona-role">PERSONA 06: CORPORATE FIELD PROFESSIONAL</span>
            <span class="persona-badge">ENTERPRISE TIER</span>
          </div>
          <h4 class="mini-name">Field Surveyors, Energy Right-of-Way &amp; Ag Appraisers</h4>
          <p class="mini-text">Requires multi-seat corporate accounts, centralized billing, offline mobile boundary caching, CAD parcel record bulk exports (KML/CSV/GeoJSON), and shared team annotations for land acquisition and utility corridors.</p>
        </div>

        <div class="persona-mini-card">
          <div class="mini-header">
            <span class="persona-role">PERSONA 07: PLATFORM ADMINISTRATOR</span>
            <span class="persona-badge">INTERNAL ROLE</span>
          </div>
          <h4 class="mini-name">Trust, Safety, Data Stewards &amp; Compliance Officers</h4>
          <p class="mini-text">Oversees statewide county parcel syncs, monitors listing fraud, enforces Fair Housing Act compliance, reviews disputed ownership claims, audits payment exception queues, and ensures Texas regulatory alignment.</p>
        </div>
      </div>
    `
  },

  // PAGE 7: SECTION 4: USER JOURNEYS (PART 1: HOME SEARCH & RURAL PARCEL INSPECTION)
  {
    num: 7,
    header: 'SECTION 4: END-TO-END USER JOURNEYS (PART 1)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 04</div>
        <h2 class="section-heading">End-to-End User Journeys (Part 1)</h2>
      </div>

      <div class="journey-container">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 01</span>
          <h3 class="journey-title">Suburban Residential Home Search, Saved Alert &amp; Tour Scheduling</h3>
          <span class="journey-user">Primary Actor: Elena Rodriguez (Homebuyer)</span>
        </div>
        <p class="journey-desc">Covers the discovery, evaluation, dynamic cost modeling, search alert subscription, and physical tour booking flow for residential properties in Texas metropolitan areas.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Discovery &amp; Location Query:</strong> Enters target metro, neighborhood, or zip code (e.g., "Frisco, TX") into omni-search bar. Toggles to "For Sale" view. Map renders interactive clusters and individual listing pins with asking prices.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Granular Filter Application:</strong> Filters for $450k–$650k, 4+ beds, 2.5+ baths, 2+ garage spaces, and minimum 0.25-acre lot size. Uses the interactive polygon tool to encircle a specific school attendance boundary.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Property Evaluation &amp; Cost Modeling:</strong> Opens Property Detail Page. Reviews high-res gallery, CAD assessed tax value, and school ratings. Adjusts the Texas Payment Calculator to factor local 2.2% property tax rate and $125/mo MUD bond assessment.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>Search Subscription &amp; Favoriting:</strong> Clicks "Save Property" and writes private note ("Great backyard, need to check MUD taxes"). Saves the custom polygon search with "Instant Push &amp; Email Alert" selected for new matching inventory.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Tour Scheduling Request:</strong> Selects "Request a Tour" button. Selects preferred date and time slot (Saturday at 10:00 AM). Inputs contact info and confirms pre-approval status. System validates phone via SMS code.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Confirmation &amp; Agent Routing:</strong> System routes request to listing agent or participating premier partner. Sends calendar confirmation to buyer. System prompts user to review mandatory TREC Information About Brokerage Services (IABS) disclosure.
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Search saved, instant notification schedule active, tour inquiry logged in CRM, buyer receives email confirmation with agent contact details.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> Zero results in polygon (prompts filter expansion); agent unavailable for requested time (suggests alternate slots); SMS verification timeout (resend code prompt).</div>
        </div>
      </div>

      <div class="journey-container" style="margin-top: 10px;">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 02</span>
          <h3 class="journey-title">Rural Parcel Lookup, GPS Field Boundary Walk &amp; Acreage Analysis</h3>
          <span class="journey-user">Primary Actor: Caleb Sterling (Acreage Seeker) / Field Professional</span>
        </div>
        <p class="journey-desc">Examines the cadastral parcel lookup, aerial boundary review, on-site mobile GPS walking, agricultural exemption check, and project export workflow across Texas rural counties.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Cadastral Search:</strong> Enters County Appraisal District Property ID (APN) or recorded owner surname into search bar (e.g., "Gillespie County, Parcel 14209"). Platform zooms map directly to parcel centroid with boundaries highlighted in gold.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Attribute &amp; Ag Valuation Inspection:</strong> Inspects parcel slide-out card: confirms 48.65 surveyed acres, recorded deed reference, legal description, and current 1-d-1 Agricultural Exemption status (cattle grazing valuation vs. market value).
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Layer Exploration:</strong> Toggles base map from street map to USGS High-Resolution Topographic layer to inspect elevation contours, seasonal creek beds, and potential flood draw areas. Toggles Railroad Commission (RRC) pipeline overlay.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>On-Site Live GPS Walking:</strong> Arrives at physical property. Launches mobile app and taps "Locate Me". Live blue location dot with directional compass appears inside parcel boundary. Walks northern fence line to verify physical corners against digital boundary.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Measurement &amp; Waypoint Drop:</strong> Uses interactive measurement tool to measure road frontage (1,320 feet) and drops a custom waypoint pin labeled "Potential Barn Site / Water Well Needed" with attached field photograph.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Project Save &amp; Data Export:</strong> Saves parcel into custom folder "2026 Hill Country Ranch Candidates". Clicks "Export Data" to generate a standardized KML and CSV file containing boundary coordinates, APN, and CAD assessment data for offline use.
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Parcel boundary verified on-site, field pins and photos synced to cloud, agricultural tax risk noted, export file delivered for surveying team.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> Cellular dead zone (triggers offline cached map view); unmapped rural parcel geometry (displays CAD tax card with "Boundary geometry pending county update").</div>
        </div>
      </div>
    `
  },

  // PAGE 8: SECTION 4: USER JOURNEYS (PART 2: TENANT SCREENING & LANDLORD LEASING/RENT)
  {
    num: 8,
    header: 'SECTION 4: END-TO-END USER JOURNEYS (PART 2)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 04 CONTINUED</div>
        <h2 class="section-heading">End-to-End User Journeys (Part 2)</h2>
      </div>

      <div class="journey-container">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 03</span>
          <h3 class="journey-title">Tenant Discovery, Reusable Screening Profile &amp; Application Submission</h3>
          <span class="journey-user">Primary Actor: Marcus Vance (Prospective Renter)</span>
        </div>
        <p class="journey-desc">Details the step-by-step path of a renter finding a vacancy, completing an FCRA-compliant background and credit check, and submitting a reusable application package to a Texas landlord.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Rental Discovery:</strong> Browses rental listings in Dallas-Fort Worth. Identifies a 3-bedroom single-family rental in Plano listed at $2,450/month with an "Apply with Portable Screening" badge.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Profile Assembly:</strong> Clicks "Apply Now". Enters personal identity info, employment history, declared monthly income ($8,500/mo), vehicle details, and uploads two recent paystubs and government photo ID.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Screening Authorization &amp; Payment:</strong> Authorizes a soft-pull credit report, 50-state criminal record check, and nationwide eviction history. Pays one-time $35 platform fee providing 30 days of unlimited applications.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>Verification Processing:</strong> Background verification service generates report within 2 minutes. Credit score (740), payment history, zero criminal records, and clean eviction history populated into private profile.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Application Submission:</strong> Reviews assembled application package. Clicks "Submit Application to Landlord". Adds an optional personal introduction note explaining move-in timeline and pet documentation.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Status Tracking &amp; Notice:</strong> Dashboard status updates to "Under Landlord Review". System triggers notification when landlord opens the report. Displays expected decision timeline (typically 24–48 hours).
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Landlord receives instant notification of completed screening package; renter retains reusable report valid across all platform listings for 30 days.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> Credit bureau identity mismatch (prompts knowledge-based authentication questions); screening incomplete (blocks submission until mandatory fields verified).</div>
        </div>
      </div>

      <div class="journey-container" style="margin-top: 10px;">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 04</span>
          <h3 class="journey-title">Landlord Listing Setup, Application Review, Lease Execution &amp; Rent Rail</h3>
          <span class="journey-user">Primary Actor: David &amp; Sarah Chen (Independent Landlords)</span>
        </div>
        <p class="journey-desc">Walks through the landlord's complete lifecycle from vacancy marketing and applicant screening review to digital lease generation and automated ACH rent collection.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Listing Creation &amp; Verification:</strong> Enters property address in Landlord Portal. System pulls CAD property records to verify ownership. Enters rent ($2,450), deposit ($2,450), pet rules, and uploads 15 photos. Listing syndicates live.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Application &amp; Screening Review:</strong> Receives email alert: "New Application Received from Marcus Vance". Opens Landlord Dashboard. Reviews income verification, credit score (740), criminal, and eviction reports in structured view.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Applicant Acceptance:</strong> Clicks "Accept Applicant". System automatically updates application status and triggers an automated notification to applicant. System offers option to send adverse action notices to declined applicants.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>Texas Digital Lease Creation:</strong> Launches digital lease builder. System auto-populates tenant info, property address, rent amount, and default Texas Property Code Chapter 92 statutory rules (smoke detectors, repair procedures, 30-day deposit return).
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Electronic Signature Routing:</strong> Landlord reviews draft and clicks "Send for Signatures". Tenant receives secure e-sign link, reviews, and signs. Landlord countersigns digitally. System seals PDF and archives in both dashboards.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Automated ACH Rent Setup:</strong> Landlord links checking account via micro-deposit/instant verification. Tenant sets up recurring auto-pay on the 1st of each month. Move-in deposit and first month's rent schedule initiated with zero transaction fees.
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Vacancy filled, compliant Texas lease archived, recurring banking rail established, automatic late fees configured for grace period expiration on the 4th.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> Ownership name mismatch against CAD (requires manual deed upload); tenant fails to sign within 48 hours (triggers automated expiration warning).</div>
        </div>
      </div>
    `
  },

  // PAGE 9: SECTION 4: USER JOURNEYS (PART 3: HOMEOWNER CLAIM & CORPORATE TEAMS)
  {
    num: 9,
    header: 'SECTION 4: END-TO-END USER JOURNEYS (PART 3)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 04 CONTINUED</div>
        <h2 class="section-heading">End-to-End User Journeys (Part 3)</h2>
      </div>

      <div class="journey-container">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 05</span>
          <h3 class="journey-title">Homeowner Property Claim, Assessment Tracking &amp; Home Fact Editing</h3>
          <span class="journey-user">Primary Actor: Residential Homeowner</span>
        </div>
        <p class="journey-desc">Demonstrates how an existing homeowner claims their residence, tracks property tax assessments, edits private home facts, and monitors neighborhood sales activity.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Property Lookup &amp; Claim Request:</strong> Navigates to home address. Clicks "Claim This Home" link on property detail page. System prompts user to log in or create a verified homeowner account.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Identity &amp; Ownership Verification:</strong> User enters full legal name and mailing address. Platform cross-checks user credentials against the official County Appraisal District tax roll and recorded deed grantee records.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Two-Factor Ownership Validation:</strong> If identity matches CAD records, system triggers instant phone/email verification code. If name differs (e.g., recent purchase or trust ownership), prompts upload of closing statement or deed.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>Private Owner Dashboard Access:</strong> Upon verification, user gains private administrative access. Views estimated market value trends, local rental yield estimate, and historical County Appraisal District tax assessment history.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Home Facts &amp; Upgrade Adjustments:</strong> Edits home facts: updates finished square footage from 2,400 to 2,650 following a permitted patio enclosure, adds custom pool specification, and updates HVAC replacement year.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Market Tracking &amp; Off-Market Alerts:</strong> Sets off-market status to "Not Currently for Sale". Subscribes to monthly neighborhood digest tracking nearby listing activity, CAD protest deadlines, and tax rate changes.
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Ownership locked to verified user account; home facts updated in public showcase; homeowner receives automated alerts regarding property tax appraisal notices.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> Competing claim on same property (triggers admin dispute lock and document audit); unverified document upload (notifies user with specific deficiency reasons).</div>
        </div>
      </div>

      <div class="journey-container" style="margin-top: 10px;">
        <div class="journey-header">
          <span class="journey-id">JOURNEY 06</span>
          <h3 class="journey-title">Corporate Multi-Seat Provisioning, Collaborative Tagging &amp; GIS Export</h3>
          <span class="journey-user">Primary Actor: Enterprise Team Administrator / Field Project Manager</span>
        </div>
        <p class="journey-desc">Details how an enterprise organization (e.g., land brokerage, pipeline survey firm, appraisal practice) subscribes, manages team seats, and collaborates on field parcel projects.</p>

        <div class="journey-steps">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <strong>Corporate Plan Selection:</strong> Account manager visits Enterprise Pricing page. Selects "Corporate Team Plan" with 12 team seats on annual billing (receiving a 25% tiered volume discount). Enters company billing info.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <strong>Team Member Provisioning:</strong> Enters corporate email addresses for 11 field agents and surveyors. System dispatches automated invitation emails with secure account association links.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <strong>Role &amp; Permission Allocation:</strong> Assigns role-based permissions: assigns 2 Senior Surveyors as "Team Managers" (able to invite seats and view billing) and 9 staff members as "Field Operators" (field mapping and data entry only).
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <strong>Shared Workspace Configuration:</strong> Admin creates a shared team folder: "Brazos River Basin Pipeline Corridor A". Tags 145 contiguous rural parcels across three Texas counties with project-specific status labels ("Acquisition Pending").
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">5</div>
            <div class="step-content">
              <strong>Field Collaboration &amp; Sync:</strong> Field agents access the shared folder on mobile devices. They inspect fence lines, verify landowner contact details on-site, add geotagged field photos, and mark boundary survey markers.
            </div>
          </div>
          <div class="step-card">
            <div class="step-num">6</div>
            <div class="step-content">
              <strong>Centralized Reporting &amp; GIS Export:</strong> Admin views consolidated team activity in real time. Exports the entire 145-parcel corridor dataset in standardized Shapefile and CSV format for engineering and legal review.
            </div>
          </div>
        </div>

        <div class="journey-meta-grid">
          <div class="j-meta-box"><strong>Expected Outcomes:</strong> Centralized billing invoice generated; team seats active; shared field data synchronizes across mobile and desktop; full audit log of field changes preserved.</div>
          <div class="j-meta-box"><strong>Failure &amp; Edge States:</strong> User seat limit exceeded (prompts instant seat add with prorated billing); team member departs company (one-click admin revokes seat and reassigns to new hire).</div>
        </div>
      </div>
    `
  }
];

console.log('Part 2 defined: Pages 5 to 9.');
