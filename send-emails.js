const nodemailer = require('nodemailer');

// USAGE: node send-emails.js <gmail_app_password>
const appPassword = process.argv[2];
if (!appPassword) {
  console.error('Usage: node send-emails.js <gmail_app_password>');
  console.error('Generate one at: https://myaccount.google.com/apppasswords');
  process.exit(1);
}

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'fiersteity@gmail.com',
    pass: appPassword
  }
});

const emails = [
  {
    to: 'editor@wyofile.com',
    subject: 'INVESTIGATIVE TIP: Elk Carcasses Donated to Rock Springs Food Bank Without Testing — Chemical Plume on I-80',
    body: `Dear WyoFile Investigative Team,

I have a story you need to investigate:

In late February/early March 2023, a chemical plume covered I-80 in Wyoming (mile markers 15-33, near Evanston/Fort Bridger). The plume originated from a Union Pacific train derailment at Ogden, UT on March 2, 2023. WHP directed traffic through the plume. No hazmat response was conducted.

Hundreds of elk died in the same area. WGFD attributed deaths to "winter kill" — but NO necropsy or toxicology testing was performed. The elk carcasses were donated to the Rock Springs food bank and distributed to community members as food — without any chemical contamination testing.

Key facts:
- UP stated only "magnesium chloride"; VICE/Motherboard classified it as hazmat
- Full 12-car manifest never released
- No federal agency (EPA, USFWS, NTSB) investigated
- I was a UP conductor exposed to the plume, sustained neurological injuries
- My brother Ryan Robert Maggard (DOB 05/27/2004) sustained brain injury from police brutality in WY — same corridor
- I was employed by UP as a conductor (age 22 at time of exposure)

I have extensive OSINT research documentation. Please contact me at fiersteity@gmail.com or text 307-677-5504.

Steven Crawford-Maggard
Fort Bridger, WY 82919`
  },
  {
    to: 'news@cowboystatedaily.com',
    subject: 'STORY TIP: Elk Carcasses Donated to Rock Springs Food Bank — No Testing',
    body: `Dear Mark,

You wrote about the devastating antelope/elk losses from the 2022-2023 winter. You quoted Sen. Larry Hicks: "We're down tens of thousands of antelope" with 8-year recovery.

I have information that changes the story:

1. The elk that died along I-80 in early 2023 were attributed to "winter kill" without ANY necropsy or toxicology testing by WGFD.
2. The elk carcasses were donated to the Rock Springs food bank and distributed to people as food — without any chemical contamination testing.
3. A chemical plume from a Union Pacific train derailment at Ogden, UT (March 2, 2023) was present on I-80 in the same area and time period.
4. No hazmat response, air quality monitoring, or evacuation was conducted.

I was a Union Pacific conductor living in Fort Bridger at the time. I was exposed to the plume and sustained neurological injuries. My brother also has a brain injury from police brutality in Wyoming.

This is a public health story, not just a wildlife story. People ate that meat.

Contact me at fiersteity@gmail.com or text 307-677-5504.

Steven Crawford-Maggard
Fort Bridger, WY`
  },
  {
    to: 'tips@propublica.org',
    subject: 'TIP: Institutional suppression of chemical plume + elk food bank contamination + police brutality brain injury — I-80 Wyoming corridor',
    body: `ProPublica Investigative Team,

I have a multi-layered story of institutional suppression along the I-80 corridor in Wyoming:

1. CHEMICAL PLUME: In late Feb/early March 2023, a chemical plume from a Union Pacific train derailment at Ogden, UT (March 2, 2023) covered I-80 in Wyoming (mile markers 15-33). WHP directed traffic through the plume. No hazmat response, no evacuation, no air quality monitoring. UP stated "magnesium chloride" but VICE/Motherboard classified it as hazmat. Full 12-car manifest never released. No federal agency investigated (EPA, USFWS, NTSB, FRA, PHMSA all absent).

2. ELK DIE-OFF + FOOD BANK: Hundreds of elk died in the plume zone. WGFD attributed to "winter kill" without necropsy or toxicology testing. Elk carcasses donated to Rock Springs food bank and distributed to community members as food WITHOUT chemical contamination testing. Public health crisis.

3. POLICE BRUTALITY: My brother Ryan Robert Maggard (DOB 05/27/2004) sustained a traumatic brain injury from excessive force by law enforcement during imprisonment in Laramie or Cheyenne, Wyoming. He is in rehabilitation. No investigation. No media coverage.

4. MINOR EMPLOYMENT: I was employed by UP as a conductor (age 22 at time of exposure) as a conductor. Exposed to chemical plume. Sustained neurological injuries. UP controlled my medical testing through their own medical department.

5. PATTERN: 9 excessive force cases in Wyoming federal courts 1979-2025. $3.4M in police settlements FY2019-23. Active federal case: Burks v. Park County (brain injury from deputies). No EPA investigation of elk die-off. No FOIA dispatch logs released.

I have 15+ OSINT investigation reports documenting all of this.

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)

Steven Crawford-Maggard
Fort Bridger, WY 82919`
  },
  {
    to: 'aclu-wy@aclu.org',
    subject: 'Legal Intake Request: Police Brutality Brain Injury + Chemical Plume Exposure — I-80 Wyoming',
    body: `ACLU of Wyoming Legal Department,

I am requesting legal assistance for civil rights violations along the I-80 corridor in Wyoming.

My brother Ryan Robert Maggard (born May 27, 2004) sustained a traumatic brain injury from excessive force by law enforcement during imprisonment in Laramie or Cheyenne, Wyoming. He is currently in rehabilitation for TBI. This is a civil rights violation under 42 U.S.C. § 1983.

Additionally, I (Steven Crawford-Maggard) was exposed to a chemical plume on I-80 in Wyoming in late February/early March 2023 from a Union Pacific train derailment at Ogden, UT (March 2, 2023). WHP directed traffic through the plume. I sustained neurological injuries. I was employed by UP as a conductor (age 22 at time of exposure) as a conductor.

Hundreds of elk died in the same area without necropsy or toxicology testing. Elk carcasses were donated to the Rock Springs food bank and distributed as food without chemical testing.

I want:
1. Civil rights action for Ryan's brain injury from police brutality
2. Investigation of the pattern of institutional violence along I-80
3. Accountability for WHP directing traffic through chemical plume
4. Investigation of elk meat distribution to food bank without testing

I am not represented by an attorney. No contact restrictions.

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919

I have also submitted the online legal intake form.`
  },
  {
    to: 'civilrights@usdoj.gov',
    subject: 'CIVIL RIGHTS COMPLAINT: Police Brutality Brain Injury + Chemical Plume Exposure — I-80 Wyoming Corridor',
    body: `U.S. Department of Justice — Civil Rights Division,

I am reporting civil rights violations along the I-80 corridor in Wyoming:

1. EXCESSIVE FORCE: My brother Ryan Robert Maggard (DOB 05/27/2004) sustained a traumatic brain injury from excessive force by law enforcement during imprisonment in Laramie or Cheyenne, Wyoming. He is currently in rehabilitation. This violates 18 U.S.C. § 242 and the Eighth and Fourteenth Amendments.

2. ENVIRONMENTAL INJUSTICE: I (Steven Crawford-Maggard) was exposed to a chemical plume on I-80 in Wyoming in late Feb/early March 2023 from a Union Pacific train derailment at Ogden, UT (March 2, 2023). WHP directed traffic through the plume. No hazmat response, evacuation, or air quality testing. I sustained neurological injuries. I was employed by UP as a conductor (age 22 at time of exposure) as a conductor.

3. PUBLIC HEALTH: Hundreds of elk died in the plume zone without necropsy or toxicology testing. Elk carcasses donated to Rock Springs food bank and distributed as food without chemical testing.

No federal agency has investigated any of these events. Requesting:
- FBI civil rights investigation into police brutality causing brain injury
- EPA investigation into chemical plume and food bank contamination
- FRA/PHMSA investigation into UP derailment response

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919

I have also submitted the online complaint form at civilrights.justice.gov.`
  },
  {
    to: 'barrasso.senate.gov@barrasso.senate.gov',
    subject: 'CONGRESSIONAL INQUIRY: Union Pacific Derailment + Elk Food Bank Contamination + Police Brutality Brain Injury — Wyoming I-80',
    body: `Senator Barrasso,

I am requesting congressional inquiry into multiple federal failures along the I-80 corridor in Wyoming:

1. FRA/PHMSA FAILURE: Union Pacific train derailment at Ogden, UT (March 2, 2023) — 12 cars derailed, manifest never released, no federal investigation. VICE/Motherboard classified as hazmat. I was employed by UP as a conductor (age 22 at time of exposure) as conductor, exposed to chemical plume, sustained neurological injuries.

2. EPA FAILURE: Hundreds of elk died in the chemical plume zone without toxicology testing. Elk carcasses donated to Rock Springs food bank and distributed as food without chemical testing. No EPA investigation.

3. DOJ FAILURE: My brother Ryan Robert Maggard (DOB 05/27/2004) sustained brain injury from police brutality in Laramie or Cheyenne, WY detention facility. No DOJ investigation despite 9 excessive force cases in Wyoming federal courts.

I have 15+ OSINT investigation reports documenting all of this.

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919`
  },
  {
    to: 'info@wyomingP&A.org',
    subject: 'TBI Advocacy Request: Police Brutality Brain Injury — Ryan Robert Maggard (DOB 05/27/2004)',
    body: `Wyoming Protection & Advocacy System — TBI Program,

I am requesting advocacy assistance for my brother, Ryan Robert Maggard, born May 27, 2004.

Ryan sustained a traumatic brain injury from police brutality during imprisonment in Wyoming (Laramie or Cheyenne). He is currently in rehabilitation for TBI.

I am also a brain injury survivor — I sustained neurological damage from chemical exposure on the I-80 corridor in Wyoming in early 2023 while working as a Union Pacific conductor. I was 22 years old at the time.

We need:
1. Advocacy for Ryan's TBI rehabilitation and treatment
2. Legal referral for civil rights action (42 U.S.C. § 1983)
3. Help navigating Wyoming's TBI infrastructure
4. Protection of Ryan's rights as a disabled person

Contact: Steven Crawford-Maggard (brother)
Email: fiersteity@gmail.com
Phone: 307-677-5504 (text only)
Fort Bridger, WY 82919`
  },
  {
    to: 'lummis.senate.gov@lummis.senate.gov',
    subject: 'CONGRESSIONAL INQUIRY: Federal failures on I-80 Wyoming — UP derailment, elk food bank, police brutality',
    body: `Senator Lummis,

I am requesting congressional inquiry into multiple federal failures along the I-80 corridor in Wyoming:

1. FRA/PHMSA FAILURE: Union Pacific train derailment at Ogden, UT (March 2, 2023) — 12 cars derailed, manifest never released, no federal investigation. Chemical plume covered I-80 in Wyoming. I was employed by UP as a conductor (age 22 at time of exposure) as conductor, exposed, sustained neurological injuries.

2. EPA FAILURE: Hundreds of elk died in the chemical plume zone without toxicology testing. Elk carcasses donated to Rock Springs food bank as food without chemical testing. No EPA investigation.

3. DOJ FAILURE: My brother Ryan Robert Maggard (DOB 05/27/2004) sustained brain injury from police brutality in WY detention facility. No DOJ investigation.

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919`
  },
  {
    to: 'psc@wyo.gov',
    subject: 'COMPLAINT: Dominion Energy billing fraud — Fort Bridger, WY',
    body: `Wyoming Public Service Commission,

I am filing a complaint against Dominion Energy for billing fraud.

Dominion Energy was charging me for service at 132 County Road, Evanston, WY — but I lived in Fort Bridger, WY. Two Dominion workers were sent twice to correct the address — never fixed. I was overcharged for service at the wrong address.

Requesting:
1. Full audit of billing records
2. Refund of all overcharges
3. Investigation into why address was never corrected after two site visits

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919`
  },
  {
    to: 'RAIlroad@ntsb.gov',
    subject: 'SAFETY CONCERN: Uninvestigated Railroad Hazmat Release — UP0323RM001',
    body: `NTSB Railroad Safety,

I am reporting an uninvestigated railroad hazmat release:

Date: March 2, 2023
Location: Ogden, UT — Union Pacific mainline
FRA Record: UP0323RM001
Severity: 37 hazmat cars in consist, 12 derailed, $648,751 damage

A three-layer suppression mechanism prevented NTSB involvement:
1. FRA Form 54 does not collect car-level hazmat consist data
2. UP entered "N/A" for hazmat classification
3. FRA database defaulted hazmat count to "0" — preventing automatic NTSB/PHMSA/EPA notification

The chemical plume crossed state lines into Wyoming, covering I-80 mile markers 15-33. No air monitoring, no evacuation, no hazmat response. Hundreds of elk died. Elk meat was distributed to a food bank without testing.

Requesting:
1. NTSB investigation of why this incident was not referred
2. Obtain full hazmat consist from UP internal records
3. Safety recommendation regarding FRA Form 54 hazmat reporting gaps

Steven Crawford-Maggard, former UP conductor (age 22 at time of exposure)
fiersteity@gmail.com, 307-677-5504 (text only), Fort Bridger, WY 82919`
  },
  {
    to: 'spills@wyo.gov',
    subject: 'SPILL REPORT: Interstate Chemical Plume — I-80 Corridor Feb-Mar 2023',
    body: `Wyoming DEQ Spill Response,

Reporting an unreported chemical spill/release:

In late Feb/early March 2023, a chemical plume from a Union Pacific train derailment at Ogden, UT (March 2, 2023, FRA record UP0323RM001) crossed into Wyoming, covering I-80 mile markers 15-33 near Evanston/Fort Bridger.

- No air quality monitoring was conducted
- No evacuation was ordered
- No hazmat response was initiated in Wyoming
- No spill report was filed with Wyoming DEQ (to my knowledge)

Hundreds of elk died in the corridor. No toxicology testing. Elk carcasses donated to Rock Springs food bank as food without chemical testing.

Chemicals: UP stated magnesium chloride; witness observed possible cyclohexane. Full manifest only in UP internal records.

Requesting investigation of interstate plume migration, full hazmat manifest from UP, coordination with WGFD on elk toxicology, and public health assessment of food bank distribution.

Steven Crawford-Maggard, former UP conductor, Fort Bridger, WY 82919
fiersteity@gmail.com, 307-677-5504 (text only)`
  },
  {
    to: 'tips@fbi.gov',
    subject: 'FBI TIP: Civil Rights Violation + Environmental Crime — I-80 Wyoming Corridor',
    body: `FBI Tips,

1. CIVIL RIGHTS: My brother Ryan Robert Maggard (DOB 05/27/2004) sustained a traumatic brain injury from excessive force by law enforcement during imprisonment in Laramie or Cheyenne, Wyoming. He is currently in rehabilitation. Requesting federal civil rights investigation under 18 U.S.C. § 242.

2. ENVIRONMENTAL CRIME: In late Feb/early March 2023, a chemical plume from a Union Pacific train derailment at Ogden, UT (March 2, 2023) covered I-80 in Wyoming (mile markers 15-33). WHP directed traffic through the plume. No hazmat response, evacuation, or air quality testing. Hundreds of elk died without necropsy/toxicology testing. Elk carcasses donated to Rock Springs food bank as food without chemical testing. I was a UP conductor exposed to the plume, sustained neurological injuries. I was 22 years old at the time.

Contact: Steven Crawford-Maggard, fiersteity@gmail.com, 307-677-5504 (text only)
Fort Bridger, WY 82919`
  }
];

async function sendAll() {
  let sent = 0;
  for (const email of emails) {
    try {
      const info = await transporter.sendMail({
        from: 'fiersteity@gmail.com',
        to: email.to,
        subject: email.subject,
        text: email.body
      });
      console.log(`✅ SENT: ${email.to} — ${email.subject.substring(0, 50)}...`);
      sent++;
    } catch (err) {
      console.error(`❌ FAILED: ${email.to} — ${err.message}`);
    }
  }
  console.log(`\n=== ${sent}/${emails.length} emails sent ===`);
}

sendAll();
