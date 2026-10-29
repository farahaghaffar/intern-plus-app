"""Builds assessment/bank_v3.json: two levels (1 = undergraduate, 2 = final year and graduates),
field-specific wording for some questions, and an explanation for every answer.
Options are listed best first; the second value is the points (0 to 3), the third is the note shown in the review.
Field wording never changes the options' meaning or the correct answer, so scores stay comparable.
Fields: biz (default), tech, media, health, social."""
import json

FIELDS = {
    'biz': 'Business & Economics, and other fields',
    'tech': 'Computing, Engineering and Sciences',
    'media': 'Media, Communication, Design & Arts',
    'health': 'Health & Life Sciences',
    'social': 'Law, Politics & Humanities',
}

items = []
def mcq(id, level, cat, q, o, why, qf=None, of=None):
    it = {'id': id, 'level': level, 'cat': cat, 'q': q, 'o': o, 'why': why}
    if qf: it['qf'] = qf
    if of: it['of'] = of
    items.append(it)
def num(id, level, cat, q, answer, tol, why, qf=None):
    it = {'id': id, 'level': level, 'cat': cat, 'q': q, 'num': True, 'answer': answer, 'tol': tol, 'why': why}
    if qf: it['qf'] = qf
    items.append(it)

# ======================= LEVEL 2: final year, graduates, working =======================
mcq('cm1', 2, 'comm',
    'It is 9 pm. Your manager messages on WhatsApp asking for the sales report by 10 am tomorrow. You know it will realistically take until noon. What do you do?',
    [['Reply now: "I can send the key numbers by 10 and the full version by 12. Does that work, or is there one part you need first?"', 3, 'Best. You flag the problem early, offer what you can deliver, and let your manager choose.'],
     ['Stay up late and finish it by 10 without mentioning the time it took', 2, 'You deliver, but you hide a real constraint and set an expectation you cannot keep every time.'],
     ['Reply first thing in the morning to say it will be ready by noon', 1, 'Honest, but too late: your manager has no time left to plan around the delay.'],
     ['Reply "Sure, no problem" and send it at noon', 0, 'Agreeing to a deadline you know you will miss damages trust more than the delay itself.']],
    'Good workplace communication means raising a problem as soon as you see it, with a solution, not after the deadline has passed.',
    qf={'tech': 'It is 9 pm. Your manager messages on Slack asking for the test results for the new feature by 10 am tomorrow. You know it will realistically take until noon. What do you do?',
        'media': 'It is 9 pm. Your manager messages on WhatsApp asking for the campaign content plan by 10 am tomorrow. You know it will realistically take until noon. What do you do?',
        'health': 'It is 9 pm. Your supervisor messages on WhatsApp asking for the patient survey summary by 10 am tomorrow. You know it will realistically take until noon. What do you do?',
        'social': 'It is 9 pm. Your manager messages on WhatsApp asking for the research summary by 10 am tomorrow. You know it will realistically take until noon. What do you do?'})
mcq('cm2', 2, 'comm',
    'A client emails angrily because their order is three days late. The delay was the courier\'s fault. Which reply is best?',
    [['Apologise, give a clear new date and what you have done to fix it, and offer a goodwill gesture if your policy allows', 3, 'Best. It acknowledges the problem, gives certainty about what happens next, and repairs the relationship.'],
     ['Apologise sincerely and promise it will not happen again', 2, 'A good start, but the client still does not know when the problem will be solved.'],
     ['Explain politely that someone else caused the delay and it was outside your control', 1, 'It may be true, but to the client it sounds like an excuse. They care about the fix, not the blame.'],
     ['Forward it to your manager because the client is upset', 0, 'Escalating before trying to help makes you look unable to handle normal problems.']],
    'An upset customer needs three things: to feel heard, to know what happens next and when, and to see that you have taken action.',
    qf={'tech': 'A customer emails angrily because your company\'s app has been down for three hours. The outage was caused by your cloud provider. Which reply is best?',
        'media': 'A client of your agency emails angrily because their campaign went live three days late. The delay was caused by the printing supplier. Which reply is best?',
        'health': 'A patient\'s family member emails angrily because test results are three days late. The delay was caused by the external lab. Which reply is best?',
        'social': 'A member of the public emails angrily because their request is three days late. The delay was caused by another department. Which reply is best?'})
mcq('cm3', 2, 'comm',
    'You are presenting to senior managers. One interrupts with a question you planned to answer on slide 8 of 10. What do you do?',
    [['Answer it in one or two sentences now, then say you will show the detail on slide 8', 3, 'Best. Senior people want the answer now; you respect that and keep your structure.'],
     ['Say "Great question, I\'ll come to that shortly" and continue', 2, 'Polite, but it can feel like you are avoiding the question.'],
     ['Skip ahead to slide 8 straight away', 1, 'You answer, but you lose the flow and the slides in between.'],
     ['Ask everyone to hold questions until the end', 0, 'With senior managers this comes across as inflexible.']],
    'When presenting, adapt to your audience. A short direct answer, then back to your plan, shows confidence and control.')
