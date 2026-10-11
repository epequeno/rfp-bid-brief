# Fixture provenance

Eighteen third-party documents, all retrieved **2026-10-11** from the issuing organisation's own
website, all verified at retrieval time to be real PDFs with an extractable text layer (no OCR
anywhere in this repo — OCR is a non-goal of the decision layer).

These are **public records**: US state, local and municipal government solicitations, a state
university system, a community college, and two state-chartered non-profits. Each row names the
issuer's own published copy. Read [`NOTICE.md`](NOTICE.md) before redistributing.

**No fixture is derived from, or related to, any prior commercial engagement, employer or client.**
The set was selected from public sources specifically to satisfy that constraint: every document
here was issued by the organisation that published it, and none passed through a previous
employer's capture process. That was a decision about the fixture selection, not an accident of
searching — and it is why four plausible-looking candidates were rejected.

| # | Fixture | Issuer (type) | Subject | pp |
|---|---|---|---|---|
| 1 | `city-of-snohomish-it-strategic-plan-rfp.pdf` | City of Snohomish, WA (municipal) | Six-year IT strategic plan (advisory) | 7 |
| 2 | `city-of-spicer-mn-managed-it-services-2026.pdf` | City of Spicer, MN (municipal) | Managed IT services, three-year term | 6 |
| 3 | `coastal-bend-college-erp-sis-rfp-2026-01.pdf` | Coastal Bend College, TX (community college) | ERP and student information systems | 64 |
| 4 | `community-action-partnership-kern-information-systems-consultant.pdf` | Community Action Partnership of Kern, CA (non-profit) | Information systems consultant: AI integration, Microsoft Fabric, virtual assistant | 14 |
| 5 | `energy-trust-of-oregon-crm-migration-to-d365.pdf` | Energy Trust of Oregon (state-chartered non-profit) | On-premises CRM → Microsoft Dynamics 365 cloud | 12 |
| 6 | `hacc-rfp-26022-cloud-document-management.pdf` | Harrisburg Area Community College, PA | Cloud document management and workflow automation | 23 |
| 7 | `inprs-rfp-23-04-cloud-migration-iam-ztna.pdf` | Indiana Public Retirement System (state agency) | Cloud migration discovery, IAM and zero-trust strategy | 38 |
| 8 | `mass-tech-ai-hub-data-commons-consulting-2026-jaii-01.pdf` | Massachusetts Technology Collaborative (quasi-public) | AI Hub Data Commons: collaborative consulting | 10 |
| 9 | `palm-beach-mpo-rfp-2026-07-it-services.pdf` | Palm Beach Metropolitan Planning Organization, FL | IT services and management | 27 |
| 10 | `tahoe-transportation-district-it-consulting-2025.pdf` | Tahoe Transportation District, CA/NV | IT consulting and support | 43 |
| 11 | `u-maine-system-rfp-2026-065-enterprise-genai-services.pdf` | University of Maine System | Enterprise generative AI services | 48 |
| 12 | `indian-river-county-utilities-technology-master-plan-rfp.pdf` | Indian River County Dept. of Utility Services (IRCDUS), FL (county utility) | Utilities Technology Master Plan and Customer Information System — consulting services | 16 |
| 13 | `allentown-school-district-data-warehousing-services-2026.pdf` | Allentown School District, PA (school district) | Data warehousing services | 19 |
| 14 | `cisd-texas-rfp-26-10-enterprise-data-warehouse-software.pdf` | Cleveland Independent School District, TX (school district) | Enterprise data warehouse and performance management software | 57 |
| 15 | `kansas-city-kansas-cc-rfp-26-003-data-warehouse-analytics-platform.pdf` | Kansas City Kansas Community College (community college) | Data warehouse and analytics platform | 19 |
| 16 | `college-of-western-idaho-rfp-05-2024-ai-technology-services.pdf` | College of Western Idaho (community college) | AI technologies and services for faculty and students | 20 |
| 17 | `judicial-council-of-california-rfp-it-2026-213-rb-technical-staff-augmentation.pdf` | Judicial Council of California (state court system) | Master agreements for technical staff augmentation services | 20 |
| 18 | `savec-alaska-managed-it-services-2026.pdf` | Southwest Alaska Vocational & Educational Center (non-profit) | Managed IT services: help desk, network administration, on-site support | 5 |

## Source URLs

| # | Source (the issuer's own copy) |
|---|---|
| 1 | https://www.snohomishwa.gov/DocumentCenter/View/9780/RFP-Information-Technology-Strategic-Plan |
| 2 | http://spicermn.govoffice.com/uploads/dm/80063/RFP_IT_Services_2026_APPROVED.pdf |
| 3 | https://www.coastalbend.edu/finance_business_operations/files/26-03-cbc-it-2026-01-erp-and-student-information-systems-rfp.pdf |
| 4 | https://www.capk.org/wp-content/uploads/2025/11/RFP-IS-2025-001-INFORMATION-SYSTEMS-CONSULTANT.pdf |
| 5 | https://www.energytrust.org/wp-content/uploads/2026/03/CRM-Migration-RFP.pdf |
| 6 | https://hacc.org/wp-content/uploads/2026/03/RFP-26022-Cloud-Based-Document-Management-Workflow-Automation-Software-Solution.pdf |
| 7 | https://www.in.gov/inprs/files/RFP23-04CloudMigrationIdentityAccessMgmt.pdf |
| 8 | https://aihub.masstech.org/sites/default/files/2025-09/2026-JAII-01%20AI%20Hub%20Data%20Commons%20Consulting%20Services.pdf |
| 9 | https://palmbeachmpo.org/wp-content/uploads/2026/04/RFP-2026-07-IT-Services-and-Management.pdf |
| 10 | https://tahoetransportation.org/wp-content/uploads/2025/07/TTD-RFP-Information-Technology-Consulting-and-Support-Jul2025.pdf |
| 11 | https://www.maine.edu/strategic-procurement/wp-content/uploads/sites/5/2026/03/07-2026-065-RFP-IT-Addendum1-1.pdf |

