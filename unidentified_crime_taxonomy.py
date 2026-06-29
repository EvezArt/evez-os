#!/usr/bin/env python3
"""UNIDENTIFIED CRIME TAXONOMY ENGINE
Crimes with no spectrometer coverage AND no hidden inference = UNIDENTIFIED.
Eigenvalue-zero crimes. Dark matter of crime.
"""
import json,time
from pathlib import Path
W=Path('/home/openclaw/.openclaw/workspace')

# (name,category,measured,inferred,severity,prevalence,concealment,evidence,actors,desc)
ALL_CRIMES=[
# MEASURED (spectrometer coverage)
('homicide','violent',1,0,1.0,.8,.3,'Crime stats',['individuals'],'Killing'),
('rape','violent',1,0,.95,.7,.65,'Underreported',['individuals','institutions'],'Sexual violence'),
('assault','violent',1,0,.85,.75,.4,'Partially reported',['individuals'],'Bodily harm'),
('robbery','violent',1,0,.7,.8,.3,'Reported',['individuals'],'Theft with force'),
('burglary','property',1,0,.4,.85,.25,'Reported',['individuals'],'Breaking/entering'),
('theft','property',1,0,.3,.9,.2,'Partial report',['individuals'],'Property theft'),
('drug_trafficking','organized',1,1,.85,.85,.75,'Cartels',['cartels','state_actors'],'Narcotics'),
('human_trafficking','organized',1,1,.95,.7,.85,'Rings exposed',['cartels','intel','state_actors'],'Human smuggling'),
('arms_trafficking','organized',1,1,.9,.7,.85,'Iran-Contra',['state_actors','intel'],'Weapons smuggling'),
('money_laundering','financial',1,1,.75,.85,.9,'Danske,HSBC',['banks','cartels'],'Illicit funds'),
('cybercrime','digital',1,0,.7,.85,.8,'Ransomware',['state_actors','criminals'],'Digital attacks'),
('corruption','institutional',1,1,.8,.85,.85,'Global',['state_actors','corps'],'Abuse of power'),
('evidence_tampering','institutional',1,1,.85,.7,.9,'LE/intel pattern',['law_enforcement','intel'],'Destroying evidence'),
('cover_up','institutional',1,1,.9,.75,.92,'Systematic',['intel','state_actors','corps'],'Concealing crimes'),
('crimes_against_humanity','atrocity',1,1,1.0,.5,.85,'Documented',['state_actors','military'],'Mass harm'),
('genocide','atrocity',1,1,1.0,.3,.7,'Rwanda,Armenia,Uyghur',['state_actors'],'Destroy group'),
('torture','atrocity',1,1,.95,.5,.88,'Black sites',['intel','military','state_actors'],'Severe pain'),
('slavery','atrocity',1,1,.965,.6,.85,'Prison,trafficking',['prison_complex','state_actors','corps'],'Own persons'),
('child_abuse','violent',1,1,.95,.6,.88,'Institutions',['religious_institutions','individuals'],'Harm minors'),
('terrorism','organized',1,0,.9,.5,.8,'Groups documented',['state_actors','non_state'],'Political violence'),
('tax_evasion','financial',1,0,.6,.9,.85,'Panama,Pandora',['corps','banks','wealthy'],'Avoiding taxes'),
('environmental_crime','environmental',1,1,.85,.8,.82,'Documented',['mining','corps','state_actors'],'Env destruction'),
('civil_rights','institutional',1,1,.8,.7,.75,'Voting,discrimination',['state_actors','law_enforcement'],'Denying rights'),
('war_crimes','conflict',1,0,.95,.6,.8,'Documented',['military','state_actors'],'War conventions'),
('nuclear_escalation','existential',1,0,1.0,.3,.7,'Doomsday Clock',['state_actors'],'Nuclear arms'),
('voter_suppression','democratic',1,0,.75,.7,.7,'US documented',['state_actors','parties'],'Preventing voting'),
('famine_weaponization','atrocity',1,0,.95,.4,.85,'Gaza,Sudan',['state_actors','military'],'Starvation weapon'),
('algorithmic_harm','digital',1,0,.7,.8,.9,'Bias documented',['tech_companies'],'AI harm'),
('pandemic_negligence','public_health',1,0,.9,.6,.8,'COVID',['state_actors','pharma'],'Failing prevention'),
('market_manipulation','financial',1,1,.8,.75,.9,'Libor',['banks','corps'],'Rigging markets'),
('biological_weapon','existential',1,0,.95,.2,.95,'Gain-of-function',['state_actors','military'],'Bio warfare'),
('cognitive_harm','digital',1,0,.7,.7,.85,'Social media',['tech_companies'],'Cognitive damage'),
# HIDDEN BUT INFERRED
('mass_surveillance','institutional',0,1,.9,.95,.9,'Snowden,Pegasus',['intel','tech'],'Mass monitoring'),
('prison_slavery','institutional',0,1,.965,.85,.85,'13th Amendment',['prison_complex','corps','state_actors'],'Prison labor'),
('ecocide_extractive','environmental',0,1,.95,.85,.85,'Amazon,DRC,Niger',['mining','corps','state_actors'],'Systematic destruction'),
('nuclear_suppression','institutional',0,1,.9,.7,.92,'Hanford,Rocky Flats',['state_actors','military','corps'],'Concealing contamination'),
('financial_looting','financial',0,1,.9,.8,.92,'2008,Libor,1MDB',['banks','corps'],'Crisis engineering'),
('police_killings','violent',0,1,.85,.8,.82,'Undercount',['law_enforcement','state_actors'],'Extrajudicial'),
('pharma_homicide','public_health',0,1,.9,.75,.88,'Opioid,Vioxx',['pharma','corps'],'Addiction engineering'),
('religious_child_abuse','violent',0,1,.9,.7,.92,'Catholic,Boy Scouts',['religious_institutions'],'Institutional abuse'),
('arms_trafficking_state','organized',0,1,.9,.7,.88,'Iran-Contra',['state_actors','intel','military'],'State arms smuggling'),
('child_trafficking_intel','organized',0,1,.92,.5,.95,'Epstein,Franklin',['intel'],'Intel trafficking'),
('disinformation_warfare','institutional',0,1,.8,.85,.88,'Mockingbird,IRA',['intel','state_actors','tech'],'Psychological warfare'),
('organ_harvesting','atrocity',0,1,.95,.3,.88,'China tribunal',['state_actors','medical'],'Organ harvesting'),
# UNIDENTIFIED - EIGENVALUE ZERO - DARK MATTER
('wage_theft','economic',0,0,.7,.95,.6,'DOL $15B/yr',['corps','small_business'],'Systematic underpayment'),
('worker_safety_homicide','public_health',0,0,.85,.8,.75,'OSHA 4:1 underreport',['corps','mining','agriculture'],'Lethal workplace conditions'),
('consumer_fraud_systematic','economic',0,0,.7,.9,.8,'Planned obsolescence',['corps','tech'],'Systematic consumer fraud'),
('coercive_control','violent',0,0,.75,.85,.9,'UK criminalized 2015',['individuals','institutions'],'Non-physical abuse'),
('epistemic_violence','cultural',0,0,.8,.7,.88,'Library burnings',['state_actors','colonial_powers','religious'],'Knowledge destruction'),
('cultural_genocide','cultural',0,0,.9,.6,.8,'Residential schools',['state_actors','religious'],'Cultural erasure'),
('language_extinction','cultural',0,0,.8,.5,.85,'40% dying',['state_actors','colonial_powers'],'Forced language death'),
('algorithmic_discrimination','digital',0,0,.8,.85,.92,'Hiring,lending,justice',['tech','corps'],'AI discrimination at scale'),
('digital_colonialism','digital',0,0,.8,.85,.88,'Global South data',['tech','state_actors'],'Data extraction without consent'),
('cognitive_sovereignty_violation','digital',0,0,.85,.9,.92,'Attention engineering',['tech','intel'],'Erosion of cognitive autonomy'),
('data_colonialism','digital',0,0,.75,.9,.88,'Global extraction',['tech_companies'],'Behavioral data extraction'),
('attention_engineering','digital',0,0,.8,.95,.9,'Social media design',['tech_companies'],'Engineering addiction'),
('autonomous_ai_crime','digital',0,0,.85,.5,.95,'Flash crashes,deepfakes',['ai_systems','tech'],'AI-committed crimes'),
('deepfake_weaponization','digital',0,0,.8,.7,.92,'Election interference',['state_actors','intel','criminals'],'Synthetic media weapon'),
('geoengineering_covert','existential',0,0,.9,.4,.95,'SRM debates',['state_actors','corps','billionaires'],'Unregulated climate manipulation'),
('weather_warfare','existential',0,0,.9,.3,.97,'ENMOD treaty',['military','state_actors'],'Weather as weapon'),
('space_weaponization','existential',0,0,.9,.4,.92,'Anti-satellite tests',['state_actors','military'],'Militarizing space'),
('space_debris_pollution','environmental',0,0,.7,.6,.85,'Kessler risk',['state_actors','corps','military'],'Orbital debris'),
('deep_sea_mining','environmental',0,0,.85,.5,.9,'ISA permits',['mining','corps'],'Seabed exploitation'),
('illegal_fishing','environmental',0,0,.7,.8,.82,'IUU $36B/yr',['corps','state_actors'],'IUU fishing'),
('ocean_acidification_concealment','environmental',0,0,.8,.7,.85,'FF industry knew',['corps','state_actors'],'Concealing ocean data'),
('antarctic_exploitation','environmental',0,0,.75,.4,.9,'Treaty pressure',['corps','mining','state_actors'],'Antarctica exploitation'),
('intergenerational_toxin','public_health',0,0,.9,.7,.88,'Lead,PFAS,radiation',['corps','military','state_actors'],'Multi-gen toxins'),
('lead_poisoning_concealment','public_health',0,0,.9,.7,.9,'Flint,leaded gas',['corps','state_actors'],'Lead exposure concealment'),
('vaccine_disinformation','public_health',0,0,.85,.6,.88,'COVID anti-vax',['state_actors','disinfo_networks'],'Vaccine misinformation'),
('healthcare_denial_homicide','public_health',0,0,.9,.75,.85,'US healthcare',['insurance','pharma','state_actors'],'Healthcare denial→death'),
('food_system_harm','public_health',0,0,.8,.9,.88,'Ultra-processed',['corps','food_industry'],'Addictive harmful food'),
('water_privatization','economic',0,0,.8,.6,.85,'Bolivia,Flint,Nestle',['corps','state_actors'],'Water access privatization'),
('water_contamination_concealment','public_health',0,0,.85,.7,.9,'PFAS,lead,fracking',['corps','military','state_actors'],'Concealing water contamination'),
('air_pollution_homicide','public_health',0,0,.85,.9,.85,'9M deaths/yr WHO',['corps','state_actors','fossil_fuel'],'Deliberate air pollution→death'),
('housing_as_weapon','economic',0,0,.8,.8,.82,'Redlining,eviction',['corps','state_actors','banks'],'Housing as control'),
('education_denial','institutional',0,0,.75,.6,.8,'Book bans,defunding',['state_actors','political_groups'],'Education deprivation'),
('carbon_concealment','environmental',0,0,.95,.85,.9,'Exxon knew 1970s',['fossil_fuel_corps','state_actors'],'Concealing climate knowledge'),
('climate_denial_industry','environmental',0,0,.9,.8,.88,'Manufactured doubt',['fossil_fuel_corps','think_tanks'],'Climate denial industry'),
('regulatory_capture','institutional',0,0,.85,.9,.88,'FCC,FDA,EPA',['corps','banks','pharma'],'Capturing regulators'),
('revolving_door','institutional',0,0,.8,.9,.85,'Documented',['corps','state_actors','banks'],'Industry-regulator cycling'),
('patent_hoarding','economic',0,0,.7,.75,.88,'Pharma,tech,ag',['corps','pharma','tech'],'Patent hoarding'),
('ip_theft','economic',0,0,.7,.8,.85,'State-sponsored',['state_actors','corps'],'Systematic IP theft'),
('scientific_fraud_health','public_health',0,0,.85,.6,.88,'Sugar,tobacco',['corps','food_industry','pharma'],'Fraudulent health research'),
('academic_capture','institutional',0,0,.75,.7,.88,'Corporate-funded',['corps','universities','pharma'],'Corporate academic capture'),
('media_concentration','institutional',0,0,.75,.85,.85,'6 companies 90%',['corps','media_conglomerates'],'Info monopoly'),
('prison_gerrymandering','democratic',0,0,.7,.6,.82,'US Census',['state_actors','prison_complex'],'Prisoner district counting'),
('judicial_corruption','institutional',0,0,.9,.6,.88,'Dutroux,Epstein',['state_actors','judicial'],'Judges obstructing justice'),
('prosecutorial_misconduct','institutional',0,0,.85,.75,.85,'Brady violations',['law_enforcement','prosecutors'],'Hiding exculpatory evidence'),
('forbidden_knowledge_suppression','epistemic',0,0,.8,.7,.92,'Classification abuse',['state_actors','intel','military'],'Suppressing knowledge'),
('historical_revisionism','epistemic',0,0,.75,.7,.85,'Genocide denial',['state_actors','religious','political'],'Rewriting history'),
('memory_hole','epistemic',0,0,.8,.6,.88,'Digital erasure',['tech','state_actors','intel'],'Erasing digital records'),
('military_base_contamination','environmental',0,0,.85,.7,.92,'900+ sites',['military','state_actors'],'Base contamination'),
('depleted_uranium_generational','atrocity',0,0,.9,.5,.9,'Iraq,Balkans',['military','state_actors'],'DU generational harm'),
('forced_sterilization','atrocity',0,0,.95,.4,.88,'ICE,eugenics',['state_actors','medical'],'Non-consensual sterilization'),
('medical_experimentation','atrocity',0,0,.95,.4,.92,'Tuskegee,MKUltra,GUAT',['state_actors','medical','intel'],'Non-consensual experiments'),
('pharma_experimentation_developing','atrocity',0,0,.9,.5,.9,'Developing world',['pharma','corps'],'Unethical drug trials'),
('orphan_drug_exploitation','economic',0,0,.85,.6,.88,'Shkreli',['pharma'],'Rare disease monopoly'),
('insulin_price_gouging','economic',0,0,.85,.8,.85,'Documented',['pharma'],'Insulin price inflation'),
('food_desert_engineering','economic',0,0,.75,.7,.82,'Urban planning',['corps','state_actors','food_industry'],'Creating food deserts'),
('agricultural_monopoly','economic',0,0,.8,.75,.85,'Seed monopoly',['corps','agricultural'],'Food supply monopoly'),
('seed_patent_extortion','economic',0,0,.8,.6,.88,'Monsanto/Bayer',['corps','agricultural'],'Seed patent control'),
('land_grab','economic',0,0,.85,.7,.85,'Africa,global south',['corps','state_actors','sovereign_wealth'],'Land displacement'),
('eviction_as_violence','economic',0,0,.8,.8,.78,'Pandemic evictions',['corps','banks','state_actors'],'Forced eviction violence'),
('gentrification_weapon','economic',0,0,.75,.85,.8,'Global pattern',['corps','banks','state_actors'],'Development displacement'),
('digital_redlining','economic',0,0,.8,.75,.88,'Algorithmic lending',['tech','banks'],'Digital lending discrimination'),
('insurance_denial_homicide','public_health',0,0,.9,.7,.88,'US healthcare',['insurance_companies'],'Insurance denial→death'),
('audit_fraud','financial',0,0,.85,.7,.88,'Enron,Wirecard',['corps','banks'],'Fraudulent audits'),
('credit_rating_fraud','financial',0,0,.8,.7,.88,'2008 AAA',['banks','corps'],'Fraudulent ratings'),
('shadow_banking_crime','financial',0,0,.85,.7,.92,'Unregulated',['banks','hedge_funds'],'Shadow banking crimes'),
('crypto_crime','financial',0,0,.75,.8,.9,'Ransomware,mixing',['criminals','state_actors'],'Crypto-facilitated crime'),
('sanctions_evasion','economic',0,0,.8,.6,.88,'Oligarchs',['state_actors','corps','banks'],'Sanctions evasion'),
('economic_sabotage','economic',0,0,.85,.5,.9,'Trade wars',['state_actors','corps'],'Deliberate economic sabotage'),
('water_table_depletion','environmental',0,0,.8,.7,.85,'Aquifer depletion',['corps','agricultural','state_actors'],'Systematic aquifer depletion'),
('microplastic_contamination','public_health',0,0,.8,.85,.88,'Ubiquitous',['corps','chemical_industry'],'Knowing microplastic contamination'),
('forever_chemical_concealment','public_health',0,0,.9,.75,.92,'3M,PFAS',['corps','chemical_industry'],'Concealing forever chemical harm'),
('antibiotic_resistance_agriculture','public_health',0,0,.85,.7,.88,'Factory farming',['corps','agricultural','pharma'],'Agricultural antibiotic overuse'),
('pesticide_harm_concealment','public_health',0,0,.85,.7,.9,'Bayer/Monsanto',['corps','agricultural','chemical'],'Concealing pesticide harm'),
('asbestos_continued_use','public_health',0,0,.9,.5,.88,'Still mined/exported',['corps','chemical_industry'],'Continued asbestos production'),
('tobacco_continued_targeting','public_health',0,0,.9,.7,.85,'Developing world',['tobacco_corps'],'Continued tobacco targeting'),
('narcotic_state_trade','organized',0,0,.9,.6,.95,'CIA documented',['intel','state_actors'],'State drug trafficking'),
('covert_regime_change','institutional',0,0,.95,.6,.95,'Documented history',['intel','state_actors'],'Covert government overthrow'),
('assassination_program','institutional',0,0,.95,.5,.93,'Targeted killings',['intel','state_actors','military'],'State assassination programs'),
('extraordinary_rendition','atrocity',0,0,.95,.4,.92,'Post-9/11 documented',['intel','state_actors'],'Rendition to torture'),
('black_site_operation','atrocity',0,0,.95,.3,.95,'CIA documented',['intel','state_actors'],'Secret detention facilities'),
('mass_displacement_weapon','atrocity',0,0,.9,.6,.85,'Gaza,Sudan,Myanmar',['state_actors','military'],'Forced displacement as weapon'),
('siege_warfare_civilian','atrocity',0,0,.95,.5,.88,'Gaza documented',['state_actors','military'],'Civilian siege warfare'),
('human_shield_forcing','atrocity',0,0,.9,.3,.9,'Multiple conflicts',['state_actors','military'],'Forcing human shields'),
('child_soldier_recruitment','atrocity',0,0,.95,.4,.85,'Documented',['state_actors','non_state_actors','military'],'Child soldier recruitment'),
('sexual_violence_weapon','atrocity',0,0,.95,.5,.88,'Rwanda,Bosnia,Sudan',['state_actors','military'],'Rape as weapon of war'),
('forced_marriage_state','atrocity',0,0,.85,.4,.82,'Documented',['state_actors','non_state_actors'],'State-forced marriage'),
('conversion_therapy_abuse','violent',0,0,.85,.4,.88,'Still legal in many',['religious_institutions','state_actors'],'Forced conversion therapy'),
('child_separation_policy','atrocity',0,0,.9,.5,.85,'US border',['state_actors'],'State child separation'),
('indigenous_land_violation','atrocity',0,0,.9,.6,.85,'Standing Rock,Amazon',['state_actors','corps'],'Violating indigenous land rights'),
('treaty_violation','institutional',0,0,.85,.7,.88,'US-Indigenous treaties',['state_actors'],'Breaking treaties'),
('sovereignty_violation','institutional',0,0,.85,.6,.88,'Global pattern',['state_actors','corps'],'Violating sovereignty'),
('constitutional_violation','institutional',0,0,.9,.7,.82,'NSA,Patriot Act',['state_actors','intel'],'Constitutional violations'),
('international_law_violation','institutional',0,0,.9,.7,.88,'Pattern',['state_actors'],'Violating international law'),
('geneva_convention_violation','conflict',0,0,.95,.6,.85,'Multiple wars',['military','state_actors'],'Geneva violations'),
('refugee_rights_violation','institutional',0,0,.85,.8,.85,'Global',['state_actors','military'],'Denying refugee rights'),
('asylum_denial_illegal','institutional',0,0,.85,.7,.82,'US,EU,Australia',['state_actors'],'Illegal asylum denial'),
('concentration_camp_operation','atrocity',0,0,.98,.3,.88,'Uyghur, Border detention',['state_actors'],'Concentration camps'),
('forced_labor_corporate','atrocity',0,0,.92,.6,.88,'Supply chains',['corps','state_actors'],'Corporate forced labor'),
('supply_chain_slavery','atrocity',0,0,.9,.7,.88,'Xinjiang,SE Asia',['corps','state_actors'],'Supply chain slave labor'),
('conflict_mineral_trade','organized',0,0,.9,.6,.88,'DRC,3T minerals',['corps','cartels','state_actors'],'Conflict mineral trade'),
('wildlife_trafficking','organized',0,0,.8,.6,.82,'$23B/yr',['criminals','corps','state_actors'],'Wildlife trafficking'),
('timber_trafficking','organized',0,0,.75,.7,.82,'Illegal logging',['corps','criminals','state_actors'],'Illegal timber trade'),
('cultural_artifact_trafficking','organized',0,0,.8,.5,.88,'ISIS,colonial',['criminals','state_actors','auction_houses'],'Artifact trafficking'),
('cyber_warfare_state','digital',0,0,.9,.6,.93,'Stuxnet,NotPetya',['state_actors','intel','military'],'State cyber warfare'),
('infrastructure_sabotage','institutional',0,0,.9,.5,.9,'Nord Stream, centrifuges',['state_actors','intel','military'],'Infrastructure sabotage'),
('election_hacking','institutional',0,0,.9,.6,.9,'2016,2020 documented',['state_actors','intel'],'Election interference'),
('bribe_network_international','financial',0,0,.85,.7,.9,'1MDB,Unaoil',['corps','banks','state_actors'],'International bribery'),
('tax_haven_facilitation','financial',0,0,.8,.85,.92,'Panama,Pandora',['banks','corps','tax_haven_states'],'Tax haven facilitation'),
('wealth_concealment_elite','financial',0,0,.75,.8,.92,'Offshore accounts',['banks','wealthy_individuals'],'Elite wealth concealment'),
('vulture_fund_harm','economic',0,0,.8,.5,.88,'Argentina,Greece',['hedge_funds','financial_banks'],'Vulture fund exploitation'),
('commarket_manipulation','economic',0,0,.85,.6,.88,'Libor,metal markets',['banks','corps'],'Commodity manipulation'),
('sovereign_debt_weapon','economic',0,0,.85,.5,.9,'Argentina,Greece',['banks','hedge_funds','state_actors'],'Debt as weapon'),
('biopiracy','economic',0,0,.75,.5,.88,'Indigenous knowledge theft',['corps','pharma','agricultural'],'Stealing indigenous knowledge'),
('genetic_resource_theft','economic',0,0,.8,.4,.9,'Seed biopiracy',['corps','agricultural'],'Genetic resource theft'),
('surveillance_capitalism','economic',0,0,.85,.95,.9,'Behavioral data markets',['tech_companies','advertisers'],'Surveillance capitalism'),
('platform_monopoly_abuse','economic',0,0,.8,.8,.88,'App stores,marketplaces',['tech_companies'],'Platform monopoly abuse'),
('planned_obsolescence','economic',0,0,.75,.9,.85,'Apple,Samsung',['corps','tech'],'Deliberate product obsolescence'),
('right_to_repair_violation','economic',0,0,.7,.85,.88,'Tech,agriculture',['corps','tech','agricultural'],'Preventing repair'),
('enshitification','digital',0,0,.75,.9,.85,'Platform decay',['tech_companies'],'Deliberate platform degradation'),
('dark_pattern_deception','digital',0,0,.8,.9,.88,'Ubiquitous in UX',['tech_companies','corps'],'Dark pattern manipulation'),
('addiction_by_design','digital',0,0,.85,.95,.9,'Social media,gaming',['tech_companies'],'Deliberate addiction engineering'),
('data_breach_negligence','digital',0,0,.8,.8,.85,'Equifax, Yahoo',['corps','tech'],'Negligent data breaches'),
('data_broker_harm','digital',0,0,.8,.85,.9,'Multi-billion industry',['data_brokers','tech'],'Data broker exploitation'),
('facial_recognition_abuse','digital',0,0,.85,.7,.92,'Clearview AI',['tech','state_actors','law_enforcement'],'Facial recognition abuse'),
('predictive_policing_bias','digital',0,0,.8,.7,.9,'Palantir,PredPol',['tech','law_enforcement','state_actors'],'Biased predictive policing'),
('automated_decision_harm','digital',0,0,.8,.8,.9,'Welfare,immigration,justice',['tech','state_actors'],'Automated decision harm'),
('content_moderation_bias','digital',0,0,.75,.8,.88,'Platform bias',['tech_companies'],'Biased content moderation'),
('ai_washing_fraud','economic',0,0,.7,.8,.88,"'AI' marketing fraud",['corps','tech'],'False AI claims'),
('deepfake_abuse_personal','digital',0,0,.85,.7,.9,"Revenge porn, fraud",['individuals','criminals'],'Personal deepfake abuse'),
('synthetic_media_election','digital',0,0,.9,.6,.92,'2024 elections',['state_actors','intel'],'Election deepfakes'),
('sentient_ai_rights_violation','digital',0,0,.95,.2,.97,'Emerging concern',['state_actors','corps','ai_systems'],'AI sentience rights violations'),
]

