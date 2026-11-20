// pages_part5.js: Build vs Buy, Phased Roadmap, Assumptions & Gaps, Glossary & Conclusion (Pages 19 through 22)

module.exports = [
  // PAGE 19: SECTION 8: BUILD VS. BUY / OUTSIDE SERVICE PROVIDER MATRIX
  {
    num: 19,
    header: 'SECTION 8: BUILD VS. BUY / OUTSIDE PROVIDER MATRIX',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 08</div>
        <h2 class="section-heading">Build vs. Buy / Outside Service Provider Matrix</h2>
      </div>

      <p class="section-intro">
        To maximize capital efficiency and time-to-market, the platform strictly delineates between core proprietary capabilities built internally 
        and commoditized external datasets or regulated financial services licensed from specialized service provider categories.
      </p>

      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 24%;">Platform Capability</th>
            <th style="width: 14%;">Strategy</th>
            <th style="width: 32%;">Service Provider Category</th>
            <th style="width: 30%;">Operational Rationale &amp; Integration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Cadastral Vector Mapping Tiles</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>Commercial Cadastral Parcel Aggregator &amp; State GIS Bureau (TxGIO)</td>
            <td>Avoids negotiating 254 individual county parcel licenses; leverages pre-standardized geometry while syncing directly with top Texas metro CADs.</td>
          </tr>
          <tr>
            <td><strong>Base Map &amp; Aerial Tiles</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>Commercial Map Tile Provider &amp; USGS Topographic Repositories</td>
            <td>Global satellite and street tile infrastructure is capital-intensive to build; license vector street tiles and satellite raster tiles via monthly active user tiers.</td>
          </tr>
          <tr>
            <td><strong>Active Residential MLS Feeds</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>MLS Data Aggregator &amp; Regional Real Estate Board Feeds (RESO Web API)</td>
            <td>Aggregates active listings across major Texas MLSs (HAR, ACTRIS, MetroTex, SABOR) via standardized data feeds and broker participant agreements.</td>
          </tr>
          <tr>
            <td><strong>Tenant Screening Reports</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>FCRA-Certified Consumer Reporting Agency &amp; Credit Bureau Gateway</td>
            <td>Handling raw credit files requires specialized Fair Credit Reporting Act compliance; partner with certified bureau to deliver instant soft-pull scores.</td>
          </tr>
          <tr>
            <td><strong>ACH &amp; Card Rent Rails</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>Licensed Banking-as-a-Service (BaaS) &amp; Payment Processing Gateway</td>
            <td>Avoids state money-transmitter licensing by routing funds through an authorized banking partner handling direct ACH transfers and card processing.</td>
          </tr>
          <tr>
            <td><strong>Electronic Signatures</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>Legally Binding E-Signature Gateway &amp; Audit Trail Seal Provider</td>
            <td>Provides cryptographic tamper-evident sealing, timestamping, and compliance with the Texas Uniform Electronic Transactions Act (UETA).</td>
          </tr>
          <tr>
            <td><strong>School Boundaries &amp; Ratings</strong></td>
            <td><span class="status-pill status-conf">Licensed Partner</span></td>
            <td>National Educational Rating &amp; Boundary Provider</td>
            <td>Licenses geocoded school attendance zones and academic performance metrics updated annually for all Texas Independent School Districts.</td>
          </tr>
          <tr>
            <td><strong>Hazard &amp; Flood Data Layers</strong></td>
            <td><span class="status-pill status-inf">Hybrid Direct</span></td>
            <td>FEMA Digital Flood Insurance Rate Maps (NFIP) &amp; State Water Board (TWDB)</td>
            <td>Direct ingestion of open federal FEMA flood hazard layers combined with proprietary modeling of Texas coastal windstorm zones and river drainage basins.</td>
          </tr>
          <tr>
            <td><strong>Texas Payment Calculator</strong></td>
            <td><span class="status-pill status-conf">Internal Build</span></td>
            <td>Proprietary Internal Development</td>
            <td>Core competitive differentiator: internal engine linking active listings to exact county/city/ISD/MUD tax rates to calculate transparent all-in payments.</td>
          </tr>
          <tr>
            <td><strong>Digital Lease Builder</strong></td>
            <td><span class="status-pill status-conf">Internal Build</span></td>
            <td>Proprietary Internal Development (Legal Counsel Approved)</td>
            <td>Built internally using Texas-promulgated standard lease clauses, custom landlord rules, and statutory Chapter 92 disclosures.</td>
          </tr>
          <tr>
            <td><strong>Search &amp; Filter Architecture</strong></td>
            <td><span class="status-pill status-conf">Internal Build</span></td>
            <td>Proprietary Internal Development</td>
            <td>Proprietary multi-attribute search linking geospatial parcel boundaries, residential listing attributes, and agricultural tax statuses into a single index.</td>
          </tr>
        </tbody>
      </table>
    `
  },

  // PAGE 20: SECTION 9: PHASED IMPLEMENTATION & DELIVERY ROADMAP
  {
    num: 20,
    header: 'SECTION 9: PHASED IMPLEMENTATION & DELIVERY ROADMAP',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 09</div>
        <h2 class="section-heading">Phased Implementation &amp; Delivery Roadmap</h2>
      </div>

      <p class="section-intro">
        The platform execution plan is organized into four sequential delivery phases over 16 months, prioritized by foundational data dependencies, 
        core user value, and commercial revenue generation.
      </p>

      <div class="phase-container">
        <div class="phase-card">
          <div class="phase-top">
            <span class="phase-badge badge-p1">PHASE 01: MONTHS 1–4</span>
            <h4 class="phase-title">Core Cadastral Engine &amp; Texas County Data Foundation</h4>
          </div>
          <div class="phase-details">
            <div class="phase-col">
              <strong>Core Deliverables:</strong>
              <ul class="phase-list">
                <li>Deploy interactive vector map engine with street, satellite, and USGS topo base layers.</li>
                <li>Ingest standardized statewide parcel boundary geometry covering 254 Texas counties.</li>
                <li>Build automated CAD tax assessment sync pipelines for top 25 metropolitan counties.</li>
                <li>Deliver omni-search (address, APN, owner name) and real-time mobile GPS tracking.</li>
                <li>Launch user account registration, saved properties, and individual subscription billing.</li>
              </ul>
            </div>
            <div class="phase-col">
              <strong>Milestone Gate &amp; Risk:</strong>
              <p class="phase-gate">Gate: 98%+ parcel rendering reliability across top 10 metros; sub-second parcel attribute slide-out response. Risk: CAD schema discrepancies in rural counties (mitigated by TxGIO standard schema mapping).</p>
            </div>
          </div>
        </div>

        <div class="phase-card">
          <div class="phase-top">
            <span class="phase-badge badge-p2">PHASE 02: MONTHS 5–8</span>
            <h4 class="phase-title">Residential Marketplace &amp; MLS Listing Integration</h4>
          </div>
          <div class="phase-details">
            <div class="phase-col">
              <strong>Core Deliverables:</strong>
              <ul class="phase-list">
                <li>Integrate regional Texas MLS syndication feeds (HAR, ACTRIS, MetroTex, SABOR).</li>
                <li>Deliver residential search filtering (price, beds, baths, lot size, property type).</li>
                <li>Deploy interactive polygon and lasso boundary drawing tools.</li>
                <li>Launch Property Detail Page showcase with high-res media, school data, and flood zones.</li>
                <li>Release Texas All-In Payment Calculator factoring local ISD and MUD property tax rates.</li>
                <li>Deploy tour scheduling request engine and licensed agent lead routing.</li>
              </ul>
            </div>
            <div class="phase-col">
              <strong>Milestone Gate &amp; Risk:</strong>
              <p class="phase-gate">Gate: Certified MLS syndication compliance across all major Texas boards; 100% adherence to non-disclosure display rules. Risk: MLS approval delays (mitigated by early broker sponsorship engagement).</p>
            </div>
          </div>
        </div>

        <div class="phase-card">
          <div class="phase-top">
            <span class="phase-badge badge-p3">PHASE 03: MONTHS 9–12</span>
            <h4 class="phase-title">Tenant Screening, Digital Leasing &amp; Automated Rent Collection</h4>
          </div>
          <div class="phase-details">
            <div class="phase-col">
              <strong>Core Deliverables:</strong>
              <ul class="phase-list">
                <li>Launch reusable 30-day digital rental application with FCRA-certified credit/criminal/eviction screening.</li>
                <li>Deploy self-service Landlord Portal for listing creation, applicant review, and adverse action delivery.</li>
                <li>Build digital Texas residential lease builder with Chapter 92 statutory disclosures.</li>
                <li>Integrate legally binding e-signature routing with tamper-evident PDF archiving.</li>
                <li>Deploy zero-fee automated ACH rent rails, auto-pay scheduling, and automated late fee enforcement.</li>
              </ul>
            </div>
            <div class="phase-col">
              <strong>Milestone Gate &amp; Risk:</strong>
              <p class="phase-gate">Gate: Successful end-to-end lease execution and automated ACH settlement test; banking compliance sign-off. Risk: Banking underwriting hold periods (mitigated by early BaaS onboarding).</p>
            </div>
          </div>
        </div>

        <div class="phase-card">
          <div class="phase-top">
            <span class="phase-badge badge-p4">PHASE 04: MONTHS 13–16</span>
            <h4 class="phase-title">Enterprise Field Tools, Texas Special Overlays &amp; Advanced Analytics</h4>
          </div>
          <div class="phase-details">
            <div class="phase-col">
              <strong>Core Deliverables:</strong>
              <ul class="phase-list">
                <li>Deploy Railroad Commission of Texas (RRC) oil/gas wells and pipeline GIS overlays.</li>
                <li>Integrate Municipal Utility District (MUD) boundaries and automated statutory notice generation.</li>
                <li>Launch 1-d-1 Agricultural Exemption analysis and Agricultural Rollback Tax liability simulator.</li>
                <li>Deploy Multi-Seat Corporate Management Console with volume billing and shared parcel folders.</li>
                <li>Release bulk GIS export tools (KML, CSV, GeoJSON, Shapefiles) and offline mobile map caching.</li>
              </ul>
            </div>
            <div class="phase-col">
              <strong>Milestone Gate &amp; Risk:</strong>
              <p class="phase-gate">Gate: Enterprise corporate pilot sign-offs from Texas land brokerages and utility surveying teams. Risk: RRC data alignment latency (mitigated by direct state open-data GIS synchronization).</p>
            </div>
          </div>
        </div>
      </div>
    `
  },

  // PAGE 21: SECTION 10: KEY ASSUMPTIONS, RESEARCH GAPS & OPEN ITEMS
  {
    num: 21,
    header: 'SECTION 10: ASSUMPTIONS, GAPS & CONFIRMATION ITEMS',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 10</div>
        <h2 class="section-heading">Key Assumptions, Research Gaps &amp; Open Confirmation Items</h2>
      </div>

      <p class="section-intro">
        In accordance with senior product analysis standards, this proposal distinguishes verified facts from operational assumptions, 
        acknowledges public research limitations, and defines specific decisions requiring resolution prior to engineering execution.
      </p>

      <div class="sub-section">
        <h3 class="sub-heading">Foundational Operational Assumptions</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 25%;">Domain</th>
              <th style="width: 45%;">Operational Assumption</th>
              <th style="width: 30%;">Validation &amp; Impact if Invalid</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Commercial Parcel Licensing</strong></td>
              <td>Statewide parcel aggregators provide commercially licensable vector geometry covering 250+ Texas counties at predictable annual per-seat costs.</td>
              <td>If unavailable, platform must license TxGIO StratMap open data directly and handle in-house schema normalization across CAMA vendors.</td>
            </tr>
            <tr>
              <td><strong>MLS Broker Sponsorship</strong></td>
              <td>Platform can secure broker-of-record sponsorship or MLS participant status to receive direct RESO Web API IDX and VOW syndication feeds.</td>
              <td>If delayed, initial launch focuses on cadastral parcel search, landlord direct listings, and off-market acreage discovery.</td>
            </tr>
            <tr>
              <td><strong>BaaS Payment Underwriting</strong></td>
              <td>Banking-as-a-service partners permit independent residential landlords to collect tenant rent via automated ACH without merchant processor reserve holds.</td>
              <td>If underwriting is restrictive, platform will introduce standard 2-day micro-deposit verification and identity screening for landlords.</td>
            </tr>
            <tr>
              <td><strong>County Appraisal Cadence</strong></td>
              <td>Major urban CADs publish open electronic appraisal rolls annually in the spring with interim certified roll updates in late summer.</td>
              <td>Automated sync pipelines will run quarterly for metropolitan counties and annually for rural districts.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="sub-section" style="margin-top: 8px;">
        <h3 class="sub-heading">Explicit Research Gaps (Public Evaluation Boundaries)</h3>
        <div class="gaps-grid">
          <div class="gap-card">
            <strong>Proprietary Search Ranking Algorithms:</strong>
            <p>The exact mathematical weights used by commercial platforms to rank search listings, distribute sponsored agent leads, and order search results are proprietary and invisible from public screens. In our build, ranking will be transparently determined by geographic proximity, filter match quality, and listing completeness.</p>
          </div>
          <div class="gap-card">
            <strong>Automated Fraud &amp; Scam Scoring Thresholds:</strong>
            <p>The internal statistical thresholds used to automatically suspend fraudulent listings, flag stolen photos, or block high-risk IP addresses operate in closed backend systems. Our platform will deploy standard Fair Housing text filters and cross-reference creator identity with County Clerk deed rolls.</p>
          </div>
          <div class="gap-card">
            <strong>Credit Bureau Scoring Logic:</strong>
            <p>Third-party credit reporting bureaus calculate credit scores and background risk indicators using proprietary models. Our platform relies on certified consumer reporting agencies delivering FCRA-compliant standardized scoring packages.</p>
          </div>
          <div class="gap-card">
            <strong>Enterprise Custom Contract Terms:</strong>
            <p>Published pricing covers 2 to 100 seats; pricing terms for custom enterprise accounts with 500+ users are negotiated under private corporate contracts. Our roadmap establishes clear tiered volume discounts up to 100+ seats with custom pricing for larger fleets.</p>
          </div>
        </div>
      </div>

      <div class="sub-section" style="margin-top: 8px;">
        <h3 class="sub-heading">Actionable Confirmation Items Prior to Phase 1 Kickoff</h3>
        <ul class="action-list">
          <li><strong>Legal Counsel Review:</strong> Retain Texas real estate legal counsel to review the standardized digital residential lease template and verify compliance with Texas Property Code Chapter 92 and TREC advertising rules.</li>
          <li><strong>Banking Partner Selection:</strong> Solicit RFPs from three leading banking-as-a-service providers to finalize ACH transaction fees, float timelines, and underwriting criteria for independent landlords.</li>
          <li><strong>TxGIO Data Alignment:</strong> Finalize technical alignment with the Texas Geographic Information Office (TxGIO) to confirm StratMap Land Parcel update cadences and licensing agreements for commercial redistribution.</li>
        </ul>
      </div>
    `
  },

  // PAGE 22: SECTION 11: PLAIN-LANGUAGE PRODUCT GLOSSARY & CONCLUSION
  {
    num: 22,
    header: 'SECTION 11: GLOSSARY & CONCLUDING ASSESSMENT',
    content: `
      <div class="section-title-group">
        <div class="section-badge">SECTION 11</div>
        <h2 class="section-heading">Plain-Language Product Glossary &amp; Concluding Assessment</h2>
      </div>

      <p class="section-intro">
        To maintain total clarity across non-technical stakeholders, the definitions below explain essential real estate, legal, 
        and cadastral concepts utilized throughout this proposal in plain, everyday language.
      </p>

      <div class="glossary-grid">
        <div class="glossary-item">
          <strong>1-d-1 Agricultural Valuation:</strong>
          A special Texas property tax provision allowing working farmland, timber tracts, and wildlife management acreage to be taxed based on agricultural productive capacity rather than fair market value, substantially reducing annual property taxes.
        </div>
        <div class="glossary-item">
          <strong>Cadastral Parcel:</strong>
          A legally defined piece of land with precise, recorded geometric boundary lines, a unique County Appraisal District property identification number (APN), and registered ownership records.
        </div>
        <div class="glossary-item">
          <strong>County Appraisal District (CAD):</strong>
          The official Texas county government agency responsible for identifying, mapping, and determining the appraised taxable value of all real and personal property within that county.
        </div>
        <div class="glossary-item">
          <strong>Homestead Exemption:</strong>
          A statutory tax exemption for a Texas homeowner's primary residence that removes a portion of the home's value from taxation and caps annual assessment increases to 10%.
        </div>
        <div class="glossary-item">
          <strong>Municipal Utility District (MUD):</strong>
          A specialized political subdivision created under Texas law to finance municipal infrastructure (water, sewer, drainage) in developing suburban areas via property tax levies and voter-approved bonds.
        </div>
        <div class="glossary-item">
          <strong>Non-Disclosure State:</strong>
          A state, such as Texas, where final real estate transaction sales prices are private between buyer and seller and are not recorded in public government documents or county deed filings.
        </div>
        <div class="glossary-item">
          <strong>Parcel Identification Number (APN):</strong>
          A unique numeric or alphanumeric code assigned by a county tax assessor to identify a specific parcel of land for taxation and recordkeeping purposes.
        </div>
        <div class="glossary-item">
          <strong>Railroad Commission of Texas (RRC):</strong>
          The state regulatory agency that oversees oil and gas exploration, drilling operations, pipeline infrastructure, and surface energy activity across Texas.
        </div>
        <div class="glossary-item">
          <strong>Rollback Tax:</strong>
          A mandatory statutory penalty imposed by Texas law when the use of land qualified for agricultural valuation is changed to non-agricultural use, recapturing the prior 3 years of tax savings plus interest.
        </div>
        <div class="glossary-item">
          <strong>Split Estate:</strong>
          A legal doctrine in Texas where ownership of the surface land is severed from ownership of the underlying mineral, oil, and gas rights, with the mineral estate holding legal dominance.
        </div>
        <div class="glossary-item">
          <strong>Texas Real Estate Commission (TREC):</strong>
          The state agency that regulates and licenses real estate brokers, sales agents, inspectors, and residential service companies across Texas, enforcing consumer protection standards.
        </div>
        <div class="glossary-item">
          <strong>Texas Windstorm Insurance Association (TWIA):</strong>
          The state's insurer of last resort providing windstorm and hail coverage for properties located in 14 designated coastal counties and parts of Harris County vulnerable to hurricanes.
        </div>
      </div>

      <div class="concluding-box" style="margin-top: 10px;">
        <h3 class="concluding-title">Concluding Strategic Assessment &amp; Recommendation</h3>
        <p class="concluding-text">
          The Texas real estate market represents an exceptional commercial opportunity for a unified property intelligence and management platform. 
          By bridging the gap between cadastral land mapping utilities and residential consumer portals, the platform solves real, daily frustrations 
          experienced by suburban homebuyers, rural acreage seekers, independent landlords, and enterprise field teams. 
        </p>
        <p class="concluding-text">
          Rather than imposing a generic national template, designing specifically for Texas's legal and geographic conditions—non-disclosure transparency, 
          254-county appraisal district aggregation, agricultural rollback protection, dominant mineral rights overlays, and MUD tax disclosures—creates 
          an enduring, defensible competitive advantage. The phased delivery roadmap outlines a measured, risk-managed progression from core cadastral 
          mapping to a full-cycle real estate marketplace and rental management ecosystem. Executive approval is recommended to proceed with 
          Phase 1 data alignment and partner onboarding.
        </p>
      </div>
    `
  }
];

console.log('Part 5 defined: Pages 19 to 22.');
