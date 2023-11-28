import email.message
import random
from pathlib import Path

PEOPLE = """
John Doe <john@example.com>
Jane Doe <jane@example.com>
Robert Smith <robert@example.com>
Sarah Johnson <sarah@example.com>
Michael Williams <michael@example.com>
Emma Brown <emma@example.com>
Emily Davis <emily@example.com>
Daniel Miller <daniel@example.com>
David Wilson <david@example.com>
Sophia Moore <sophia@example.com>
Olivia Taylor <olivia@example.com>
Evelyn Thomas <evelyn@example.com>
""".strip().splitlines()

TEMPLATE = """
Hei {name}!

Salapukkilahjanvaihtokumppanisi on {target}.

Terveisin,

Salapukkilahjatoimikunta
""".strip()


def split_name_email(person):
    name, _, email = person.partition("<")
    return name.strip(), email.strip("<>").strip()


def make_mapping(people):
    people = list(people)
    random.shuffle(people)
    rolled_people = people[1:] + people[:1]
    return dict(zip(people, rolled_people))


def main():
    mapping = make_mapping(PEOPLE)
    dest_dir = Path("santa_mails")
    dest_dir.mkdir(exist_ok=True)
    for i, (full_santa, full_giftee) in enumerate(sorted(mapping.items())):
        name, _ = split_name_email(full_santa)
        target, _ = split_name_email(full_giftee)
        email_content = TEMPLATE.format(name=name, target=target)
        eml = email.message.EmailMessage()
        eml["Subject"] = "Salapukkilahja"
        eml["To"] = full_santa
        eml.set_content(email_content)
        dest_name = dest_dir / f"secret_santa_{i:04d}.eml"
        dest_name.write_bytes(eml.as_bytes())
        print("=>", dest_name)


if __name__ == "__main__":
    main()