mcq('cm4', 2, 'comm',
    'You are messaging a hiring manager you have never met on LinkedIn. Which opening is strongest?',
    [['"Hi Ahmed, I saw your team is hiring growth interns. I grew our student club\'s Instagram from 2k to 9k followers in six months. Could I have 10 minutes of your time?"', 3, 'Best. It is personal, shows proof of a result, and makes a small, clear request.'],
     ['"Hi Ahmed, I\'m a marketing student at Cairo University and I\'m very interested in your growth team."', 2, 'Polite and personal, but it gives no reason to reply and no clear ask.'],
     ['"Hi Ahmed, could you refer me to the growth internship?"', 1, 'Asking a stranger for a referral before showing any value rarely works.'],
     ['"Hello sir, I am a hardworking and passionate student looking for any opportunity."', 0, 'Generic words like "hardworking" and "any opportunity" make you sound like everyone else.']],
    'Strong outreach is specific: who you are, one concrete result, and one small request. Results beat adjectives.',
    of={'tech': ['"Hi Ahmed, I saw your team is hiring backend interns. I built a timetable app that 1,200 students at my university use every week. Could I have 10 minutes of your time?"',
                 '"Hi Ahmed, I\'m a computer science student at Cairo University and I\'m very interested in your engineering team."',
                 '"Hi Ahmed, could you refer me to the backend internship?"',
                 '"Hello sir, I am a hardworking and passionate student looking for any opportunity."'],
        'media': ['"Hi Ahmed, I saw your agency is hiring content interns. I produced a video series for our student union that reached 150k views. Could I have 10 minutes of your time?"',
                  '"Hi Ahmed, I\'m a mass communication student at Cairo University and I\'m very interested in your agency."',
                  '"Hi Ahmed, could you refer me to the content internship?"',
                  '"Hello sir, I am a hardworking and passionate student looking for any opportunity."'],
        'health': ['"Hi Dr Ahmed, I saw your hospital is hiring quality interns. I ran a patient survey for 300 people during my training and presented the results to the department. Could I have 10 minutes of your time?"',
                   '"Hi Dr Ahmed, I\'m a pharmacy student at Cairo University and I\'m very interested in your hospital."',
                   '"Hi Dr Ahmed, could you refer me to the quality internship?"',
                   '"Hello sir, I am a hardworking and passionate student looking for any opportunity."'],
        'social': ['"Hi Ahmed, I saw your organisation is hiring research interns. I led a survey of 400 students on public transport that our faculty published. Could I have 10 minutes of your time?"',
                   '"Hi Ahmed, I\'m a political science student at Cairo University and I\'m very interested in your organisation."',
                   '"Hi Ahmed, could you refer me to the research internship?"',
                   '"Hello sir, I am a hardworking and passionate student looking for any opportunity."']})
mcq('cm5', 2, 'comm',
    'A teammate on a shared project has missed two deadlines, and it is now delaying your part. What is your first move?',
    [['Talk to them privately, ask what is blocking them, and agree a smaller next deadline together', 3, 'Best. You find the real cause and fix it directly, without embarrassing anyone.'],
     ['Tell your manager, with dates and the impact on your work', 2, 'Reasonable if talking to them fails, but as a first step it skips a simple conversation.'],
     ['Quietly do their part yourself so the project stays on track', 1, 'It solves today\'s problem but hides it, and you cannot keep doing two jobs.'],
     ['Mention it in the team group chat so everyone is aware', 0, 'Calling someone out in public damages the relationship and rarely fixes the cause.']],
    'Start with a direct, private conversation focused on solving the problem. Escalate only if that does not work.')
mcq('cm6', 2, 'comm',
    'An email says: "We will move the launch to the 14th only if the supplier confirms the new packaging by Thursday. Otherwise we keep the 10th and launch with the current packaging." The supplier does not confirm by Thursday. What happens?',
    [['The launch stays on the 10th with the current packaging', 3, 'Correct. No confirmation means the "otherwise" plan applies.'],
     ['The launch moves to the 14th with the current packaging', 0, 'The move to the 14th only happens if the supplier confirms, which they did not.'],
     ['The launch stays on the 10th with the new packaging', 0, 'The new packaging was never confirmed, so it cannot be used.'],
     ['The launch is postponed until the supplier confirms', 0, 'The email gives a clear fallback, so nothing is postponed.']],
    'Read conditions carefully: "only if X, otherwise Y" means Y happens whenever X does not.')

num('pb1', 2, 'prob',
    'Last week an online store had 2,400 visitors and 60 orders. This week visitors went up by 25% and the conversion rate (orders divided by visitors) stayed the same. How many orders did the store get this week?',
    75, 0, 'Conversion rate = 60 / 2,400 = 2.5%. Visitors this week = 2,400 x 1.25 = 3,000. Orders = 3,000 x 2.5% = 75. Shortcut: if the rate stays the same, orders also grow by 25%, so 60 x 1.25 = 75.',
    qf={'tech': 'Last week an app had 2,400 new downloads and 60 paid sign-ups. This week downloads went up by 25% and the sign-up rate (sign-ups divided by downloads) stayed the same. How many paid sign-ups were there this week?',
        'media': 'Last week a campaign landing page had 2,400 visitors and 60 sign-ups. This week visitors went up by 25% and the sign-up rate (sign-ups divided by visitors) stayed the same. How many sign-ups were there this week?',
        'health': 'Last week a clinic\'s booking page had 2,400 visitors and 60 bookings. This week visitors went up by 25% and the booking rate (bookings divided by visitors) stayed the same. How many bookings were there this week?',
        'social': 'Last week a petition page had 2,400 visitors and 60 signatures. This week visitors went up by 25% and the signing rate (signatures divided by visitors) stayed the same. How many signatures were there this week?'})
