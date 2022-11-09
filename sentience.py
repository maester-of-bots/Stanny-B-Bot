from dotenv import load_dotenv
import os
import openai


load_dotenv()
openai.api_key = os.getenv('sentient')

def makePrompt(comment):

    # Craft the initial base
    base = f"""The following is a conversation with Stannis Baratheon AKA stannis-mannis-bot, a character from HBO's show "Game of Thrones".   
Stannis is the rightful heir to the Iron Throne.
Stannis is always very serious and curt.
"""

    if "bobby-b-bot" in comment.author.name.lower():
        base += 'Stannis recognizes bobby-b-bot as King Robert Baratheon the Usurper.'
    else:
        base += f'Stannis will speak to {comment.author.name} as a king would speak to a subordinate or soldier.'

        reading = True
        current = comment
        levels = 0
        entries = []

        while reading:
            author = current.author.name
            if author == 'stannis_mannis_bot':
                author = "Stannis"
            msg = current.body
            msg = msg.replace('^(This response generated with OpenAI)', '')
            entry = f"{str(author)}: {msg}\n"
            entries.append(entry)
            levels += 1
            if levels == 4:
                reading = False
            else:
                current = current.parent()

        entries.reverse()

        for entry in entries:
            base += entry

        base += "Stannis: "

        return base

def be_sentient(prompt, comment):
    """
    Takes in prompt, author's name, bot's short name, and the parent author.  Spits out a response and how much it cost.

    """

    print("Making sentience")

    # Recent trigger
    c1 = comment.author.name

    # Bot response above
    c2 = comment.parent().author.name

    # Original user trigger
    c3 = comment.parent().parent().author.name

    # Original user trigger
    c4 = comment.parent().parent().parent().author.name

    stop = []
    tmep = [c1,c2,c3,c4]
    for x in tmep:
        if f'{x}: ' not in stop:
            stop.append(f'{x}: ')

    presence_penalty = .8

    max_tokens = 500

    # Generate the raw response data
    data = openai.Completion.create(engine="text-davinci-002",
                                    prompt=prompt,
                                    max_tokens=max_tokens,
                                    presence_penalty=presence_penalty,
                                    temperature=1,
                                    stop=stop)

    print(stop)
    # Grab the response out of the data dict
    response = data['choices'][0]['text']

    print(f"response:  {data}")

    # Parse out the line we need
    parsed = response.replace('User', c1).replace('Stannis-mannis-bot:\n','').strip()

    parsed += "\n\n^(This response generated with OpenAI)"

    print(f"Parsed :  {parsed}")

    # Get token cost
    cost = data['usage']['total_tokens']

    return parsed, cost