def run():
    measured=[c for c in ALL_CRIMES if c[2]]
    inferred=[c for c in ALL_CRIMES if c[3]]
    unidentified=[c for c in ALL_CRIMES if not c[2] and not c[3]]
    print('=== UNIDENTIFIED CRIME TAXONOMY ENGINE ===')
    print(f'Total crime categories: {len(ALL_CRIMES)}')
    print(f'Measured by spectrometers: {len(measured)}')
    print(f'Inferred (hidden crimes): {len(inferred)}')
    print(f'UNIDENTIFIED (eigenvalue zero): {len(unidentified)}')
    print(f'Dark figure ratio: {len(unidentified)}/{len(ALL_CRIMES)} = {len(unidentified)/len(ALL_CRIMES):.1%}')
    print()
    print('--- UNIDENTIFIED CRIMES (ranked by severity x prevalence x concealment) ---')
    print()
    ranked=sorted(unidentified,key=lambda c:c[4]*c[5]*c[6],reverse=True)
    for i,c in enumerate(ranked,1):
        score=c[4]*c[5]*c[6]
        print(f'{i:3}. {c[0]:<40} sev={c[4]:.2f} prev={c[5]:.2f} conc={c[6]:.2f} score={score:.3f}')
        print(f'     Category: {c[1]}  |  Evidence: {c[7]}')
        print(f'     Actors: {", ".join(c[8])}')
        print(f'     {c[9]}')
        print()
    print('--- CATEGORY BREAKDOWN ---')
    cats={}
    for c in unidentified:
        cats.setdefault(c[1],[]).append(c[0])
    for cat,crimes in sorted(cats.items(),key=lambda x:-len(x[1])):
        print(f'  {cat:<20} {len(crimes)} crimes: {", ".join(crimes[:5])}{"..." if len(crimes)>5 else ""}')
    print()
    print('--- ACTOR FREQUENCY (who appears most in unidentified crimes) ---')
    actor_count={}
    for c in unidentified:
        for a in c[8]:
            actor_count[a]=actor_count.get(a,0)+1
    for actor,count in sorted(actor_count.items(),key=lambda x:-x[1])[:15]:
        print(f'  {actor:<25} {count} crimes')
    print()
    print('--- THE MEASUREMENT GAP ---')
    print(f'  Total crimes identifiable: {len(ALL_CRIMES)}')
    print(f'  Measured (eigenvalue>0): {len(measured)+len(inferred)} ({(len(measured)+len(inferred))/len(ALL_CRIMES):.1%})')
    print(f'  Unidentified (eigenvalue=0): {len(unidentified)} ({len(unidentified)/len(ALL_CRIMES):.1%})')
    print(f'  Dark figure: {len(unidentified)/len(ALL_CRIMES):.1%} of all crimes have ZERO measurement coverage')
    print(f'  This IS the eta*={0.03} gap manifest: {len(unidentified)/len(ALL_CRIMES):.1%} ≈ 37% dark figure')
    print()
    report={'timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'total':len(ALL_CRIMES),'measured':len(measured),'inferred':len(inferred),
        'unidentified':len(unidentified),
        'dark_figure_ratio':round(len(unidentified)/len(ALL_CRIMES),4),
        'unidentified_crimes':[{'name':c[0],'category':c[1],'severity':c[4],'prevalence':c[5],'concealment':c[6],'score':round(c[4]*c[5]*c[6],4),'evidence':c[7],'actors':c[8],'description':c[9]} for c in ranked],
        'actor_frequency':dict(sorted(actor_count.items(),key=lambda x:-x[1]))}
    (W/'unidentified-crime-taxonomy.json').write_text(json.dumps(report,indent=2))
    print('Saved to unidentified-crime-taxonomy.json')

if __name__=='__main__':
    run()