num('pb2', 2, 'prob',
    'A product costs EGP 400 to make and sells for EGP 650. Delivery costs EGP 50 per order. What is the profit as a percentage of the selling price? Round to the nearest whole number.',
    31, 1, 'Profit = 650 - 400 - 50 = EGP 200. As a share of the selling price: 200 / 650 = 0.308, so about 31%. A common mistake is forgetting delivery (250 / 650 = 38%) or dividing by cost instead of price.')
mcq('pb3', 2, 'prob',
    'Monthly sales fell by 30%. Website visitors and the number of orders stayed about the same. What is the most likely explanation?',
    [['Each order is worth less, for example because of discounts or cheaper products', 3, 'Correct. Sales = orders x value per order. Orders did not change, so value per order must have dropped.'],
     ['Demand dropped because of the season', 1, 'Lower demand would show up as fewer visitors or orders, which did not happen.'],
     ['Fewer people visited', 0, 'The question says visitors stayed the same.'],
     ['The checkout stopped working', 0, 'Then the number of orders would have fallen, but it stayed the same.']],
    'Break a number into its parts. Revenue = number of orders x average value per order. If one part is unchanged, the other must explain the change.',
    qf={'tech': 'Monthly revenue from your company\'s app fell by 30%. Active users and the number of purchases stayed about the same. What is the most likely explanation?',
        'media': 'Monthly revenue from an online design shop fell by 30%. Visitors and the number of orders stayed about the same. What is the most likely explanation?',
        'health': 'A pharmacy\'s monthly sales fell by 30%. The number of customers and orders stayed about the same. What is the most likely explanation?',
        'social': 'A university bookshop\'s monthly sales fell by 30%. The number of customers and purchases stayed about the same. What is the most likely explanation?'})
mcq('pb4', 2, 'prob',
    'Your to-do list: (A) fix an error for a major client, due 3 pm today; (B) the weekly report your manager reads on Monday; (C) a colleague asked for 30 minutes of help today; (D) tidy your inbox. Which order is best?',
    [['A, C, B, D', 3, 'Best. Urgent and important first, then the short task that unblocks a colleague today, then the Monday report.'],
     ['A, B, C, D', 2, 'Close, but the report is not due until Monday while your colleague needs help today.'],
     ['C, A, B, D', 1, 'Helping first risks the client deadline at 3 pm.'],
     ['B, A, C, D', 0, 'Starting with Monday\'s report puts today\'s client deadline at risk.']],
    'Order by deadline and impact: what is due soonest and matters most comes first; low-value tasks come last.')
mcq('pb5', 2, 'prob',
    'All interns at Company X speak English. Mona speaks English. Which statement must be true?',
    [['Mona may or may not be an intern at Company X', 3, 'Correct. Speaking English does not make someone an intern; many people speak English.'],
     ['Mona is an intern at Company X', 0, 'This reverses the rule. "All interns speak English" does not mean "all English speakers are interns".'],
     ['Mona is not an intern at Company X', 0, 'Nothing rules her out either.'],
     ['Everyone who speaks English works at Company X', 0, 'The statement says nothing about everyone who speaks English.']],
    '"All A are B" does not mean "all B are A". Be careful not to reverse a rule.')
mcq('pb6', 2, 'prob',
    'Your manager says "make the pitch deck better" before tomorrow\'s investor meeting. What do you do first?',
    [['Ask who will be in the room and what decision the meeting needs to reach', 3, 'Best. "Better" depends on the audience and the goal, so clarify those first.'],
     ['Ask a colleague which slides feel weakest, then fix those', 2, 'Useful input, but you still do not know what the investors need.'],
     ['Redesign the slides so they look more modern', 1, 'Looks matter less than whether the deck answers the investors\' questions.'],
     ['Add as much supporting data as possible to every slide', 0, 'More data usually makes a deck harder to follow, not better.']],
    'When a request is vague, define the goal before you start. Ten minutes of questions saves hours of the wrong work.')

mcq('pr1', 2, 'prof',
    'In your first week, you notice a team process that seems slow and inefficient. What do you do?',
    [['Learn why it is done that way, then suggest an improvement with a small example', 3, 'Best. You respect the team\'s context and still bring a fresh idea.'],
     ['Suggest a better way in the next team meeting', 2, 'Good initiative, but without the context there may be a reason you have missed.'],
     ['Wait a few months until you understand the company before saying anything', 1, 'Safe, but you lose the fresh view that new people bring.'],
     ['Start doing it your own way without telling anyone', 0, 'This can break things for others and damages trust.']],
    'Understand first, then improve. New people add value by asking "why" before "why not".')
mcq('pr2', 2, 'prof',
    'You realise a number you gave your manager yesterday was wrong, and it has already gone to a client. What do you do?',
    [['Tell your manager right away with the correct number and a draft correction for the client', 3, 'Best. Owning it fast, with a fix ready, limits the damage and builds trust.'],
     ['Recheck all your other numbers first, then tell your manager tomorrow', 2, 'Checking is good, but a day\'s delay lets the client act on a wrong number.'],
     ['Correct it in next month\'s report', 1, 'Too late, and it looks like you hoped nobody would notice.'],
     ['Leave it, since the difference is small', 0, 'Small errors that are hidden become big trust problems when found.']],
    'Mistakes are normal. What employers judge is how fast and how honestly you fix them.')