## Notes that affect how a fixture may be read

- **#11 is the addendum revision**, not the original release: it carries the Q&A responses that
  establish the load-bearing facts for this fixture (that the University is buying licences for a
  **vendor-hosted SaaS solution**, that a flat-rate/unlimited-usage requirement applies, and that
  the solution must be multi-model). Citing this fixture means citing the addendum.
- **#1, #2, #9 and #4 were published on agency-hosted document endpoints** (`DocumentCenter`,
  `govoffice`, WordPress uploads) rather than in a procurement portal. Two other candidates were
  dropped for exactly this reason: a City of Antioch RFQ returned HTTP 403 to every request, and
  portal-gated documents are not reproducible, so they are not fixtures.
- **#5 and #4 are non-profit issuers**, included because they publish on the same terms as the
  government bodies and add issuer variety. They are not government records.
- Page counts are from `pdfinfo` at retrieval.

## Integrity manifest

`tools/verify-fixtures.sh` recomputes these hashes and fails if any fixture has changed. Run it
with `just verify-fixtures`. A fixture that has been edited in place is no longer the document its
issuer published, and any span citation against it is void — so this is a gate, not a formality.

```
3185dc70be05115a436e9bed5828e3e120a04e87c30b170e67469c0680f5314c  city-of-snohomish-it-strategic-plan-rfp.pdf
e82998cfbb27674ae3c4dc061519155ef5ddb49760bc97e20e781d52f8713cd4  city-of-spicer-mn-managed-it-services-2026.pdf
c327a9cd4c22b001ae89b98ebd5866317f27838912d76b869c10c04d07edec66  coastal-bend-college-erp-sis-rfp-2026-01.pdf
373bc828a399a2e7dce746d73bedb1cbdf88e23430b85910130491b6caabbd9c  community-action-partnership-kern-information-systems-consultant.pdf
9d60913497b846582963c58672ad6ef8e747ff4212695c1023f4a5051aa0d20f  energy-trust-of-oregon-crm-migration-to-d365.pdf
2a8d205e58488f29331d0ec118b1887f78a943ecb0305a25716f319800de67d8  hacc-rfp-26022-cloud-document-management.pdf
1ba14c71c5bbdd3f9acd7336877abd2393ebc9ee0864c01a548caada3f6e70d6  inprs-rfp-23-04-cloud-migration-iam-ztna.pdf
b38b517f17db024f12a3a282c267e9f8fb1ccad863170e57a7af66420d0b8c97  mass-tech-ai-hub-data-commons-consulting-2026-jaii-01.pdf
ff7a200c37a8306d55d633cbfb26dfa5068c2771a55183a02b0b633b7ea5f302  palm-beach-mpo-rfp-2026-07-it-services.pdf
69633f114695bcd910017781cc0ee98eb8400d3371e489a90886797dd79d8f32  tahoe-transportation-district-it-consulting-2025.pdf
42d5c1c1581e8da02782152d9bde11ae3556ea9d114f0318687fbbb3d64b0d5a  u-maine-system-rfp-2026-065-enterprise-genai-services.pdf
87aa0da0ac74c581281b6c417ba4dcc3b2f60f601906aa12e57b51b97bc4f694 allentown-school-district-data-warehousing-services-2026.pdf
7a0a2b2e4317583c4e10c4432cc55b78a111db807d3e8732c321623eead4164e cisd-texas-rfp-26-10-enterprise-data-warehouse-software.pdf
40d0d488ccb27b291705f6f2c76ac98ea7d9f0530a9de80c3b04d704b074aa39 college-of-western-idaho-rfp-05-2024-ai-technology-services.pdf
fda10cb752e7b189e2b90e737ff1e3f822ff7f7264cc0c87b26585ef5b956b95 indian-river-county-utilities-technology-master-plan-rfp.pdf
164170ccea518ed31a16285e135ba9ba5688406ea3dbcd7117708d68374dde1d judicial-council-of-california-rfp-it-2026-213-rb-technical-staff-augmentation.pdf
45e485ac4d0cea2d659a999b02bc1f99d577042c4b3b8b0afc77d89b2b822bb0 kansas-city-kansas-cc-rfp-26-003-data-warehouse-analytics-platform.pdf
e6dfc120042ac98af20dfb3d014841b2c17c004f5fbe5566b1cf3362e643972c savec-alaska-managed-it-services-2026.pdf
```
