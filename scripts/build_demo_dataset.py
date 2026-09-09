from pathlib import Path
import random

import pandas as pd


SAFE_SUBJECTS = [
    "Meeting notes for {topic}",
    "Your booking confirmation {number}",
    "Weekly update from the {team} team",
    "Receipt for order {number}",
    "Reminder: {topic} tomorrow",
    "Draft agenda for our next meeting",
    "Library item due next week",
    "Project files are ready to review",
    "Monthly account summary",
    "Welcome to the {topic} course",
]

SAFE_BODIES = [
    "Hi {name}, the notes from our {topic} meeting are attached. Please add any corrections before Friday.",
    "Thanks for your order. Your reference is {number}. You can view the receipt in the account you already use.",
    "This is a reminder that our session starts at {time}. Reply if you need to rearrange it.",
    "The {team} team has completed this week's update. The document is in the shared project folder.",
    "Your library loan has been renewed until next week. No action is needed today.",
    "Here is the agenda we discussed: progress, open questions and plans for the next sprint.",
    "Your monthly summary is now available through the usual account portal. This message contains no payment request.",
    "Welcome to the {topic} course. The first class is at {time} in the room shown on your timetable.",
]

PHISH_SUBJECTS = [
    "Urgent: verify your account now",
    "Payment failed - immediate action required",
    "Mailbox will be suspended today",
    "Unusual sign-in detected",
    "You have won a reward",
    "Final warning for invoice {number}",
    "Password expires in one hour",
    "Confidential document shared with you",
    "Security alert: confirm your details",
    "Refund waiting for approval",
]

PHISH_BODIES = [
    "Dear user, your account will be locked today. Click the link and confirm your password immediately.",
    "We could not process invoice {number}. Open the secure form now and enter your card details to avoid a fee.",
    "Your mailbox has exceeded its limit. Sign in through this link within one hour to keep access.",
    "A login from a new device was detected. Verify your identity and security answer now.",
    "Congratulations, you were selected for a reward. Claim it today by providing your delivery and payment details.",
    "The attached document is confidential. Enable editing and sign in when prompted to read it.",
    "A refund of GBP {number} is waiting. Confirm your bank details before the request expires.",
    "This is the final security notice. Failure to verify immediately will permanently suspend your account.",
]


def make_rows(per_class: int = 120, seed: int = 42) -> list[dict[str, object]]:
    randomiser = random.Random(seed)
    names = ["Alex", "Jordan", "Morgan", "Sam", "Taylor", "Casey"]
    topics = ["research", "security", "data", "software", "seminar", "project"]
    teams = ["support", "library", "research", "teaching", "project"]
    times = ["09:00", "10:30", "13:00", "15:30"]

    rows: list[dict[str, object]] = []
    for label, subjects, bodies, prefix in (
        (0, SAFE_SUBJECTS, SAFE_BODIES, "legit"),
        (1, PHISH_SUBJECTS, PHISH_BODIES, "phish"),
    ):
        for index in range(per_class):
            values = {
                "name": randomiser.choice(names),
                "topic": randomiser.choice(topics),
                "team": randomiser.choice(teams),
                "time": randomiser.choice(times),
                "number": randomiser.randint(1000, 9999),
            }
            rows.append(
                {
                    "message_id": f"{prefix}-{index + 1:03d}",
                    "subject": randomiser.choice(subjects).format(**values),
                    "body": randomiser.choice(bodies).format(**values),
                    "label": label,
                }
            )

    randomiser.shuffle(rows)
    return rows


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "messages.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(make_rows()).to_csv(output_path, index=False)
    print(f"Wrote 240 synthetic messages to {output_path}")