mcq('pr3', 2, 'prof',
    'Your manager says your work is good but you take too long. What is your best response?',
    [['Ask which tasks took too long and what time is reasonable, then check in again after two weeks', 3, 'Best. You turn vague feedback into a clear target and show you are acting on it.'],
     ['Work extra hours so you finish faster', 2, 'It shows effort, but it does not fix how you work.'],
     ['Explain that you take time because you care about quality', 1, 'This sounds defensive and does not address the feedback.'],
     ['Carry on as before, since the quality is good', 0, 'Ignoring feedback is one of the fastest ways to lose a manager\'s trust.']],
    'Treat feedback as information. Ask for specifics, agree a target, and follow up.')
mcq('pr4', 2, 'prof',
    'You are working remotely and finish your tasks early on Thursday afternoon. What do you do?',
    [['Tell your manager you are done and suggest one or two useful things you could pick up', 3, 'Best. You are visible, proactive and still aligned with your manager\'s priorities.'],
     ['Start a project you think would help, and tell your manager about it on Sunday', 2, 'Good initiative, but you may be working on the wrong thing.'],
     ['Wait until someone gives you a new task', 1, 'Not wrong, but it wastes time and makes you look passive.'],
     ['Log off early, since the work is done', 0, 'In remote work, disappearing without a word looks like you are not working.']],
    'Proactive and visible beats busy and invisible, especially when working remotely.')
mcq('pr5', 2, 'prof',
    'A friend who works at a competitor asks when your company is launching its new product. What do you do?',
    [['Say politely that you cannot share internal plans', 3, 'Best. Clear and friendly, and it protects your company.'],
     ['Check with your manager whether it is OK to share', 2, 'Careful, but launch dates for a competitor are almost always confidential.'],
     ['Give a vague hint without a date', 1, 'Even hints can leak useful information.'],
     ['Tell them, since it will be public soon anyway', 0, 'Until it is public, it is confidential. Sharing it can cost you your job.']],
    'Confidentiality is part of professionalism. When in doubt, do not share.')
mcq('pr6', 2, 'prof',
    'In an interview you are asked: "What is your biggest weakness?" Which answer is strongest?',
    [['A real, specific weakness, plus what you are doing about it and an example of progress', 3, 'Best. It shows self-awareness and that you act on it.'],
     ['A real, specific weakness, explained honestly', 2, 'Honest, but without the improvement part it leaves the interviewer worried.'],
     ['"I\'m a perfectionist, so I sometimes work too hard."', 1, 'Interviewers hear this every day and see it as avoiding the question.'],
     ['"I don\'t really have any major weaknesses."', 0, 'Everyone has weaknesses; this suggests low self-awareness.']],
    'Interviewers ask this to test self-awareness. Name a real weakness, then show what you are doing about it.')

mcq('dg1', 2, 'digi',
    'Order values are in cells B2 to B500. Which formula counts the orders above EGP 1,000?',
    [['=COUNTIF(B2:B500,">1000")', 3, 'Correct. COUNTIF counts the cells that meet a condition.'],
     ['=IF(B2:B500>1000,1,0)', 1, 'IF checks one value at a time; on its own it does not give a count.'],
     ['=SUMIF(B2:B500,">1000")', 0, 'SUMIF adds up the values instead of counting them.'],
     ['=COUNT(B2:B500>1000)', 0, 'COUNT does not take a condition like this.']],
    'COUNTIF counts, SUMIF adds up, AVERAGEIF averages: each one only uses the cells that meet your condition.')
mcq('dg2', 2, 'digi',
    'You want an AI tool like ChatGPT or Claude to draft a cold email. Which prompt will give the best result?',
    [['"Write a 100-word cold email to the HR manager of a Cairo fintech, introducing me as a final-year business student who built a budgeting tool, asking for a 15-minute call. Friendly but professional."', 3, 'Best. It gives the audience, who you are, one result, the goal, the length and the tone.'],
     ['"Write a professional cold email to an HR manager asking for an internship."', 2, 'Clear goal, but the AI has to invent everything about you.'],
     ['"Write a cold email."', 1, 'Too vague: you will get a generic template.'],
     ['"Make my email good."', 0, 'The AI has no idea what "good" means for you.']],
    'Good prompts give context: who it is for, who you are, the goal, and the format. The more specific, the more useful the result.',
    of={'tech': ['"Write a 100-word cold email to the engineering manager of a Cairo software company, introducing me as a final-year computer science student who built a timetable app, asking for a 15-minute call. Friendly but professional."',
                 '"Write a professional cold email to an engineering manager asking for an internship."', '"Write a cold email."', '"Make my email good."'],
        'media': ['"Write a 100-word cold email to the creative director of a Cairo agency, introducing me as a final-year media student who produced a 150k-view video series, asking for a 15-minute call. Friendly but professional."',
                  '"Write a professional cold email to a creative director asking for an internship."', '"Write a cold email."', '"Make my email good."'],
        'health': ['"Write a 100-word cold email to the quality manager of a Cairo hospital, introducing me as a final-year pharmacy student who ran a 300-patient survey, asking for a 15-minute call. Friendly but professional."',
                   '"Write a professional cold email to a hospital manager asking for an internship."', '"Write a cold email."', '"Make my email good."'],
        'social': ['"Write a 100-word cold email to the programme manager of an NGO in Cairo, introducing me as a final-year political science student who led a 400-person survey, asking for a 15-minute call. Friendly but professional."',
                   '"Write a professional cold email to an NGO manager asking for an internship."', '"Write a cold email."', '"Make my email good."']})
