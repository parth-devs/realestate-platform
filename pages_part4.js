// pages_part4.js: Business Rules, Status Lifecycles, Permissions, and Texas Regulatory Architecture (Pages 15 through 18)

module.exports = [
  // PAGE 15: SECTION 6: BUSINESS RULES, PERMISSIONS & STATUS LIFECYCLES
  {
    num: 15,
    header: 'SECTION 6: BUSINESS RULES & STATUS LIFECYCLES',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 06</div>
        <h2 class="section-heading">Business Rules, Permissions &amp; Status Lifecycles</h2>
      </div>

      <p class="section-intro">
        Robust platforms depend on clear, deterministic business rules. Below are the operational lifecycles governing the core transaction objects: 
        Property Listings, Tenant Applications, Lease Agreements, Payment Transactions, and Property Ownership Claims.
      </p>

      <div class="lifecycle-container">
        <div class="lifecycle-card">
          <div class="lifecycle-header">
            <span class="lifecycle-badge">LIFECYCLE 01</span>
            <h4 class="lifecycle-title">Property Listing Lifecycle</h4>
          </div>
          <div class="flow-steps">
            <span class="flow-node">DRAFT</span> &rarr;
            <span class="flow-node">PENDING VERIFICATION</span> &rarr;
            <span class="flow-node node-active">ACTIVE / PUBLISHED</span> &rarr;
            <span class="flow-node">UNDER CONTRACT</span> &rarr;
            <span class="flow-node">CLOSED / OFF-MARKET</span>
          </div>
          <p class="lifecycle-rules">
            <strong>Business Rules:</strong> A draft listing requires verified street address, monthly rent/price, minimum 5 photos, and contact info. Listing moves to "Pending Verification" where CAD ownership or agent MLS ID is verified. Once verified, listing transitions to "Active". While Active, inquiries and applications are routed. When landlord/agent accepts an offer, status shifts to "Under Contract" (pausing new inquiries). Upon lease execution or sale closing, listing moves to "Closed/Off-Market".
          </p>
        </div>

        <div class="lifecycle-card">
          <div class="lifecycle-header">
            <span class="lifecycle-badge">LIFECYCLE 02</span>
            <h4 class="lifecycle-title">Rental Application &amp; Screening Lifecycle</h4>
          </div>
          <div class="flow-steps">
            <span class="flow-node">STARTED / INCOMPLETE</span> &rarr;
            <span class="flow-node">SCREENING AUTHORIZED</span> &rarr;
            <span class="flow-node">READY FOR REVIEW</span> &rarr;
            <span class="flow-node node-active">ACCEPTED / APPROVED</span> &rarr;
            <span class="flow-node node-fail">DECLINED / ADVERSE ACTION</span>
          </div>
          <p class="lifecycle-rules">
            <strong>Business Rules:</strong> Tenant completes identity, income, and vehicle data. User pays $35 fee and authorizes soft credit pull. Background service delivers reports within 120 seconds. Application status becomes "Ready for Review" in Landlord Portal. Landlord may Accept or Decline. Declining triggers an automated, FCRA-compliant digital Adverse Action Notice specifying credit bureau contact details.
          </p>
        </div>

        <div class="lifecycle-card">
          <div class="lifecycle-header">
            <span class="lifecycle-badge">LIFECYCLE 03</span>
            <h4 class="lifecycle-title">Digital Lease Agreement Lifecycle</h4>
          </div>
          <div class="flow-steps">
            <span class="flow-node">DRAFTING</span> &rarr;
            <span class="flow-node">OUT FOR SIGNATURES</span> &rarr;
            <span class="flow-node">PARTIALLY SIGNED</span> &rarr;
            <span class="flow-node node-active">FULLY EXECUTED</span> &rarr;
            <span class="flow-node">ACTIVE TENANCY</span> &rarr;
            <span class="flow-node">TERMINATED / EXPIRED</span>
          </div>
          <p class="lifecycle-rules">
            <strong>Business Rules:</strong> Landlord configures lease parameters and Texas statutory disclosures. Sent simultaneously to all adult tenants. Tenants have 72 hours to sign before link expires. Once all tenants sign, landlord countersigns. Upon countersignature, PDF is sealed with tamper-evident digital certificate, archived in both accounts, and triggers automated rent collection schedule.
          </p>
        </div>

        <div class="lifecycle-card">
          <div class="lifecycle-header">
            <span class="lifecycle-badge">LIFECYCLE 04</span>
            <h4 class="lifecycle-title">Automated Rent Payment Lifecycle</h4>
          </div>
          <div class="flow-steps">
            <span class="flow-node">SCHEDULED</span> &rarr;
            <span class="flow-node">PROCESSING (ACH HOLD)</span> &rarr;
            <span class="flow-node node-active">SETTLED / DEPOSITED</span> &rarr;
            <span class="flow-node node-fail">RETURNED / NSF FAILED</span> &rarr;
            <span class="flow-node">LATE FEE APPLIED</span>
          </div>
          <p class="lifecycle-rules">
            <strong>Business Rules:</strong> Auto-pay initiates 2 business days prior to due date. ACH clearing window requires 1–3 business days. If funds clear, status is "Settled" and ledger updates. If ACH returns (insufficient funds / NSF), system notifies tenant, reverses ledger credit, and issues retry invoice. If unpaid after Texas statutory 2-day grace period, automated late fee is assessed on the 4th day.
          </p>
        </div>
      </div>
    `
  },

  // PAGE 16: SECTION 6: SYSTEM PERMISSIONS MATRIX & OPERATIONAL EDGE CASES
  {
    num: 16,
    header: 'SECTION 6: PERMISSIONS MATRIX & OPERATIONAL EDGE CASES',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 06 CONTINUED</div>
        <h2 class="section-heading">System Permissions Matrix &amp; Operational Edge Cases</h2>
      </div>

      <div class="sub-section">
        <h3 class="sub-heading">Role-Based Access Control (RBAC) Permissions Matrix</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 25%;">Platform Capability</th>
              <th style="width: 12%;">Public Visitor</th>
              <th style="width: 12%;">Registered Buyer</th>
              <th style="width: 12%;">Verified Tenant</th>
              <th style="width: 13%;">Independent Landlord</th>
              <th style="width: 13%;">Licensed Agent</th>
              <th style="width: 13%;">Enterprise Field Team</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Browse Listings &amp; Parcels</td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
            </tr>
            <tr>
              <td>View CAD Tax Assessments</td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
            </tr>
            <tr>
              <td>Save Homes &amp; Custom Polygons</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
            </tr>
            <tr>
              <td>Submit Reusable Application</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
            </tr>
            <tr>
              <td>Access Credit/Eviction Reports</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-inf">Own Only</span></td>
              <td><span class="status-pill status-conf">Applicants</span></td>
              <td><span class="status-pill status-inf">With Consent</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
            </tr>
            <tr>
              <td>Publish Rental Listing</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
            </tr>
            <tr>
              <td>Draft &amp; Sign Digital Leases</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-inf">Sign Only</span></td>
              <td><span class="status-pill status-conf">Create/Sign</span></td>
              <td><span class="status-pill status-conf">Authorized</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
            </tr>
            <tr>
              <td>ACH Rent Collection</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-inf">Pay Only</span></td>
              <td><span class="status-pill status-conf">Collect</span></td>
              <td><span class="status-pill status-inf">Managed</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
            </tr>
            <tr>
              <td>Live GPS Field Tracking</td>
              <td><span class="status-pill status-inf">Basic</span></td>
              <td><span class="status-pill status-conf">Standard</span></td>
              <td><span class="status-pill status-inf">Standard</span></td>
              <td><span class="status-pill status-conf">Standard</span></td>
              <td><span class="status-pill status-conf">Advanced</span></td>
              <td><span class="status-pill status-conf">Advanced</span></td>
            </tr>
            <tr>
              <td>Bulk GIS Data Export (KML/CSV)</td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-fail">Denied</span></td>
              <td><span class="status-pill status-inf">Licensed</span></td>
              <td><span class="status-pill status-conf">Allowed</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="sub-section" style="margin-top: 8px;">
        <h3 class="sub-heading">Operational Edge Cases &amp; Exception Handling Protocols</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 25%;">Operational Scenario</th>
              <th style="width: 40%;">Root Cause / Business Condition</th>
              <th style="width: 35%;">System Mitigation &amp; Exception Workflow</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Unmapped Rural Parcel Geometry</strong></td>
              <td>Remote Texas county CAD lacks digitized GIS vector boundaries; property only exists as a paper tax roll card.</td>
              <td>Renders an informational card with tax assessments and legal deed description; displays banner: <em>"Geometry pending county digital survey."</em></td>
            </tr>
            <tr>
              <td><strong>Disputed Ownership Claim</strong></td>
              <td>Two competing users attempt to claim the private owner dashboard for the same residential address.</td>
              <td>System instantly locks property dashboard; freezes private data edits; prompts both parties to upload recorded deed or closing statement for admin audit.</td>
            </tr>
            <tr>
              <td><strong>ACH Rent Payment Default (NSF)</strong></td>
              <td>Tenant bank account has insufficient funds during automated monthly rent draft.</td>
              <td>System issues automated alert to tenant; reverses ledger credit; issues retry link; calculates and adds late fee if unsettled after grace period.</td>
            </tr>
            <tr>
              <td><strong>Split Parcel Undivided Interests</strong></td>
              <td>Rural Texas acreage owned by multiple fractional heirs (undivided estate interests).</td>
              <td>Displays all recorded fractional owners and their percentage interests from CAD rolls; alerts buyers that sale requires unanimous partition agreement.</td>
            </tr>
            <tr>
              <td><strong>Unassigned Rural Addresses</strong></td>
              <td>Raw unimproved acreage tracts lacking a formal USPS postal street number.</td>
              <td>Enables geocoding and search indexing via County Appraisal District Property ID (APN), GPS coordinates, and road name references.</td>
            </tr>
          </tbody>
        </table>
      </div>
    `
  },

  // PAGE 17: SECTION 7: TEXAS-SPECIFIC DATA ARCHITECTURE (PART 1: NON-DISCLOSURE, CADs, AG VALUATION)
  {
    num: 17,
    header: 'SECTION 7: TEXAS-SPECIFIC DATA & REGULATION (PART 1)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 07</div>
        <h2 class="section-heading">Texas-Specific Data Architecture &amp; Regulatory Landscape (Part 1)</h2>
      </div>

      <p class="section-intro">
        Building a viable real estate and land platform in Texas requires solving for distinct state statutes, tax structures, 
        and institutional frameworks that do not exist in standard national software templates.
      </p>

      <div class="statute-box">
        <div class="statute-header">
          <span class="statute-tag">STATUTORY REALITY 01</span>
          <h3 class="statute-title">Texas is a Strict Non-Disclosure State</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">The Legal Framework</h4>
            <p class="statute-text">
              Texas is one of 12 non-disclosure states in the U.S. In Texas, actual real estate sales transaction prices are <strong>not public record</strong>. 
              When a deed is recorded with the County Clerk, it documents the legal transfer of title, grantor, grantee, and legal property description, 
              but does not disclose the financial purchase price.
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Platform Operational Solution</h4>
            <p class="statute-text">
              The platform clearly differentiates between <em>Active MLS Asking Prices</em>, <em>County Appraisal District (CAD) Assessed Values</em>, 
              and <em>Modeled Market Estimates</em>. Public deed transfer histories display deed date, instrument type, and parties, with an educational notice: 
              <em>"Texas is a non-disclosure state; recorded deeds do not reflect confidential transaction prices."</em> Closed MLS prices are restricted to compliant VOW client views.
            </p>
          </div>
        </div>
      </div>

      <div class="statute-box" style="margin-top: 8px;">
        <div class="statute-header">
          <span class="statute-tag">DATA AGGREGATION REALITY 02</span>
          <h3 class="statute-title">The 254-County &amp; 253-Appraisal District Landscape</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">Decentralization &amp; Vendor Fragmentation</h4>
            <p class="statute-text">
              Texas consists of 254 counties served by 253 independent County Appraisal Districts (CADs). There is no single statewide database 
              or mandated parcel schema. Counties utilize diverse Computer-Assisted Mass Appraisal (CAMA) software vendors (e.g., Pritchard &amp; Abbott, 
              Tyler Technologies, Harris Gover, True Automation) with varying update cycles.
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Hybrid Aggregation Strategy</h4>
            <p class="statute-text">
              The platform utilizes a two-tier data pipeline: (1) Partner with the <strong>Texas Geographic Information Office (TxGIO / TNRIS StratMap)</strong> 
              to ingest standardized statewide parcel boundary geometry covering 245+ counties; and (2) Establish direct automated ETL pipelines with the 
              top 25 metropolitan CADs (representing 80%+ of the Texas population) for real-time tax rolls and ownership synchronizations.
            </p>
          </div>
        </div>
      </div>

      <div class="statute-box" style="margin-top: 8px;">
        <div class="statute-header">
          <span class="statute-tag">PROPERTY TAX REALITY 03</span>
          <h3 class="statute-title">1-d-1 Agricultural, Timber &amp; Wildlife Valuations</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">Productivity vs. Market Valuation</h4>
            <p class="statute-text">
              Under Article VIII, Section 1-d-1 of the Texas Constitution, qualified rural land devoted to agriculture, timber, or wildlife management 
              is taxed based on productive agricultural capacity rather than speculative market value. A 100-acre ranch worth $1,500,000 may have an 
              agricultural productivity valuation of just $15,000, dramatically lowering property taxes.
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Rollback Tax Liability Alerts</h4>
            <p class="statute-text">
              If a buyer changes the use of agricultural land (e.g., subdividing for residential development), Texas law imposes a mandatory 
              <strong>3-Year Rollback Tax</strong> plus 5% annual statutory interest, recapturing the difference between market taxes and agricultural taxes. 
              The platform provides a built-in <em>Rollback Tax Calculator</em> to warn buyers of potential liabilities before purchase.
            </p>
          </div>
        </div>
      </div>
    `
  },

  // PAGE 18: SECTION 7: TEXAS-SPECIFIC DATA ARCHITECTURE (PART 2: MINERAL/RRC, MUDs, TWIA, TREC)
  {
    num: 18,
    header: 'SECTION 7: TEXAS-SPECIFIC DATA & REGULATION (PART 2)',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 07 CONTINUED</div>
        <h2 class="section-heading">Texas-Specific Data Architecture &amp; Regulatory Landscape (Part 2)</h2>
      </div>

      <div class="statute-box">
        <div class="statute-header">
          <span class="statute-tag">LEGAL DOCTRINE 04</span>
          <h3 class="statute-title">The Split Estate: Dominant Mineral Rights &amp; Surface Rights</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">Texas Mineral Estate Supremacy</h4>
            <p class="statute-text">
              In Texas, real estate is severed into the <em>Surface Estate</em> and the <em>Mineral Estate</em>. Under Texas legal doctrine, the mineral 
              estate is <strong>dominant</strong>. The mineral owner or their oil/gas lessee has the legal right to use as much of the surface as reasonably 
              necessary to extract oil, gas, and minerals without the surface owner's permission.
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Railroad Commission (RRC) GIS Overlays</h4>
            <p class="statute-text">
              The platform integrates open public GIS data layers from the <strong>Railroad Commission of Texas (RRC)</strong>, displaying: 
              active and permitted oil/gas wells, plugged dry holes, gathering pipelines, and major transmission corridors across every parcel. 
              This alerts surface buyers to active drilling rigs, pipeline easements, and mineral operations.
            </p>
          </div>
        </div>
      </div>

      <div class="statute-box" style="margin-top: 8px;">
        <div class="statute-header">
          <span class="statute-tag">TAXING ENTITIES 05</span>
          <h3 class="statute-title">Municipal Utility Districts (MUDs) &amp; Mandatory Notices</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">Overlapping Infrastructure Debt</h4>
            <p class="statute-text">
              Texas contains over 1,200 active Municipal Utility Districts (MUDs), Emergency Service Districts (ESDs), and Fresh Water Supply Districts. 
              MUDs issue voter-approved bonds to finance water, sewer, and drainage infrastructure in suburban subdivisions, levying substantial 
              additional property taxes (often adding 0.5% to 1.5% to the annual tax rate).
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Statutory MUD Notice Generation</h4>
            <p class="statute-text">
              Under Texas Water Code § 49.452, sellers must provide buyers with a statutory MUD disclosure notice detailing tax rates, outstanding bond debt, 
              and standby fees prior to contract execution. Failure to disclose grants the buyer rescission rights. The platform automatically identifies 
              MUD boundaries and auto-generates the required statutory disclosure notice.
            </p>
          </div>
        </div>
      </div>

      <div class="statute-box" style="margin-top: 8px;">
        <div class="statute-header">
          <span class="statute-tag">COASTAL HAZARDS &amp; HOUSING STATUTES 06</span>
          <h3 class="statute-title">Coastal Windstorm (TWIA) &amp; Texas Residential Tenancies</h3>
        </div>
        <div class="statute-grid">
          <div class="statute-col">
            <h4 class="statute-sub">Texas Windstorm Insurance (TWIA)</h4>
            <p class="statute-text">
              Properties in Texas's 14 coastal counties and portions of Harris County (east of Hwy 146) are excluded from standard private hurricane wind 
              coverage. They must obtain coverage through the <strong>Texas Windstorm Insurance Association (TWIA)</strong>, requiring WPI-8 building code 
              certificates. The platform displays coastal catastrophe zone designations and TWIA certification indicators.
            </p>
          </div>
          <div class="statute-col">
            <h4 class="statute-sub">Texas Property Code Chapter 92</h4>
            <p class="statute-text">
              Residential leasing in Texas is strictly governed by Texas Property Code Chapter 92. Key mandates include: strict 30-day security deposit 
              accounting deadlines with treble damages for bad-faith retention; mandatory keyless deadbolts and window latches; and certified mail repair 
              notice protocols. The platform's digital lease suite builds these exact statutory protections into every digital agreement.
            </p>
          </div>
        </div>
      </div>
    `
  }
];

console.log('Part 4 defined: Pages 15 to 18.');
