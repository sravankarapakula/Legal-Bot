import json
import os
import random

# We'll generate realistic user queries for each of the main dispute categories
CATEGORIES = {
    "Rental / Tenant Dispute": [
        "My landlord hasn't returned my security deposit despite vacating 2 months ago.",
        "The tenant is not paying rent and refuses to leave the house.",
        "I need to recover my rent deposit of 50000 rupees from my previous owner.",
        "Owner is threatening to evict me without proper notice.",
        "My landlord locked me out of the apartment.",
        "I gave one month notice but owner is keeping the entire security advance.",
        "Tenant has damaged the property and isn't paying for repairs.",
        "I rented a shop but the owner is cutting electricity frequently.",
        "How can I file a case against my landlord for not returning deposit?",
        "Tenant's lease expired but they are still occupying the flat."
    ] * 5,  # Multiply to have more samples

    "Employment Dispute": [
        "My company fired me suddenly without notice pay.",
        "I resigned last month but haven't received my full and final settlement.",
        "My employer is holding back my 3 months salary.",
        "I was illegally terminated due to office politics.",
        "My boss refuses to pay my pending wages.",
        "Company hasn't deposited PF and is avoiding my calls.",
        "I worked overtime but the employer didn't pay any extra money.",
        "They fired me for no reason and refused to clear my dues.",
        "My employer is withholding my original certificates until I pay them.",
        "Is there a legal way to recover my pending salary from a startup?"
    ] * 5,

    "Consumer Dispute": [
        "I bought a defective laptop and the company is refusing replacement.",
        "The washing machine broke down in 10 days and customer care isn't helping.",
        "I paid for a service but didn't receive it, need a refund.",
        "The airline cancelled my flight and won't give the money back.",
        "I ordered shoes online but received a cheap copy, seller ignoring me.",
        "The builder hasn't handed over the flat even after 3 years delay.",
        "Hospital overcharged me for simple treatment.",
        "My gym closed down suddenly and took my yearly membership fee.",
        "I found a bug in the packaged food I bought.",
        "The coaching center refuses to refund fees after I cancelled."
    ] * 5,

    "Financial Dispute": [
        "I lent my friend 2 lakhs and he gave a cheque that bounced.",
        "A business partner's cheque got dishonoured due to insufficient funds.",
        "Someone took a personal loan from me and is absconding.",
        "The cheque I received returned unpaid from the bank.",
        "I need to send a legal notice for a cheque bounce case under section 138.",
        "My client hasn't paid the invoice and their cheque bounced.",
        "How do I recover money from someone who gave me a fake cheque?",
        "The bank memo says funds insufficient for the 50,000 cheque.",
        "I gave a hand loan on a promissory note, now he denies it.",
        "Cheque was returned with reason 'signature differs', what to do?"
    ] * 5,

    "Family Dispute": [
        "I want a mutual consent divorce from my husband.",
        "My wife deserted me 2 years ago, I want to file for divorce.",
        "Husband is committing adultery and I want a separation.",
        "I am facing extreme mental cruelty from my spouse.",
        "Need to claim maintenance from my husband for myself and kids.",
        "My in-laws are demanding dowry and harassing me.",
        "I want alimony after divorcing my abusive husband.",
        "Wife filed a false 498a case, need to file for divorce.",
        "We have been living separately for 5 years and want to end marriage.",
        "Spouse is refusing to grant divorce despite irreconcilable differences."
    ] * 5,

    "Property Dispute": [
        "My neighbour encroached on 5 feet of my land and built a wall.",
        "Someone forged documents and sold my ancestral property illegally.",
        "I have a boundary dispute with the adjacent plot owner.",
        "Local goons are trying to grab my vacant plot in the village.",
        "My relative is trying to establish false possession on my house.",
        "There is an illegal construction blocking my right of way.",
        "A tenant is claiming ownership of the land I leased to them.",
        "I bought land but the seller is refusing to register it.",
        "Want to file an injunction to stop illegal construction next to my house.",
        "My uncle forcefully acquired my agricultural land."
    ] * 5,

    "Motor Accident": [
        "I met with a car accident and suffered heavy injuries, need compensation.",
        "A truck hit my bike and ran away, I have the license plate.",
        "My hospital bills are huge after the road accident due to negligent driving by another car.",
        "Need to file an MACT claim for the death of my relative in a bus accident.",
        "Drunk driver crashed into my auto rickshaw, broke my leg.",
        "Can I claim lost wages after a severe traffic accident?",
        "The other driver's insurance is offering very low settlement for my injuries.",
        "I was hit while crossing the road at the zebra crossing.",
        "Need help filing compensation claim for permanent disability from car crash.",
        "A speeding bike hit me from behind causing spinal injury."
    ] * 5,

    "Criminal / Civil Harassment": [
        "Someone is constantly stalking me and sending threat messages.",
        "My ex is threatening to leak personal photos online.",
        "Local money lender is coming to my house and harassing my family.",
        "Neighbours are throwing garbage intentionally and abusing us daily.",
        "I am receiving daily blank calls and death threats.",
        "Need a restraining order against an abusive former friend.",
        "A group of men follow me from the bus stop every evening.",
        "My relatives are constantly mentally harassing me for property.",
        "Workplace colleague is spreading vicious lies and intimidating me.",
        "An unknown person is repeatedly banging on my door at night."
    ] * 5,

    "Contract Dispute": [
        "The vendor breached our service agreement by not delivering on time.",
        "My business partner violated the non-compete clause.",
        "A supplier took the 5 lakh advance but never sent the materials.",
        "I want to sue for breach of contract because they didn't fulfill the terms.",
        "The IT company failed to deliver the software as per our MoU.",
        "We signed an NDA but the other party leaked confidential info.",
        "Client refuses to pay for the completed project despite the contract.",
        "The contractor abandoned the construction work midway.",
        "Event management company cancelled at the last minute breaking the agreement.",
        "Freelancer took payment but provided plagiarized work."
    ] * 5,

    "Partition Suit": [
        "My brother is not giving me my share in the ancestral house.",
        "I want to divide the joint family agricultural land.",
        "Sisters are demanding their legal share in father's property.",
        "Co-owners are refusing to partition the commercial building we inherited.",
        "Need to file a partition suit in civil court for my 1/3rd share.",
        "Relatives occupy the entire joint property and deny me access.",
        "My uncle sold joint family property without our consent.",
        "I want a separate patta and partition of the family estate.",
        "We can't agree on how to divide the inherited flat, need a court order.",
        "Can a daughter claim partition if the father died before 2005?"
    ] * 5,

    "Succession / Probate": [
        "My father died without a will, need a succession certificate for his bank accounts.",
        "How do I apply for probate of my mother's registered will?",
        "The bank is asking for a legal heir certificate or succession certificate.",
        "Need to transfer shares of deceased husband but company demands probate.",
        "My brother is contesting our father's will, saying it's forged.",
        "How to distribute assets if someone dies intestate?",
        "I am the executor of the will but don't know how to get it probated.",
        "Need succession certificate to claim PF and gratuity of late father.",
        "A distant relative is objecting to the grant of succession certificate.",
        "My aunt nominated me but bank says nomination is not enough, need succession."
    ] * 5,

    "Cybercrime": [
        "Someone hacked my bank account and transferred 50,000 rupees.",
        "I fell for an online job fraud and lost money.",
        "A fake Facebook profile is using my pictures and asking for money.",
        "I got a phishing link via SMS and my credit card was charged.",
        "Someone blackmailing me over video call saying they recorded me.",
        "OTP fraud, the caller pretended to be from bank and stole funds.",
        "I paid for a product on Instagram but the page blocked me.",
        "Someone has hacked my email and is sending spam to clients.",
        "Cryptocurrency scam, lost thousands in a fake investment portal.",
        "How to file complaint with cyber cell for online harassment?"
    ] * 5,

    "Child Custody": [
        "I want full custody of my 5 year old daughter after divorce.",
        "My wife took our son and moved to another state without my permission.",
        "Seeking visitation rights to see my kids every weekend.",
        "Husband is an alcoholic, I want sole custody of children.",
        "Need guardianship certificate for my minor nephew.",
        "The mother is denying me access to our child even after court orders.",
        "I want joint custody so we share parenting responsibilities.",
        "Can I get custody of my child if I earn less than my husband?",
        "Father is not paying child support, how to seek sole custody.",
        "I fear my ex will kidnap the children during visitation."
    ] * 5,

    "Insurance Dispute": [
        "Health insurance rejected my claim citing pre-existing disease unfairly.",
        "Car insurance company is offering half the repair cost after accident.",
        "Life insurance claim denied because they say I hid medical history.",
        "My shop caught fire but the surveyor rejected the insurance claim.",
        "Insurance company is delaying the settlement for over 6 months.",
        "They cancelled my policy without any prior notice.",
        "TPA is refusing cashless authorization despite valid health cover.",
        "Crop insurance claim not paid by the company after drought.",
        "How to complain to Insurance Ombudsman about wrongful claim rejection?",
        "The sum insured was randomly reduced by the company at renewal."
    ] * 5,

    "Defamation Suit": [
        "A newspaper printed a false article ruining my business reputation.",
        "My ex-business partner is spreading malicious lies about me on WhatsApp.",
        "Someone posted fake negative reviews on Google to destroy my restaurant.",
        "A politician gave a speech making baseless allegations against me.",
        "Colleague sent a mass email with false claims about my character.",
        "I want to sue a YouTuber for making a defamatory video about my brand.",
        "Need to send a legal notice for slander and demand an apology.",
        "A rival company published an ad that directly mocks our trademark unfairly.",
        "Someone is spreading rumors in the society WhatsApp group calling me a thief.",
        "Can I claim damages for mental agony caused by character assassination?"
    ] * 5,

    "Public Interest Litigation": [
        "A factory is dumping toxic waste into the village river, need to file PIL.",
        "Want to challenge a government order that harms the local environment.",
        "PIL to stop illegal tree cutting in the city forest area.",
        "The municipality is not maintaining roads causing daily accidents.",
        "Found major corruption in public mid-day meal scheme, want court intervention.",
        "Filing a PIL for proper disabled access in all public buildings.",
        "The historical monument is being encroached upon by local mafia.",
        "Government hospital has no beds and turning away critical patients, need PIL.",
        "Challenging the unconstitutional rule passed by the state legislature.",
        "PIL seeking strict enforcement of noise pollution norms during festivals."
    ] * 5,

    "Government Service Dispute": [
        "I was wrongly denied promotion in my government department despite seniority.",
        "Challenging my arbitrary transfer order which violates the transfer policy.",
        "My pension has been stopped without any disciplinary action pending.",
        "Received a suspension order without being given a chance to explain.",
        "Government refuses to regularize my services after 10 years of contract work.",
        "Need to file an OA in CAT regarding wrong pay fixation.",
        "The disciplinary committee passed a removal order based on a bogus report.",
        "I want to claim my withheld retirement benefits from the state government.",
        "My juniors were promoted but my name was skipped in the DPC list.",
        "Tribunal case for compassionate appointment rejected arbitrarily."
    ] * 5,

    "Tax Dispute": [
        "Income tax department sent a demand notice for 5 lakhs with an erroneous calculation.",
        "GST registration got cancelled without a proper show cause notice.",
        "I want to file an appeal before CIT against the assessing officer's order.",
        "Customs department seized my goods and levied unfair penalty.",
        "Tax authority is not processing my refund for the last 3 assessment years.",
        "My GST input tax credit was disallowed wrongly by the auditor.",
        "Need to challenge the re-assessment order under section 147.",
        "Notice received for unexplained cash deposits but I have all proofs.",
        "Appeal before ITAT regarding disallowance of legitimate business expenses.",
        "The GST officer attached my bank account illegally without prior intimation."
    ] * 5,
}