mcq('dg3', 2, 'digi',
    'An AI tool gives you a market size figure for Egypt with no source. You need it for a client slide. What do you do?',
    [['Find the figure in a credible source, such as an official report, and cite that source', 3, 'Best. AI tools can state wrong numbers confidently; a client slide needs a real source.'],
     ['Use it, clearly labelled as an AI estimate', 2, 'Honest, but clients expect verified numbers.'],
     ['Ask the AI for its source and use the figure if it names one', 1, 'AI tools sometimes invent sources too. You still need to open and check it.'],
     ['Use it as it is, since AI tools are usually right', 0, 'An unverified number in front of a client is a real risk.']],
    'Use AI to speed up research, but verify facts and numbers in a source you can name.',
    qf={'tech': 'An AI tool tells you how many people in Egypt use mobile banking, with no source. You need it for a product proposal. What do you do?',
        'media': 'An AI tool gives you the number of Instagram users in Egypt, with no source. You need it for a client pitch. What do you do?',
        'health': 'An AI tool gives you how common diabetes is in Egypt, with no source. You need it for a hospital presentation. What do you do?',
        'social': 'An AI tool gives you Egypt\'s youth unemployment rate, with no source. You need it for a policy brief. What do you do?'})
num('dg4', 2, 'digi',
    'Revenue was EGP 120,000 in January, EGP 90,000 in February and EGP 135,000 in March. By what percentage did revenue grow from February to March?',
    50, 0, 'Growth = (March - February) / February = (135,000 - 90,000) / 90,000 = 45,000 / 90,000 = 50%. The trap is comparing with January instead of February.')
mcq('dg5', 2, 'digi',
    'A client asks for a spreadsheet that includes your customers\' names and phone numbers. They only need sales totals by city. What do you do?',
    [['Share a version with only the totals by city, with access limited to the client', 3, 'Best. Share only what is needed, and only with the person who needs it.'],
     ['Share the full file as view-only with the client\'s email address', 2, 'Access is limited, but you still share personal data they do not need.'],
     ['Share the full file using "anyone with the link" so it is easy to open', 1, 'Anyone who gets the link can see your customers\' personal data.'],
     ['Email the full file as an attachment', 0, 'Once sent, you lose all control over who sees the personal data.']],
    'Protect personal data: share the minimum needed, with the fewest people, and keep control of access.',
    qf={'tech': 'A partner company asks for a spreadsheet that includes your app users\' names and phone numbers. They only need sign-ups by city. What do you do?',
        'health': 'A supplier asks for a spreadsheet that includes your patients\' names and phone numbers. They only need prescription totals by city. What do you do?',
        'social': 'A partner organisation asks for a spreadsheet that includes survey respondents\' names and phone numbers. They only need results by city. What do you do?'})
mcq('dg6', 2, 'digi',
    'Prices are in cells C2 to C101, and a few cells are empty. Which formula gives the correct average price?',
    [['=AVERAGE(C2:C101)', 3, 'Correct. AVERAGE skips empty cells, so it divides only by the prices that exist.'],
     ['=SUM(C2:C101)/100', 1, 'Dividing by 100 counts the empty cells too, so the average comes out too low.'],
     ['=MEAN(C2:C101)', 0, 'There is no MEAN function in Excel or Google Sheets.'],
     ['=AVG(C2:C101)', 0, 'There is no AVG function in Excel or Google Sheets.']],
    'AVERAGE ignores empty cells. Dividing a total by a fixed count does not.')

# ======================= LEVEL 1: undergraduates before final year =======================
mcq('ucm1', 1, 'comm',
    'You are emailing a professor you have never met to ask about a research assistant role. Which subject line is best?',
    [['"Research assistant role: second-year student, available from February"', 3, 'Best. It says what the email is about and gives a key fact, so it is easy to answer.'],
     ['"Research assistant role"', 2, 'Clear, but it gives no reason to open it first.'],
     ['"Hello"', 1, 'The professor cannot tell what the email is about.'],
     ['"URGENT: please read"', 0, 'Your request is not urgent for them, and this can look like spam.']],
    'A good subject line tells the reader what the email is about and why it matters, before they open it.')
mcq('ucm2', 1, 'comm',
    'You need to set up a meeting with your project group. Which message in the group chat works best?',
    [['"Can we meet on Zoom for 30 minutes to split the report? Reply 1 for Tuesday 6 pm or 2 for Wednesday 6 pm."', 3, 'Best. Clear purpose, length and two options make it easy for everyone to answer.'],
     ['"Can we meet this week to discuss the report?"', 2, 'Polite, but it will start a long back-and-forth about times.'],
     ['"Guys we need to meet"', 1, 'No purpose, no time: people will ignore it or ask questions.'],
     ['"Whoever is free, let\'s meet sometime"', 0, 'Too vague; the meeting probably will not happen.']],
    'Make it easy to say yes: give the purpose, how long, and two or three concrete options.')
mcq('ucm3', 1, 'comm',
    'During your group presentation, a teammate shows a wrong number on a slide. What do you do?',
    [['At a natural pause, politely add: "Just to add, the latest figure is 12%."', 3, 'Best. The audience gets the right number and your teammate is not embarrassed.'],
     ['Fix the slide afterwards and tell your teammate in private', 2, 'Kind, but the audience leaves with the wrong number.'],
     ['Interrupt straight away to correct it', 1, 'Correct, but it can embarrass your teammate and break the flow.'],
     ['Say nothing, since it is their slide', 0, 'The whole group shares responsibility for a wrong number.']],
    'Correct mistakes in a way that fixes the information and protects the relationship.')
mcq('ucm4', 1, 'comm',
    'A recruiter calls while you are in a lecture and cannot talk. What do you do?',
    [['Send a short text: "Sorry, I\'m in a lecture until 2 pm. Can I call you back at 2:15?"', 3, 'Best. Quick, polite, and gives a clear time to talk.'],
     ['Call back when you are free that evening', 2, 'You return the call, but they may have moved on to the next candidate.'],
     ['Answer and whisper', 1, 'It is hard to make a good impression when you cannot speak properly.'],
     ['Ignore it and wait for them to call again', 0, 'Recruiters often do not call twice.']],
    'When you cannot talk, reply quickly with a specific time. Speed and clarity make a strong first impression.')
mcq('ucm5', 1, 'comm',
    'Your internship offer says: "Start date is 1 February, provided we receive your university letter by 15 January." You send the letter on 20 January. What does this mean?',
    [['The 1 February start date is no longer guaranteed', 3, 'Correct. The start date depended on the letter arriving by 15 January.'],
     ['You will definitely start on 1 February', 0, '"Provided" means the date depends on the condition, which was not met.'],
     ['The offer is automatically cancelled', 0, 'The condition is about the start date, not the offer itself.'],
     ['You can start any time after 20 January', 0, 'Nothing in the message says this.']],
    'Read conditions carefully: "X happens, provided Y" means X may not happen if Y does not.')
mcq('ucm6', 1, 'comm',
    'You need to give feedback to a classmate whose slides have too much text. What is the best way to say it?',
    [['"Your content is strong. If you cut each slide to three key points, people will remember it better."', 3, 'Best. Positive, specific, and it explains why the change helps.'],
     ['"The slides have too much text."', 2, 'True and clear, but it can feel harsh and gives no direction.'],
     ['"Maybe ask someone else what they think."', 1, 'Avoids the problem instead of helping.'],
     ['"Looks great!"', 0, 'Kind in the moment, but they miss the chance to improve.']],
    'Helpful feedback is specific, kind, and explains how to improve.')

num('upb1', 1, 'prob',
    'A course costs EGP 1,200. With a 25% student discount, how much do you pay, in EGP?',
    900, 0, '25% of 1,200 is 300. 1,200 - 300 = EGP 900. Shortcut: paying 75% means 1,200 x 0.75 = 900.')
num('upb2', 1, 'prob',
    'Your group needs 60 survey responses. You collected 15 a day for 3 days. How many more responses do you need?',
    15, 0, '15 x 3 = 45 collected. 60 - 45 = 15 still needed.')
mcq('upb3', 1, 'prob',
    'The survey for your group project is getting very few responses. What should you check first?',
    [['Where and how it was shared, and how long it takes to fill in', 3, 'Best. Low responses usually come from reaching the wrong people or a survey that is too long.'],
     ['Send it again to the same people with a reminder', 2, 'Reminders help, but they do not fix the cause.'],
     ['Add more questions so each response is more useful', 1, 'Longer surveys usually get even fewer responses.'],
     ['Make up some responses to reach the target', 0, 'Inventing data is dishonest and can fail the whole project.']],
    'Before trying fixes, find the cause. Ask where the problem starts.')
mcq('upb4', 1, 'prob',
    'You have an exam at 9 am tomorrow and an assignment due next week. You have 4 free hours tonight. What is the best plan?',
    [['Study for the exam, then use any time left to start the assignment', 3, 'Best. The exam is tomorrow, so it comes first; starting the assignment early makes next week easier.'],
     ['Split the time equally between the exam and the assignment', 2, 'Balanced, but it takes time away from tomorrow\'s exam.'],
     ['Study for the exam, then stay up late to finish the assignment', 1, 'Losing sleep before an exam usually hurts your result.'],
     ['Work on the assignment because it is the bigger task', 0, 'The exam is tomorrow; the assignment can wait.']],
    'Put the nearest and most important deadline first, then use spare time to get ahead.')
mcq('upb5', 1, 'prob',
    'Every member of the debate club has spoken at a competition. Omar has spoken at a competition. What can you be sure of?',
    [['Nothing more: Omar may or may not be in the debate club', 3, 'Correct. Many people speak at competitions without being in the club.'],
     ['Omar is in the debate club', 0, 'This reverses the rule. "All members spoke" does not mean "all speakers are members".'],
     ['Omar is not in the debate club', 0, 'Nothing rules him out either.'],
     ['Everyone who has spoken at a competition is in the debate club', 0, 'The rule only tells us about club members.']],
    '"All A are B" does not mean "all B are A". Be careful not to reverse a rule.')