# Also generate some random generic variations for "General Civil Dispute"
CATEGORIES["General Civil Dispute"] = [
    "I have a legal issue and need help.",
    "Someone cheated me and I want to go to court.",
    "I have a civil dispute requiring legal action.",
    "Need to file a case in the civil court for my rights.",
    "Looking for legal guidance on a miscellaneous issue.",
    "I want to send a legal notice to someone for causing me harm.",
    "How do I start a lawsuit against a person?",
    "I need a lawyer to fight my civil case.",
    "Can you tell me the procedure to file a general complaint?",
    "Seeking justice for a civil wrong done to me."
] * 5

def generate():
    dataset = []
    
    # Simple templates to combine text slightly
    prefixes = [
        "Help, ", "I have a problem: ", "Legal advice needed: ", 
        "My situation: ", "", "", "Please guide me: "
    ]
    suffixes = [
        "", " What should I do?", " Need legal help.", " Can I sue?",
        " What is the process to file a case?", ""
    ]

    for label, texts in CATEGORIES.items():
        for text in texts:
            # We add a little randomness to make the model robust
            pref = random.choice(prefixes)
            suff = random.choice(suffixes)
            final_text = f"{pref}{text}{suff}".strip()
            
            # Label index creation (we map labels to integers later in the training script)
            dataset.append({
                "text": final_text,
                "label": label
            })
    
    # Shuffle the dataset
    random.shuffle(dataset)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "synthetic_dataset.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Generated {len(dataset)} synthetic training examples at {output_path}")

if __name__ == "__main__":
    generate()