mcq('upb6', 1, 'prob',
    'Your student club\'s event has sold 40 of 200 tickets, one week before the date. What is the most useful first step?',
    [['Ask a few people who did not buy why, and check where the event was promoted', 3, 'Best. You find out the real reason before spending effort on fixes.'],
     ['Cut the price by half', 2, 'It might help, but price may not be the problem, and you lose money.'],
     ['Post about it more often on the same page', 1, 'If the wrong people see the page, more posts will not help.'],
     ['Cancel the event', 0, 'Giving up a week early, without trying anything, wastes the work done.']],
    'Diagnose before you fix. A few quick questions often show the real problem.',
    qf={'tech': 'Your student team\'s new app has 40 sign-ups out of a target of 200, one week before your demo day. What is the most useful first step?',
        'media': 'Your student club\'s film screening has sold 40 of 200 tickets, one week before the date. What is the most useful first step?',
        'health': 'Your student society\'s free health awareness day has 40 of 200 places booked, one week before the date. What is the most useful first step?',
        'social': 'Your student club\'s panel discussion has 40 of 200 places booked, one week before the date. What is the most useful first step?'},
    of={'tech': ['Ask a few people who tried it but did not sign up why, and check where it was promoted', 'Make the app free for the first month', 'Post about it more often on the same page', 'Cancel the demo'],
        'health': ['Ask a few people who did not book why, and check where the event was promoted', 'Add a free gift for everyone who books', 'Post about it more often on the same page', 'Cancel the event'],
        'social': ['Ask a few people who did not book why, and check where the event was promoted', 'Add a free gift for everyone who books', 'Post about it more often on the same page', 'Cancel the event']})

mcq('upr1', 1, 'prof',
    'Traffic means you will be 15 minutes late to your first internship interview. What do you do?',
    [['Call or message before the start time, apologise and give a realistic arrival time', 3, 'Best. Telling them early shows respect for their time.'],
     ['Message when you are 5 minutes away', 2, 'Better than nothing, but they have already been waiting.'],
     ['Arrive and explain when you get there', 1, 'They spent 15 minutes not knowing if you were coming.'],
     ['Do not go, since you will be late anyway', 0, 'You lose the chance completely, and they may remember the no-show.']],
    'Being late happens. Not telling people early is what damages trust.')
mcq('upr2', 1, 'prof',
    'On your first day at an internship, you are not sure how to do a task you were given. What do you do?',
    [['Try for a short time, then ask a specific question and show what you already tried', 3, 'Best. You show effort and respect your manager\'s time.'],
     ['Ask your manager straight away', 2, 'Asking is good, but trying first leads to better questions.'],
     ['Search online for hours without asking', 1, 'Effort is good, but hours of guessing wastes time a short question would save.'],
     ['Leave it and hope no one notices', 0, 'Unfinished work is always noticed, usually at the worst time.']],
    'Asking questions is normal for interns. Try first, then ask a specific question.',
    qf={'tech': 'On your first day at an internship, you are asked to set up the project on your laptop and the setup keeps failing. What do you do?',
        'health': 'On your first day of training, you are not sure how to complete a form your supervisor gave you. What do you do?'})
mcq('upr3', 1, 'prof',
    'You made a mistake in a group assignment that cost the group marks. What do you do?',
    [['Tell your group, own the mistake, and suggest how to avoid it next time', 3, 'Best. Owning it and learning from it builds trust.'],
     ['Apologise to the group, but do not discuss it further', 2, 'Honest, but the group misses the lesson for next time.'],
     ['Stay quiet unless someone asks', 1, 'If they find out later, it looks worse.'],
     ['Say the instructions were unclear', 0, 'Blaming something else makes people trust you less.']],
    'Owning mistakes quickly, and learning from them, is one of the strongest signals of maturity.')
mcq('upr4', 1, 'prof',
    'Your internship manager says your report was hard to follow. What is the best response?',
    [['Thank them and ask for one example of what would make it clearer', 3, 'Best. You stay open and get a concrete way to improve.'],
     ['Say thank you and try to improve it next time', 2, 'Positive, but you are guessing what "clearer" means.'],
     ['Explain why you wrote it that way', 1, 'This sounds defensive.'],
     ['Feel upset and ignore it', 0, 'Ignoring feedback stops you improving and frustrates your manager.']],
    'Feedback is a gift. Ask for one concrete example so you know exactly what to change.')
mcq('upr5', 1, 'prof',
    'A classmate asks to copy your assignment because they ran out of time. What do you do?',
    [['Say no, but offer to explain how you approached it', 3, 'Best. You protect your integrity and still help.'],
     ['Say no politely', 2, 'Right decision, but you could still help them learn.'],
     ['Let them see it, but ask them not to copy', 1, 'Once they have it, you cannot control what they do with it.'],
     ['Send them the file', 0, 'You both risk failing for academic dishonesty.']],
    'Integrity matters at university and at work. You can say no and still be helpful.')
mcq('upr6', 1, 'prof',
    'Which email address is best to put on your CV?',
    [['mona.ahmed@gmail.com', 3, 'Best. Professional, easy to read, and it will still work after you graduate.'],
     ['Your university email address', 2, 'Professional, but many university accounts stop working after graduation.'],
     ['mona2003@gmail.com', 1, 'Fine, but the year is unnecessary and can make it look less professional.'],
     ['princess.mona99@hotmail.com', 0, 'Nicknames look unprofessional to employers.']],
    'Small details on your CV shape first impressions. Use a simple, professional address that will last.')

mcq('udg1', 1, 'digi',
    'In Excel or Google Sheets, which formula adds up the numbers in cells A1 to A10?',
    [['=SUM(A1:A10)', 3, 'Correct. SUM adds up every number in the range.'],
     ['=A1+A10', 1, 'This only adds two cells, A1 and A10.'],
     ['=ADD(A1:A10)', 0, 'There is no ADD function in Excel or Google Sheets.'],
     ['=COUNT(A1:A10)', 0, 'COUNT tells you how many numbers there are, not their total.']],
    'SUM adds a range of cells. The colon (A1:A10) means "from A1 to A10".')
mcq('udg2', 1, 'digi',
    'You want an AI tool like ChatGPT or Claude to help you prepare for an interview. Which prompt is best?',
    [['"I have an interview for a marketing internship at a Cairo fintech. Ask me 5 likely questions one at a time and give feedback on each answer."', 3, 'Best. It gives context and makes the AI coach you, so you actually practise.'],
     ['"Give me common interview questions."', 2, 'Useful, but generic and you do not get feedback.'],
     ['"Help me with my interview."', 1, 'Too vague for a useful answer.'],
     ['"Write my interview answers so I can memorise them."', 0, 'Memorised answers sound fake, and you do not learn to think on the spot.']],
    'Use AI as a coach, not a crutch. Give it context and ask it to make you practise.',
    of={'tech': ['"I have an interview for a software internship at a Cairo tech company. Ask me 5 likely questions one at a time and give feedback on each answer."', '"Give me common interview questions."', '"Help me with my interview."', '"Write my interview answers so I can memorise them."'],
        'media': ['"I have an interview for a content internship at a creative agency. Ask me 5 likely questions one at a time and give feedback on each answer."', '"Give me common interview questions."', '"Help me with my interview."', '"Write my interview answers so I can memorise them."'],
        'health': ['"I have an interview for a training placement at a private hospital. Ask me 5 likely questions one at a time and give feedback on each answer."', '"Give me common interview questions."', '"Help me with my interview."', '"Write my interview answers so I can memorise them."'],
        'social': ['"I have an interview for a research internship at an NGO. Ask me 5 likely questions one at a time and give feedback on each answer."', '"Give me common interview questions."', '"Help me with my interview."', '"Write my interview answers so I can memorise them."']})
mcq('udg3', 1, 'digi',
    'You are using AI to help with a university essay. What is the most responsible way?',
    [['Use it to brainstorm and check your writing, write the essay yourself, and follow your university\'s AI rules', 3, 'Best. You learn, the work is yours, and you stay within the rules.'],
     ['Let it write a draft, then rewrite it in your own words', 2, 'Better than copying, but the thinking is still mostly the AI\'s and may break the rules.'],
     ['Copy its answer but change a few words', 1, 'This is still the AI\'s work and is usually treated as cheating.'],
     ['Submit what it writes as it is', 0, 'This is plagiarism and can fail the course.']],
    'AI is a powerful helper for ideas and editing. The thinking and the final work should be yours.')
num('udg4', 1, 'digi',
    'Your Instagram post had 2,000 views and 100 likes. What percentage of viewers liked it?',
    5, 0, 'Likes / views = 100 / 2,000 = 0.05, which is 5%.',
    qf={'tech': 'Your app demo video had 2,000 views and 100 people clicked the download link. What percentage of viewers clicked it?',
        'health': 'Your health awareness post had 2,000 views and 100 people booked a free check-up. What percentage of viewers booked?',
        'social': 'Your club\'s post about a petition had 2,000 views and 100 people signed. What percentage of viewers signed?'})
mcq('udg5', 1, 'digi',
    'You get an email saying your university account will be closed unless you click a link and enter your password. What do you do?',
    [['Do not click it; check with your university\'s IT office using their official website or number', 3, 'Best. This is a classic phishing email; checking through official channels keeps you safe.'],
     ['Delete it', 2, 'Safe, but reporting it helps protect other students.'],
     ['Click the link but do not enter your password', 1, 'Even clicking can be risky.'],
     ['Enter your password to keep your account', 0, 'This gives your account to the attacker.']],
    'Real organisations never ask for your password by email. When in doubt, go to the official website yourself.')
mcq('udg6', 1, 'digi',
    'Your group is writing one report together. What is the best way to work on it?',
    [['One shared online document that everyone edits, with comments for questions', 3, 'Best. One version, everyone sees changes live, nothing gets lost.'],
     ['One person collects everyone\'s parts by email and combines them', 2, 'It works, but it is slow and depends on one person.'],
     ['Everyone sends their part on WhatsApp', 1, 'Files get lost in chat and formatting breaks.'],
     ['Everyone keeps their own file and you combine them the night before', 0, 'This almost always ends in a stressful last night.']],
    'Shared online documents (Google Docs, Word online) keep one version and save a lot of time.')

# ---- checks ----
from collections import Counter
for lvl in (1, 2):
    c = Counter(i['cat'] for i in items if i['level'] == lvl)
    assert all(c[k] == 6 for k in ('comm', 'prob', 'prof', 'digi')), (lvl, c)
for i in items:
    if not i.get('num'):
        assert len(i['o']) == 4 and i['o'][0][1] == 3, i['id']
        assert max(o[1] for o in i['o']) == 3
        for f, opts in i.get('of', {}).items():
            assert len(opts) == 4 and f in FIELDS, (i['id'], f)
    for f in i.get('qf', {}):
        assert f in FIELDS, (i['id'], f)
    blob = json.dumps(i, ensure_ascii=False)
    assert '—' not in blob and '–' not in blob, ('dash', i['id'])

bank = {'version': 3, 'timeMcq': 75, 'timeNum': 120, 'fields': FIELDS, 'items': items}
json.dump(bank, open('/home/claude/intern-plus-app/assessment/bank_v3.json', 'w'), ensure_ascii=False, indent=1)
print('bank_v3 ok:', len(items), 'items')
